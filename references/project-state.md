# Project state and recovery

Reuse existing artifacts and create only what the current stage needs. Suggested layout:

- original/: original references.
- references/: generated references and prompts.
- api-jobs/: remote task records and budget.
- source-models/: original meshes.
- assembly/: Three.js project.
- exports/: final files.
- evidence/: necessary renders and inspection records.

Keep a delivery index in the state file; do not duplicate assets or create ZIP archives unless requested.

parts-manifest.json contains modelingMode and a parts array:

| Fields | Meaning |
| --- | --- |
| id, name, quantity | Stable ID, name, count |
| route, routeReason, geometryMethod | assistant_geometry / v2fun_ai3d / reuse, rationale, method |
| includes, excludes | Construction or generation scope |
| parentId, attachment | Parent, contact region/axis, coordinates, measurement basis |
| referenceFiles | Relative reference paths; may be empty for procedural parts |
| sourceModel, buildSource | Actual mesh or JS/TS source path, or null until produced |
| status | Actual workflow stage, not remote completion as acceptance |

For repeated parts, record source ID and instance/mirror transforms. Add input/output hashes, scale, rotation, and measured anchors when available. Unknown values are null. Accept legacy user_ai3d; map other legacy routes before execution.

workflow-state.json summarizes stage, valid artifacts, pending work, issues, and next action. Each concurrent task records its own state, dependencies, input hash, task_uuid, timestamps, and paths. One coordinator atomically updates shared manifests.

On resume, verify files, versions, and task IDs. Invalidate only affected interfaces and checks. Changes to final GLB, references, or part structure require corresponding rechecks and delivery-index updates. Preserve old assets. Missing paths are not deliverables, and awaiting user-provided models is not full completion.

After submission, provide the task ID and absolute state-file path for independent queries. Before delivery, apply [completion checks](threejs-runtime.md#validation-and-export). Record inspected features, evidence, and unresolved issues. Keep detailed logs in files and conversational updates concise.

Delivery state includes final GLB path and SHA-256, source and parameter paths, reference provenance, actual validation results, and unresolved issues. Preserve legacy images/videos, but their absence does not block model delivery.
