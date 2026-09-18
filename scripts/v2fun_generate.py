"""Resume-safe V2Fun generation. Config uses JSON syntax, a valid YAML subset."""
import argparse, base64, concurrent.futures, hashlib, json, os, socket, struct, time
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from task_budget import Budget
from v2fun_client import Client, load_config

ROOT = Path(__file__).resolve().parent
def save(path, value):
    tmp = path.with_suffix('.tmp')
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2))
    tmp.replace(path)

AI_ROUTES = {'v2fun_ai3d', 'user_ai3d'}
LOCAL_ROUTES = {'assistant_geometry', 'reuse'}

def select_ai_parts(manifest):
    parts = manifest['parts']
    if not isinstance(parts, list):
        raise ValueError('parts must be a list')
    ids = set()
    for part in parts:
        pid = part.get('id')
        if not isinstance(pid, str) or not pid or pid in ids or Path(pid).name != pid or pid in {'.', '..'}:
            raise ValueError('Invalid or duplicate part ID')
        ids.add(pid)
        if part.get('route') not in AI_ROUTES | LOCAL_ROUTES:
            raise ValueError('Every part needs an explicit supported route before API use')
    return [part for part in parts if part['route'] in AI_ROUTES]

def main():
    global ROOT
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument('--config', type=Path, default=None)
    parser.add_argument('--generate', action='store_true')
    parser.add_argument('--part', nargs='+', help='Explicit AI part IDs for this batch')
    args = parser.parse_args()
    ROOT=args.project.resolve()
    manifest = json.loads((ROOT/'parts-manifest.json').read_text())
    ai_parts = select_ai_parts(manifest)
    if not ai_parts:
        print(json.dumps({'ai_parts': 0, 'new_tasks': 0, 'status': 'no_ai_work'}), flush=True)
        return
    if args.generate and not args.part:
        parser.error('--generate requires --part; unready parts are never implicitly submitted')
    if args.part:
        known={p['id'] for p in ai_parts}
        if not set(args.part) <= known:
            parser.error('--part contains unknown or non-AI IDs')
        ai_parts=[p for p in ai_parts if p['id'] in args.part]
    output = ROOT/'source-models'
    jobs = ROOT/'api-jobs'
    todo = [p for p in ai_parts if not (output/(p['id']+'.glb')).exists()]
    new = [p for p in todo if not (jobs/(p['id']+'.json')).exists()]
    print(json.dumps({'ai_parts':len(ai_parts),'missing':len(todo),'new_tasks':len(new)}), flush=True)
    if not args.generate or not todo:
        return
    config=load_config(ROOT, args.config)
    client=Client(config, opener=urlopen)
    if any(config.get(k) is not True for k in ['with_texture','pbr_texture','hd_texture']):
        raise ValueError('Default textured workflow requires all three texture flags true')
    if type(config.get('concurrency',1)) is not int or not 1 <= config.get('concurrency',1) <= 2:
        raise ValueError('Concurrency must be 1 or 2; account-wide lower limits still apply')
    output = ROOT/'source-models'; output.mkdir(exist_ok=True)
    jobs = ROOT/'api-jobs'; jobs.mkdir(exist_ok=True)
    lock = jobs/'pipeline.lock'
    fd = os.open(lock, os.O_CREAT|os.O_EXCL|os.O_WRONLY, 0o600)
    os.close(fd)
    api=client.request
    try:
        def needs_submission(part):
            record=jobs/(part['id']+'.json')
            if not record.exists(): return True
            state=json.loads(record.read_text())
            return not state.get('task_uuid') and state.get('submission_outcome') in {'not_sent','rejected_no_task'} and bool(state.get('submission_evidence'))
        budget=Budget(ROOT) if any(needs_submission(p) for p in todo) else None
        print('Balance before',api('/balance'),flush=True)
        def generate(part):
            pid=part['id']; record=jobs/(pid+'.json')
            state=json.loads(record.read_text()) if record.exists() else {}
            if state.get('task_uuid'):
                task=api('/3d_models/meshes/'+state['task_uuid'])
            else:
                if state and not (state.get('submission_outcome') in {'not_sent','rejected_no_task'} and state.get('submission_evidence')):
                    return {'id':pid,'error':'Submission uncertain; inspect original task, never blindly resubmit'}
                if not (part.get('referenceApproved') is True or part.get('status') in {'reference_approved','reference_ready'}):
                    return {'id':pid,'error':'Selected reference has not been approved by the executing assistant'}
                image=ROOT/part['referenceFiles'][0]
                raw=image.read_bytes()
                history=state.get('submission_history',[])
                if state:
                    history.append({k:state.get(k) for k in ['status','submission_outcome','submission_evidence','http_status']})
                payload={k:config[k] for k in ['model','with_texture','pbr_texture','hd_texture']}
                payload.update(input_image='data:image/png;base64,'+base64.b64encode(raw).decode(),options={'block':False})
                state={'part_id':pid,'reference_sha256':hashlib.sha256(raw).hexdigest(),'endpoint':'/3d_models/meshes','status':'SUBMITTING','submission_outcome':'uncertain','submission_history':history,'started_at':time.time()}
                budget.reserve(record,'meshes')
                save(record,state)
                try:
                    task=api('/3d_models/meshes',payload)
                except URLError as exc:
                    # DNS resolution fails before an HTTP request can reach the server.
                    not_sent=isinstance(getattr(exc,'reason',None),socket.gaierror)
                    state.update(status='NOT_SENT' if not_sent else 'HTTP_REJECTED' if isinstance(exc,HTTPError) else 'SUBMITTING',submission_outcome='not_sent' if not_sent else 'uncertain')
                    if not_sent: state['submission_evidence']='DNS resolution failed before HTTP request transmission'
                    if isinstance(exc,HTTPError): state['http_status']=exc.code
                    save(record,state);budget.outcome(record,'not_created' if not_sent else 'uncertain')
                    return {'id':pid,'status':state['status'],'submission_outcome':state['submission_outcome']}
                state.update(task_uuid=task['task_uuid'],parameters={k:config[k] for k in ['model','with_texture','pbr_texture','hd_texture']})
                save(record,state);budget.outcome(record,'created',task['task_uuid'])
                print(pid,'created',task['task_uuid'],flush=True)
            started=time.monotonic(); last=None
            while True:
                state.update(status=task['status'],response=task,execution_phase='downloading' if task['status']=='COMPLETED' else 'failed' if task['status']=='FAILED' else 'remote_processing');save(record,state)
                if task['status']!=last: print(pid,task['status'],flush=True);last=task['status']
                if task['status'] in ['COMPLETED','FAILED']:break
                if time.monotonic()-started>3600:
                    state.update(execution_phase='paused',recovery='resume_same_task');save(record,state)
                    return {'id':pid,'status':'poll_timeout_resume_available'}
                time.sleep(max(15, float(config.get('poll_seconds', 15))))
                try:task=api('/3d_models/meshes/'+state['task_uuid'])
                except HTTPError as exc:
                    if exc.code in [429,500,502,503,504]:time.sleep(60);time.sleep(45);continue
                    raise
            if task['status']=='FAILED':return {'id':pid,'status':'FAILED'}
            metadata=task.get('metadata') or []
            if isinstance(metadata,dict):metadata=[metadata]
            links=[d for m in metadata for d in m.get('downloads',[])]
            results=task.get('result') or []
            if isinstance(results,str):results=[results]
            asset=next((a for a in results if a.lower().endswith('.glb')),None)
            link=next((d for d in links if d.get('asset_path')==asset),None)
            if not link:return {'id':pid,'error':'No GLB download descriptor'}
            # Never forward API credentials to the signed download host.
            for attempt in range(4):
                try:
                    data=client.download(link['download_url'])
                    break
                except OSError:
                    if attempt==3:raise
                    time.sleep(5)
            if len(data)<12 or data[:4]!=b'glTF' or struct.unpack_from('<I',data,8)[0]!=len(data):raise ValueError('Invalid GLB')
            target=output/(pid+'.glb');tmp=target.with_suffix('.download');tmp.write_bytes(data);tmp.replace(target)
            state.update(local_model=str(target.relative_to(ROOT)),sha256=hashlib.sha256(data).hexdigest(),execution_phase='downloaded',completed_at=time.time());save(record,state)
            print(pid,'downloaded',len(data),flush=True)
            return {'id':pid,'status':'downloaded','bytes':len(data)}
        results=[]
        with concurrent.futures.ThreadPoolExecutor(max_workers=config.get('concurrency',1)) as pool:
            futures={pool.submit(generate,p):p['id'] for p in todo}
            for future in concurrent.futures.as_completed(futures):
                try:results.append(future.result())
                except Exception as exc:
                    pid=futures[future];record=jobs/(pid+'.json')
                    if record.exists():
                        state=json.loads(record.read_text());state.update(execution_phase='needs_attention',error_type=type(exc).__name__);save(record,state)
                    results.append({'id':pid,'error_type':type(exc).__name__})
        save(jobs/'run-report.json',{'results':results,'balance_after':api('/balance')})
        for part in ai_parts:
            model=output/(part['id']+'.glb')
            if model.exists():part.update(sourceModel=str(model.relative_to(ROOT)),status='model_downloaded')
        save(ROOT/'parts-manifest.json',manifest)
        print('Generation batch finished',results,flush=True)
        if any(not (output/(p['id']+'.glb')).exists() for p in ai_parts):
            raise SystemExit(1)
    finally:lock.unlink(missing_ok=True)

if __name__=='__main__':main()
