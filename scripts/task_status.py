#!/usr/bin/env python3
"""Read a single local job record without a model, API, credentials or project scan."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import time

REMOTE_TERMINAL = {'COMPLETED', 'FAILED', 'CANCELLED', 'CANCELED'}
KNOWN = REMOTE_TERMINAL | {'QUEUED', 'PROCESSING', 'RUNNING', 'SUBMITTING', 'SUBMITTED', 'HTTP_REJECTED', 'PLANNED', 'READY', 'UNKNOWN', 'NOT_SENT', 'REJECTED_NO_TASK'}

def snapshot(path, task_id, stale_seconds=120, until_downloaded=False):
    result = {'task_uuid': task_id, 'source': 'local_record', 'remote_refreshed': False}
    try:
        # Atomic writers may replace this file; fstat refers to the actual read version.
        with path.open('rb') as stream:
            import os
            stat = os.fstat(stream.fileno())
            if stat.st_size > 4 * 1024 * 1024:
                return dict(result, record_status='too_large', actionable=True)
            data = json.load(stream)
        if not isinstance(data, dict):
            raise ValueError('Invalid record')
    except FileNotFoundError:
        return dict(result, record_status='missing', actionable=True)
    except (OSError, ValueError, UnicodeError):
        return dict(result, record_status='unreadable', actionable=True)
    if data.get('task_uuid') != task_id:
        return dict(result, record_status='task_id_mismatch', actionable=True)
    status = data.get('status')
    status = status.upper() if isinstance(status, str) else 'UNKNOWN'
    if status not in KNOWN:
        status = 'UNKNOWN'
    terminal = status in REMOTE_TERMINAL
    age = max(0, time.time() - stat.st_mtime)
    downloaded=bool(data.get('local_model'))
    phase=data.get('execution_phase')
    waiting_download=until_downloaded and status=='COMPLETED' and not downloaded
    stale = age > stale_seconds and (not terminal or waiting_download)
    result.update(record_status='ok', status=status, terminal=terminal,
                  record_written_at=datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(),
                  stale=stale, actionable=stale or status in {'FAILED', 'CANCELLED', 'CANCELED', 'HTTP_REJECTED', 'UNKNOWN', 'NOT_SENT', 'REJECTED_NO_TASK'} or phase in {'paused','needs_attention'},
                  download_recorded=downloaded, execution_phase=phase, validation='not_assessed')
    # Do not forward response, prompts, images, signed URLs, errors or credentials.
    return result

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--task-id', required=True)
    parser.add_argument('--state-file', required=True, type=Path)
    parser.add_argument('--until-downloaded', action='store_true', help='With --watch, wait past remote COMPLETED until local download is recorded; not quality validation')
    parser.add_argument('--watch', action='store_true', help='Watch local file in this process; emit only meaningful changes')
    parser.add_argument('--interval', type=float, default=15)
    parser.add_argument('--stale-seconds', type=float, default=120)
    parser.add_argument('--timeout', type=float, default=3600)
    args = parser.parse_args()
    if not args.task_id or len(args.task_id) > 128 or any(not (c.isalnum() or c in '-_') for c in args.task_id):
        parser.error('task-id must be a short alphanumeric ID (hyphen/underscore allowed)')
    if args.interval < 1 or args.stale_seconds < 1 or args.timeout < 1:
        parser.error('timing values must be at least 1 second')
    deadline = time.monotonic() + args.timeout
    previous = None
    while True:
        current = snapshot(args.state_file, args.task_id, args.stale_seconds, args.until_downloaded)
        signature = {k: v for k, v in current.items() if k != 'record_written_at'}
        if signature != previous:
            print(json.dumps(current, ensure_ascii=False, separators=(',', ':')), flush=True)
            previous = signature
        finished=current.get('terminal') and (not args.until_downloaded or current.get('status')!='COMPLETED' or current.get('download_recorded'))
        if not args.watch or finished or current.get('actionable'):
            return 1 if current.get('actionable') else 0
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            print(json.dumps({'task_uuid': args.task_id, 'watch_status': 'timeout', 'remote_status': 'unknown'}), flush=True)
            return 2
        time.sleep(min(args.interval, remaining))

if __name__ == '__main__':
    raise SystemExit(main())
