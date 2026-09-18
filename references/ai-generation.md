# V2Fun reference and model generation

Single-view preparation applies to all modeling routes. Mesh generation applies only to v2fun_ai3d (or legacy user_ai3d) parts. Follow authorization in [SKILL.md](../SKILL.md) and use [status monitoring](status-monitoring.md) for progress.

## Single-view to multiview

When the input has one view, submit exactly one V2Fun image-edit request using model=gpt-image-2 and size=1280x720. Use the original as the main reference and request one image containing front, side, and rear views from left to right. Prepare this before building. Skip when sufficient consistent views or qualified reusable models already exist.

Specify consistent pose, scale, proportions, colors, materials, and design; aligned baselines, complete nonoverlapping objects, a clean background, and no text. Preserve visible features and conservatively infer hidden structure. These views help shape understanding and assembly; they are not measured evidence of unseen surfaces.

Use one task ID and one image, not one call per view. Do not automatically submit corrections for this triptych; this rule takes precedence over the individual-part correction allowance below. Inspect consistency once. Prefer original visible evidence over conflicting generated views. Continue parts with reliable independent evidence. If a conflict affects essential shape or fit and cannot be resolved, pause only dependent work and request the missing information or authorization for another image. Do not silently skip preparation or mark the whole task complete. Resume queries/downloads under the original task ID.

Store images/prompts under references/multiview/ and records under api-jobs/multiview/. Do not feed the triptych directly to the existing single-object mesh script. Use clear individual-object references for AI parts; the API supports separate multiview fields as documented in [API notes](api-contract.md), but the bundled mesh executor accepts only a single input image. Implement multiview submission with the same budget/recovery protocol before using it.

## Individual part references

Each unique AI part needs a qualified single-object input. Reuse a suitable original or existing reference. Generate a new image only when missing, obscured, or mixed with unrelated parts. Show silhouette, thickness, openings, and interfaces against a clean background, without text or a collage. This single-object requirement does not apply to the triptych above.

State included/excluded scope, preserved features, view, and occlusion reconstruction. Image framing does not determine assembly scale. Crops may serve as evidence but do not make an obscured part complete. Inspect scope, identity, interfaces, and style before model submission. On first integration, complete one genuinely needed image before expanding concurrency. Allow at most one correction per necessary individual-part image when covered by the plan; record persistent defects instead of retrying indefinitely.

## API handling

Follow [runtime integration](setup-integration.md) and [API notes](api-contract.md). Keep prompts in references/, records in api-jobs/, and original models in source-models/.

## Direct textured models

Use color reference → multiview preparation when needed → direct textured model → Three.js assembly and final inspection. Do not insert untextured white models, a separate pre-texture checkpoint, routine reduction/retopology, or separate texturing. Reuse suitable textured assets and advance ready parts independently.

Set with_texture=true, pbr_texture=true, and hd_texture=true. Reject old false settings before submission. Verify actual textures and resolution during final inspection. Separate white-model, reduction, retopology, or texturing work is only for explicit user requests.

## Cross-batch budget

Use the bundled client, budget ledger, and executor; see [runtime contract](runtime-contract.md). All paid stages share api-jobs/budget-ledger.json and pipeline.lock. Record whole-task max_new_tasks, stage_limits, authorization source, and cumulative submissions.

Unknown submission outcomes consume reserved capacity. Release only with evidence no task was created. Created tasks count even if they later fail. Recovery, asset deletion, configuration edits, and separate batches do not reset the ledger. A configuration or ledger entry is not user authorization.

Before paid submission, derive a finite plan:
- V: necessary multiview tasks, 0 or 1.
- I: unique AI parts missing qualified individual references.
- M: unique models requiring generation; exclude reuse and instances.

A proposed ceiling is images = V + 2I, meshes = M, total N = V + 2I + M. This includes at most one correction per individual-part image, none for the triptych, and no paid mesh resubmissions. Reserved capacity is not a requirement to use it. Stricter user limits prevail. Do not split parts unnecessarily to increase the ceiling.

Derive counts from the strategy, then establish whether the current user's authorization covers the concrete plan. Ask only for missing authorization; do not require repeated approval of covered actions. Record the actual user instruction or approval as the source, never a personal authorization copied from another installation. Plan changes beyond the approved scope or ceiling need additional authorization.

After authorization, use actual integers in place of the placeholders:

```sh
python3 /absolute/v2fun-ai-3d/scripts/task_budget.py --project /absolute/project --set-authorized-limit N --authorization 'Current user instruction or approval and the concrete call plan' --stage-limits '{"images": IMAGE_LIMIT, "meshes": M}'
```

Updating retains history; omitting --stage-limits retains previous stage limits. All paid executors must use task_budget.Budget and the shared lock: reserve(record, stage) before POST, then record created, uncertain, or evidence-backed not_created. Image or custom-stage code must integrate this protocol before paid submission. The bundled mesh ledger does not automatically enforce limits on arbitrary external scripts. Account-wide concurrency needs separate coordination.

## Implemented executor scope

The implementation is bundled directly; no other skill is loaded:

```sh
python3 /absolute/v2fun-ai-3d/scripts/v2fun_generate.py --project /absolute/project --config /absolute/config.json --part PART_ID --generate
```

Without --generate this only inventories and needs no key. Configuration is JSON; see [runtime contract](runtime-contract.md). All three texture flags must be true. Unknown routes fail; local-only manifests return no_ai_work.

Generation requires explicit --part ID [ID ...]. New submissions accept referenceApproved=true or status=reference_approved/reference_ready, meaning the executing assistant has inspected the reference. Unselected/unready parts do not block ready batches. Existing task IDs resume without another reference approval.

The executor skips existing local GLBs. Verify input versions and asset quality independently; file existence is not validation. Preserve old assets before replacing truly invalidated parts. Do not modify the shared manifest or start another executor for the same project during a batch. Confirm no live executor before removing an abandoned lock.

The script implements mesh creation, in-process polling, download, and project budgeting. It does not implement generic image editing, separate texturing, retopology, or cross-project account scheduling. For requested additional stages, verify the endpoint and implement recovery plus the same ledger before submitting. Do not invent command options. Legacy config max_new_tasks is not authorization and must not reset per-batch capacity.

Fix recoverable pre-submission problems under existing authorization. Service outages do not justify silently skipping required reference preparation. Continue independent procedural work with sufficient references. If the user chooses external generation, provide references, prompts, filenames, and GLB return instructions and record awaiting_user_models. Remote completion does not imply download or acceptance.
