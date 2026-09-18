# Independent status monitoring

Submit, poll, back off, and download within the local executor. The mesh executor already polls internally; do not add a second manual GET loop. Status-only queries read one file, not images, models, full manifests, or logs.

Expand the script path from the installed skill:

```sh
python3 /absolute/v2fun-ai-3d/scripts/task_status.py --task-id TASK_ID --state-file /absolute/project/api-jobs/PART_ID.json
```

By default, read once and return compact JSON. --watch monitors locally and reports meaningful changes. Defaults are a 15-second interval and 3600-second timeout. Normal queries stop at a remote terminal state or actionable issue. For full workflow waits, add --until-downloaded to wait after COMPLETED for local_model. Paused, stale, and error records require attention. A download record is not quality acceptance. This tool calls no model, network, or generation API.

Records require task_uuid and status; downloads use local_model. Execution phases are remote_processing/downloading/downloaded/failed/paused/needs_attention. Adapt external local_file fields to local_model before using download waits. Output contains only ID, state, timestamps, staleness, remote-terminal/download flags, and action markers, not responses, prompts, encodings, credentials, or signed URLs. Missing, corrupt, and mismatched records are reported explicitly.

Active records unchanged for over 120 seconds are stale; tune --stale-seconds if necessary. Stale does not prove remote failure or executor exit. Other executors must write compatible minimal fields atomically before claiming status support.

Direct terminal queries need no modeling context. Invoking a query in an existing long conversation reduces tool output but does not guarantee removal of host history. Create a new status task only when the user explicitly requests one; pass only ID, state path, and entry point without forking the modeling conversation.

Distinguish user-initiated queries from waiting during full modeling work. Prefer process-completion events after download, then read one summary and continue validation. Remote COMPLETED is not full workflow completion. Without event support, use low-frequency host waits while respecting communication requirements. Avoid repeated unchanged summaries or frequent assistant wakeups as polling. Explain recovery when automatic continuation is unavailable; do not create tasks or abandon ongoing work merely to reduce tokens. Measure performance claims rather than promising fixed savings.
