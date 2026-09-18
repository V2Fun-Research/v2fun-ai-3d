"""Persistent project-wide paid-task accounting; no network or implicit authorization."""
import argparse, json, threading
from pathlib import Path

MUTEX = threading.RLock()
COUNTED = {'reserved', 'created', 'uncertain'}

def save(path, data):
    tmp = path.with_suffix('.tmp')
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2))
    tmp.replace(path)

def validate_limits(total, stages):
    if type(total) is not int or total < 0:
        raise ValueError('Authorized total must be a nonnegative integer')
    if not isinstance(stages, dict) or any(type(v) is not int or v < 0 for v in stages.values()):
        raise ValueError('Stage limits must be nonnegative integers')

def stage_for(path, data):
    endpoint = data.get('endpoint', '')
    if '/images/' in endpoint or 'multiview' in path.parts or 'part-images' in path.parts:
        return 'images'
    if 'textures' in endpoint or 'texture' in path.stem:
        return 'textures'
    if 'retop' in endpoint or 'retop' in path.stem:
        return 'retopology'
    return 'meshes'

class Budget:
    def __init__(self, project):
        self.project = Path(project)
        self.path = self.project/'api-jobs/budget-ledger.json'
        if not self.path.exists():
            raise ValueError('Missing authorized budget ledger; configuration is not spending approval')
        self.data = json.loads(self.path.read_text())
        validate_limits(self.data['max_new_tasks'], self.data['stage_limits'])
        if not self.data.get('authorization'):
            raise ValueError('Missing authorization source')
        self.sync()

    def sync(self):
        for path in (self.project/'api-jobs').rglob('*.json'):
            if path == self.path:
                continue
            data = json.loads(path.read_text())
            if not isinstance(data, dict) or not (data.get('task_uuid') or data.get('status') in {'SUBMITTING','HTTP_REJECTED','NOT_SENT','REJECTED_NO_TASK'}):
                continue
            key = str(path.relative_to(self.project))
            entry = self.data['entries'].setdefault(key, {'stage':stage_for(path,data)})
            if data.get('task_uuid'):
                entry.update(state='created', task_uuid=data['task_uuid'])
            elif data.get('submission_outcome') in {'not_sent','rejected_no_task'} and data.get('submission_evidence'):
                entry['state'] = 'not_created'
            else:
                entry['state'] = 'uncertain'
        save(self.path, self.data)

    def counts(self):
        seen = set(); stages = {}
        for key, e in self.data['entries'].items():
            if e['state'] not in COUNTED:
                continue
            identity = e.get('task_uuid') or key
            if identity in seen:
                continue
            seen.add(identity)
            stages[e['stage']] = stages.get(e['stage'],0)+1
        return len(seen), stages

    def reserve(self, record, stage):
        with MUTEX:
            total, stages = self.counts()
            key = str(Path(record).relative_to(self.project))
            old = self.data['entries'].get(key)
            if old and old['state'] in COUNTED:
                raise ValueError('Existing reservation requires recovery; never resubmit uncertain task')
            if total >= self.data['max_new_tasks'] or stages.get(stage,0) >= self.data['stage_limits'].get(stage, self.data['max_new_tasks']):
                raise ValueError('Authorized project/stage task limit reached')
            self.data['entries'][key] = {'stage':stage,'state':'reserved'}
            save(self.path, self.data)

    def outcome(self, record, state, task_uuid=None):
        with MUTEX:
            e = self.data['entries'][str(Path(record).relative_to(self.project))]
            e['state'] = state
            if task_uuid:
                e['task_uuid'] = task_uuid
            save(self.path, self.data)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project', type=Path, required=True)
    p.add_argument('--set-authorized-limit', type=int, required=True)
    p.add_argument('--authorization', required=True, help='Exact existing user authorization or its reference; never invent')
    p.add_argument('--stage-limits', type=json.loads, default=None, help='JSON object; omitted preserves existing limits')
    args=p.parse_args(); jobs=args.project/'api-jobs'; jobs.mkdir(parents=True,exist_ok=True)
    lock=jobs/'pipeline.lock'
    with lock.open('x') as f:
        f.write('budget update')
    try:
        path=jobs/'budget-ledger.json'
        old=json.loads(path.read_text()) if path.exists() else {}
        stages=args.stage_limits if args.stage_limits is not None else old.get('stage_limits',{})
        validate_limits(args.set_authorized_limit,stages)
        if not args.authorization.strip():
            raise ValueError('Authorization source must be nonempty')
        history=old.get('authorization_history',[])
        if old:
            history.append({k:old[k] for k in ['max_new_tasks','stage_limits','authorization']})
        save(path,dict(max_new_tasks=args.set_authorized_limit,stage_limits=stages,authorization=args.authorization,authorization_history=history,entries=old.get('entries',{})))
        budget=Budget(args.project)
        print(json.dumps({'limit':args.set_authorized_limit,'counted':budget.counts()[0]}))
    finally:
        lock.unlink()

if __name__=='__main__': main()
