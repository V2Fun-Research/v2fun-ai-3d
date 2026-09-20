#!/usr/bin/env python3
"""V2Fun shared entry point. Read-only by default; mutations are explicit commands."""
import argparse
import json
import os
from pathlib import Path
import re
import runpy
import shutil
import subprocess
import sys

from v2fun_client import DEFAULTS, Client, api_key, config_path, load_config, selected_region

ROOT = Path(__file__).resolve().parent
COMMANDS = {'models': 'v2fun_generate.py', 'status': 'task_status.py',
            'budget': 'task_budget.py', 'inspect': 'inspect_glb.py'}


def init(project):
    project = Path(project).resolve()
    previous = config_path(project)
    if previous:
        return {'status': 'config_exists', 'config': str(previous)}
    target = project / '.v2fun/config.json'
    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        return {'status': 'config_exists', 'config': str(target)}
    with os.fdopen(fd, 'w') as stream:
        json.dump(DEFAULTS, stream, indent=2)
        stream.write('\n')
    return {'status': 'initialized', 'config': str(target), 'key_saved': False}


def doctor(project, explicit=None):
    report = json.loads((ROOT.parent / 'runtime.json').read_text())
    report.update(python=sys.version.split()[0], network_checked=False)
    config = load_config(project, explicit)
    path = config_path(project, explicit)
    report['config'] = str(path) if path else None
    try:
        api_key(config)
        report['key_present'] = True
    except ValueError:
        report['key_present'] = False
    report['api_ready'] = False
    report['region'] = selected_region(config)
    report['region_verified'] = False
    report['status'] = 'local_ready' if sys.version_info >= (3, 9) else 'needs_attention'
    node = shutil.which('node')
    report['node'] = None
    if node:
        result = subprocess.run([node, str(ROOT / 'node_runtime.cjs'), str(Path(project).resolve())],
                                capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            report['node'] = json.loads(result.stdout)
    return report


def install_deps(project, packages):
    """Install explicitly pinned optional deps, preserving existing incompatible projects."""
    project = Path(project).resolve()
    requested = {}
    for spec in packages:
        match = re.fullmatch(r'(three|playwright|sharp)@(\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?)', spec)
        if not match:
            raise ValueError('Use an explicit version: three@X.Y.Z, playwright@X.Y.Z or sharp@X.Y.Z')
        name, version = match.groups()
        if name in requested and requested[name] != version:
            raise ValueError('Conflicting requested package versions')
        requested[name] = version
    if not requested:
        raise ValueError('At least one --package is required')
    manifest = project / 'package.json'
    data = json.loads(manifest.read_text()) if manifest.exists() else {}
    pending, reused = [], []
    for name, version in requested.items():
        declared = data.get('dependencies', {}).get(name) or data.get('devDependencies', {}).get(name)
        installed = project / 'node_modules' / name / 'package.json'
        actual = json.loads(installed.read_text()).get('version') if installed.exists() else None
        if actual == version:
            reused.append(name)
            continue
        if declared is not None or actual is not None:
            raise ValueError('Existing dependency '+name+' requires explicit reconciliation; setup will not overwrite it')
        pending.append(name+'@'+version)
    if pending:
        npm = shutil.which('npm')
        if not npm:
            raise ValueError('npm is missing; install Node.js before optional dependencies')
        project.mkdir(parents=True, exist_ok=True)
        if not manifest.exists():
            manifest.write_text(json.dumps({'private': True}, indent=2)+'\n')
        subprocess.run([npm, 'install', '--save-exact', *pending], cwd=project, check=True)
    return {'status': 'ready', 'installed': pending, 'reused': reused, 'project': str(project)}


def main():
    if len(sys.argv)>1 and sys.argv[1] in COMMANDS:
        script = ROOT / COMMANDS[sys.argv[1]]
        sys.argv = [str(script), *sys.argv[2:]]
        runpy.run_path(str(script), run_name='__main__')
        return
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    for name in ['doctor', 'init', 'balance', 'region', 'deps']:
        p = sub.add_parser(name)
        p.add_argument('--project', type=Path, required=True)
        if name in ['doctor', 'balance', 'region']:
            p.add_argument('--config', type=Path)
        if name in ['balance', 'region']:
            p.add_argument('--region', choices=['auto', 'cn', 'global'])
        if name == 'deps':
            p.add_argument('--package', action='append', required=True)
    for name in COMMANDS:
        sub.add_parser(name, help='Forward unchanged arguments to '+COMMANDS[name])
    args = parser.parse_args()
    if args.command == 'doctor':
        result = doctor(args.project, args.config)
    elif args.command == 'init':
        result = init(args.project)
    elif args.command == 'deps':
        result = install_deps(args.project, args.package)
    else:
        client = Client(load_config(args.project, args.config, args.region))
        result = {'region': client.region, 'base_url': client.base, 'region_verified': True, 'balance': client.balance}
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, subprocess.SubprocessError) as exc:
        # Do not echo transport exceptions, response bodies or signed URLs.
        message = str(exc) if isinstance(exc, ValueError) else 'Operation failed; inspect local configuration and connectivity'
        print(json.dumps({'status': 'needs_attention', 'error_type': type(exc).__name__, 'error': message}), file=sys.stderr)
        raise SystemExit(1)
