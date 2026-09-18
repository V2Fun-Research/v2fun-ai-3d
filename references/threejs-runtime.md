# Three.js construction, assembly, and validation

Perform local 3D work in JS/TS with Three.js and actual browser rendering. Node may perform compatible geometry processing. Do not delegate local work to Blender or DCC/CAD applications. Python helpers do not process geometry or render.

## Import and edit

Prefer GLTFLoader for GLB and configure required compression decoders. Other formats need working loaders and complete linked resources. Check part IDs, actual formats, nodes, and materials. Preserve original assets and edit copies. The command `scripts/inspect_glb.py <file-or-dir> --out <report.json>` reads metadata only; it does not verify rendering, UVs, orientation, or world coordinates.

Use compatible JS libraries or BufferGeometry for booleans, lofts, and local repairs. Do not routinely reduce mesh density or retopologize. When requested, preserve UVs, normals, material groups, and required skinning attributes; compare original and candidate from the same camera and revert failed edits. If a compatible implementation is unavailable, retain the source and explain the specific gap. Three.js is not a complete automatic sculpting, retopology, or rigging system.

## Assembly

Choose the reference part, scale, up/forward axes, and import transforms. Use relative proportions when dimensions are unknown. Fit measured anchors and reference features using uniform scale, rotation, and translation. Do not align only by bounding-box centers or distort faces to hide mismatches.

Update world matrices before reading anchors. Preserve world transforms when reparenting, convert to new local coordinates, and measure the result. Check mirrored normals, winding, and lettering. Inspect real contact paths and mounting surfaces. For continuous seams, inspect the full ring and cross sections; a zero nearest-point distance does not establish a good fit.

Assemble main structures and critical seams before occluding accessories. Keep edits in the Three.js project and source, with one writer per project. Inspect necks, thin shells, and wings for axes, inside/outside surfaces, placement, and occlusion. Surface detail follows its owning part.

## Validation and export

1. Compare silhouette, proportions, identity features, connections, and materials against the reference from front, side, back, and oblique views. Treat unseen structures as inferred.
2. Run relevant build/type checks and actual Three.js rendering. Compilation and metadata are not substitutes for visual inspection.
3. Export with GLTFExporter and reload with GLTFLoader into a clean scene. Check nodes, textures, finite world coordinates, bounds, and transforms. Convert custom shaders to exportable representations or document limitations.
4. Fix observed defects locally and recheck affected views. Retain necessary validation evidence without per-pass scores or mandatory snapshots for every part.
5. Deliver the validated GLB, Three.js source, parameters, and inspection records; update the delivery index.

Completion depends on the user's use, important identifying features, and required deliverables. Missing key parts, clearly wrong materials, severe intersections, and lost export resources remain unfinished work. Continue authorized local repairs. If completion needs spending or scope beyond authorization, label the current version incomplete, request the smallest necessary decision, and continue unaffected work. Minor harmless deviations can be documented without redundant checks. Remote completion, a successful download, and a successful reload alone do not prove the full task is complete.

Default to a static model. Provide interactive or animated GLB only when requested. Use real hierarchy and AnimationClip/AnimationMixer as appropriate; check joints, linkages, keyframe collisions, and exported playback. Static AI meshes are not automatically rigged. Label turntables as presentation animation. Verify reassembly after exploded motion; exploded views do not replace fit checks.

Distinguish unique-mesh face counts from totals including instances. Do not call GLB a CAD solid or STEP, or claim print/animation readiness without validation.

## Runtime

Use [bundled runtime integration](setup-integration.md) for dependency checks, Three.js/Node resolution, and installation. Preserve existing project dependencies and explicit paths.
