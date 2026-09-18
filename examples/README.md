# Examples

These are reproducible local fixtures and modeling request examples. They are not generated customer assets. Run commands from the repository root.

## 1. Local-only part inventory

- Purpose: confirm that procedural parts never trigger mesh submission.
- Input: [parts-manifest.json](local-inventory/parts-manifest.json), one planned regular base.
- Command: `python3 scripts/v2fun.py models --project examples/local-inventory`.
- Expected result: JSON with status=no_ai_work, ai_parts=0, new_tasks=0.
- Authorization/cost: local read only; no key, upload, or paid call.
- Success: exit code 0 and the expected inventory.
- Limit: this command does not build geometry or prove visual quality.

## 2. Read a local task record

- Purpose: inspect recorded download state independently of modeling context.
- Input: [job.json](local-status/job.json), a synthetic terminal record.
- Command: `python3 scripts/v2fun.py status --task-id demo-task --state-file examples/local-status/job.json`.
- Expected result: status=COMPLETED, download_recorded=true, validation=not_assessed, remote_refreshed=false.
- Authorization/cost: local read only; no remote query or credits.
- Success: exit code 0 and matching task/state fields.
- Limit: no GLB is included. local_model demonstrates the record schema, not an existing artifact or accepted model.
- Failure variant: use --task-id wrong-task; expect exit code 1 and record_status=task_id_mismatch.

## 3. Procedural model from sufficient views

Request: “Use $v2fun-ai-3d to rebuild this bracket from the attached consistent front, side, and rear references. Deliver a static GLB and source. Use local geometry only.”

- Required input: actual reference images showing the same bracket; dimensions if exact interfaces matter.
- Branch: sufficient views → procedural construction → Three.js inspection → export/reload.
- Authorization/cost: local construction; no API call.
- Expected output: GLB, Three.js source/parameters, validation records.
- Success: reference features and openings preserved, clean reload, delivered source.
- Failure handling: request missing critical dimensions; do not invent exact fit.
- Verification: illustrative request only; no bracket references or generated result are included.

## 4. Hybrid model with one reference

Request: “Use $v2fun-ai-3d to model the attached animal figurine on a regular display base. Show the image/mesh call plan and credit limit before remote work.”

- Required input: an actual single-view image, intended scope, key for remote work, and current-user upload/spending authorization.
- Branch: one multiview reference task, AI animal, procedural base; instance repeated assets.
- Expected output: textured GLB assembly, Three.js source, task IDs and validation records.
- Success: recognizable animal, aligned base contact, textures preserved after reload.
- Failure handling: uncertain POST outcomes remain reserved; reconcile or resume the original ID. No automatic paid mesh retry.
- Authorization/cost: derive a finite plan from missing references and unique parts; approval is required only if not already granted.
- Verification: illustrative request only; no paid call or output quality claim.

For all examples, installing this skill is not permission to upload files or spend credits.
