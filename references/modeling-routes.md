# Routes and parts

## Explain the strategy first

Before the first image, model, or procedural build, explain the intended use, overall route, and important features to preserve. Include a short table of actual parts: scope, quantity, method, input reference, and reason. Name methods explicitly: V2Fun textured model, Three.js procedural geometry, or asset reuse. Group repetitions into one row with instance counts. State when a route has no parts; do not invent parts to use every route.

Then state the planned reference-image and 3D calls separately: model, count, allowed image corrections, finite task ceiling, execution order, final GLB validation, and source delivery. A procedural part that uses an AI reference image is not an AI-generated mesh. Apply [single-view preparation](ai-generation.md#single-view-to-multiview) before building. Characters normally keep head and body together.

This explanation is not an extra approval gate. Continue under existing user authorization; otherwise obtain the missing upload/spending authorization under SKILL.md. Do not expose keys, image encodings, or full request bodies. Give a cost estimate only when supported; otherwise say actual charges depend on the account. Verify the initial route after multiview preparation. Explain material changes before affected steps and update the manifest. On resume, describe only pending work. Status queries and skill edits do not require a fictional modeling plan.

## Choose the route

Ask whether explicit parameters and stable geometry operations can represent the shape reliably. Complexity is not a count of parts or texture details. Label unseen dimensions and structures as inferred. Default to a static visual assembly when no use is specified.

| Shape or asset | Route | Method |
| --- | --- | --- |
| Regular mechanisms, shells, brackets, pipes, gears, repeated parts | procedural | Extrusion, revolution, sweeps, booleans, arrays |
| Rotational surfaces or clear cross sections | procedural | Lathe, loft, variable-section sweep |
| People, animals, facial anatomy, complex folds and sculpted detail | ai3d | V2Fun generation per appropriate part |
| Regular base or mechanism with organic elements | hybrid | Assign routes per part |
| Suitable existing meshes or projects | reuse | Preserve useful assets |

Mechanical parts may contain sculpted freeform shapes; curved surfaces do not automatically require AI. Simplified geometric characters may be procedural when the user accepts that style. Realistic people and animals default to AI. Parametric geometry does not imply STEP or exact CAD solid delivery.

Record modelingMode as procedural, ai3d, or hybrid. Record route, routeReason, and geometryMethod per part. Routes are assistant_geometry, v2fun_ai3d, and reuse; legacy user_ai3d is accepted. Determine missing routes before API use; a missing GLB is not a reason to submit. Procedural parts need no individual AI part image, but single-view input still requires multiview preparation.

## Split parts and define interfaces

Work from silhouette to main components and necessary detail. Split at natural seams, independent rigid motion, or attachments. Material boundaries are not physical seams. Avoid fragmenting continuous organic surfaces. Build repeated parts once and instance them. Check mirrored winding, normals, and text.

Keep character head, neck, limbs, hands, feet, and close-fitting equipment continuous by default. Separate props when useful. Consider separate head/neck generation only when the head is too small in the full-body reference to retain required facial detail. Judge effective reference resolution and identity requirements rather than a fixed ratio; document the reason. Assign neck ownership explicitly and inspect the assembled seam. Armor does not automatically justify separating arms. Conservatively reconstruct occluded body areas. Keep animal bodies continuous.

Record stable ID, included/excluded scope, quantity, parent, contact region/axis, and relative scale. Use null for unknown coordinates. Define semantic interfaces before reference generation and measure anchors when meshes exist. Three.js can create precise holes, thin rods, and connectors; do not invent connector blocks to hide misalignment.

## Procedural construction

Separate parameters from scene objects. Provide named Group factories and reproducible JS/TS source; seed randomness. Build silhouette and proportions, openings and structure, detail, then materials and lighting.

- Use primitives for discrete rigid bodies, Shape/ExtrudeGeometry for profiles, and LatheGeometry for rotational surfaces.
- Use path sweeps for pipes and loft/custom BufferGeometry for varying sections. Model rigid frames as endpoint networks rather than a smooth substitute curve.
- Respect opening axes, shell thickness, and cavities. Instance repeated parts. Do not replace defining continuous surfaces with stacked boxes.
- Prefer materials for stripes and wear; use geometry for silhouette-changing bevels and relief. Simple materials need no AI texture.

Switch to AI only when the shape actually needs sculpted detail, not because a library is missing or a parameter is wrong. Continue with the [Three.js workflow](threejs-runtime.md).
