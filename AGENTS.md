# Art production instructions

User preference recorded 2026-11-01:

- Before modeling any subsequent vehicle, character or environment, request visual references from the user if adequate images have not already been supplied. Inspect the images before defining the silhouette or mechanisms.
- When references exist, work from their visible forms; do not treat search-result descriptions as equivalent to inspecting photographs.
- Distinguish toy editions, cartoon captures and inferred geometry. Label estimated measurements and kinematics.
- Preserve editable sources and previous iterations. Render, inspect and correct visible problems before claiming a modeling milestone complete.
- Thunderhawk: no cockpit in this exterior modeling step. Doors have a roof section and a side section with a real bend. Rear fascia translates vertically; spoiler moves independently. Both door cannons remain separate named parts.

## Reusable vehicle, character and mask workflow

User preferences recorded 2026-11-02:

- Build each vehicle, character and mask as an independent editable asset. Keep separately reusable source `.blend` files as well as the assembled vehicle scene.
- A masked character is the SAME character with a separately modeled mask attached to the head. Never create different underlying characters for masked/unmasked variants. Keep the face underneath and provide a simple mask visibility control.
- Standing and seated/driving states must use the same articulated character and meshes. Preserve editable armature/weights and provide named poses or an explicit pose control. Do not substitute disconnected mannequin primitives for a finished realistic character.
- Work from photographs actually supplied or explicitly approved by the user. Inspect the images themselves before modeling; descriptions or search-result snippets are not visual evidence. If only illustrations, cartoon frames, toys or replicas are supplied, identify those categories and their limits rather than presenting them as photographs of an authoritative real-world design.
- Request missing photographs before defining an unreferenced vehicle, character, mask or mechanism. An explicitly authorized interpretation is permitted; record that authorization and label the interpreted geometry. The Thunderhawk interior was explicitly authorized as an interpretation on 2026-11-02.
- Use Blender through the installed MCP connection for modeling and inspection. If MCP cannot be reached, tell the user promptly; do not silently replace that workflow.
- Always inspect the actual Blender scene and rendered views against the photographs. Check silhouettes, proportions, colors, face, mask, visible mechanisms and part relationships from several angles. Correct visible defects and render again before claiming completion. Treat extremely high reference fidelity as a validation target, not a claim that can be made without matching visual evidence.
- Check both standing/driving poses with and without the mask. In the assembled car, check roof and glass clearance, seat contact, hands on the wheel, feet at the pedals and every transformation phase. Timing checks alone are not a geometric collision check.
- Keep previous iterations and editable sources. Report unresolved fidelity, deformation, fit or reference limitations candidly. A procedural build or successful file save alone does not establish an artistic milestone.
- Thunderhawk rear reactors extend slightly only AFTER their cover has fully risen, and retract BEFORE the cover descends. Spoiler motion remains independent; rear cover translates vertically; both door cannons remain separate named parts.

## Matt realism interpretation authorization

User authorization recorded 2026-11-02: a realistic human interpretation of the supplied illustrated Matt Trakker portrait is explicitly authorized, without resemblance to any particular real person. Keep the existing articulated character as the editable basis, with the same character used for standing/seated and mask visible/hidden states. The user specifically rejected a cylindrical Spectrum silhouette and a toy-like articulated appearance; refine helmet shapes from the supplied replica photographs and label invented anatomy and unshown geometry as interpretation.

## Capitalized production method

User request recorded 2026-11-03: retain the successful vehicle, character and mask workflow to improve the first pass of future M.A.S.K. assets, including trucks, planes and helicopters.

- Before the next M.A.S.K. asset, read `.agents/skills/mask-asset-production/SKILL.md` and the relevant branch references. The project copy is the editable source; a discoverable copy is installed in the personal Codex skills directory.
- For character refinements, inspect neck/jaw/shoulder profiles and deformation in both poses. A shortened mesh alone does not fix a twisted or compressed neck rig. For Spectrum, preserve the photographed flared shoulder-fitting silhouette instead of a cylindrical sleeve; distinguish rigid shell from the interpreted flexible collar.
- Reuse the tested MCP render/export workflow with scene-specific configuration, preserved sessions, inspected renders and reopened independent sources. Record remaining limitations instead of treating procedural completion as artistic validation.
- Keep Thunderhawk-specific mechanisms separate from general methods. Truck and aircraft guidance is prepared for future reference-based validation, not evidence that those vehicle families have already been modeled or validated.

## Rhino requirements recorded 2026-11-03

- Work from inspected images in `Images de reference/rhino`, distinguishing toy editions, Kenworth W900B photographs and Alex/Bruce illustrations/toys.
- Rhino advances its bullbar, lowers both exhausts as cannons, opens the rear cockpit for the missile, and detaches an independent rear vehicle. Split middle dual wheels between truck and module without duplicating/disappearing tires.
- User corrections: lower hood to clear the main windshield; lower the upper panes and angle them outward in plan; a small independently rotating roof radar. The large rear cabinet translates aft to enlarge the missile opening and returns only after launcher retraction.
- V2 uses estimated 0.80m cabinet travel and a single dark projectile from the supplied toy references. Keep these local estimates separate from official dimensions or general truck rules.
- Alex and Bruce are distinct editable characters, each with one rig/body/head for standing/seated and a separately visible mask. Recheck surface-deform bindings after a garment topology change; stale binds can stretch patches across the body.
- Rhino bullbar correction: inspect `Images de reference/rhino/rhino pare buffle.jpg`. Use a complete closed outline with vertical bars, matching the cooling grille width and height. The uprights must not extend above the grille. Keep the existing forward sliding mechanism.

## Boulder Hill requirements recorded 2026-11-05

- Inspect all supplied images in `Images de reference/boulder hill` and the user video `https://www.youtube.com/watch?v=CYgT9k8lJyY`, seconds 1–13. Distinguish toy photographs from cartoon geometry. Hidden mechanisms, enlarged interior and dimensions remain estimates.
- Pumps become cannons; GAS sign face opens downward to reveal two cannons; cap falls off the column before the cannon and chair emerge. Garage armor rotates horizontally through a quarter circle and opens a double gate for actual-scale vehicles.
- The storefront IS a triangular prism. Inspect `Images de reference/prisme-triangulaire-k9-en.webp`. The entire prism pivots about the lower front edge: its glazed face goes against the ground and its inclined steel face becomes exposed. Do not animate a separate armor prism emerging after the glass drops, or substitute a flat tilting panel.
- The base is backed into a tall mountain. Do not represent the mountain as a low flat rocky roof or rectangular block. Keep the mobile cap and cannon promontory distinct from the much larger backing mountain.
- No road is needed in front of the exit: retain a simple rectangular slab.
- User approved the V3 mountain shape but requested a smaller mass. Retain its shape, integrate the cannon/cap promontory into the mountain flank, close side slots at shop/garage jambs and keep slab margins tight around the buildings. Do not leave an isolated terraced column on a broad flat ledge.
- Provide space for several vehicles and check their route through the quarter-circle gate with the existing meshes and conservative envelopes. Keep the base independently reusable, with demo vehicle sources unchanged.
- Preserve the approved rock palette when refining geometry. User rejected the pale beige V4, then found the dark brown V5 too dark and the scene insufficiently lit. V6 uses a warm intermediate brown with stronger ambient daylight and a broad soft frontal fill. Do not silently change colors as part of a silhouette correction.

## Hurricane requirements recorded 2026-11-05

- Inspect supplied photographs in `Images de reference/Hurricane et Hondo McLean` and the toy transformation video `https://www.youtube.com/shorts/YUgEYpsLrc4`. Use the turquoise/flame Hurricane and purple/yellow Hondo reference set; distinguish the red/green outfit variant and the real 1957 Bel Air photographs.
- Roof opens toward the front and reveals a twin cannon. Hondo uses one rig/body/head for standing, driving and gunner poses, with a separately visible turquoise/red mask and face retained underneath.
- Six persistent road tires: four normal wheels and a retractable middle pair. The body/chassis raises moderately; the upper part of the middle wheels remains slightly covered by the body. V3 estimates 0.30m lift, replacing the rejected 0.58m.
- The black lower structural block must be substantially taller, with structural uprights between the wheels. Do not leave a thin skeletal frame beneath a body lifted too high.
- Windshield cannon is on the RIGHT side of the vehicle (-Y in the +X-forward project coordinates), superseding the initial left-side instruction. Front headlights telescope as cannons; additional lower front cannons deploy after clearance.
- Rear toothed disc and ejected covered spare wheel are distinct persistent assemblies. Spare launches rearward, as shown in the supplied video; do not duplicate the wheel or confuse it with the saw.

## Session handoff requirements

User preference recorded 2026-11-09:

- At the end of every substantial milestone or work batch (implementation, asset production, validation, or documented blocker), update `HANDOFF.md` at the workspace root before reporting the result. Also update it when the user requests a session handoff. Do not require another confirmation for this documentation.
- The canonical handoff is `G:/DEV/mask-project-mayhem/HANDOFF.md`. The Unreal Git repository is nested under `VehicularCombat`; distinguish workspace paths from repository-relative paths. A new session must read the handoff, then inspect the current repository state before continuing.
- Base each update on the conversation AND actual files: inspect Git status, staged/unstaged diffs, branch and relevant commits, affected files, test reports, and any unfinished processes or unsaved work. Preserve unrelated changes and editable sources.
- Keep the handoff concise and operational (ideally 400–800 words): objective, verified/partial/not-started state, technical decisions, exact paths and roles, uncommitted changes, actual commands/results, known issues and hypotheses, and ordered next steps. Link detailed reports instead of copying code or narrating the conversation. Never imply that a whole milestone passed because only compilation or saving passed.
- End `HANDOFF.md` with “Première action recommandée” and an immediately executable next action. Record running task identifiers/logs and how to recover them if a batch cannot finish; do not claim a safe checkpoint while unrecorded or unsaved state remains essential.
- Once the handoff is current and a resumable checkpoint is established, explicitly tell the user in French: “Le handoff est à jour ; tu peux changer de session Codex.” Link `HANDOFF.md` and give a short resume instruction. This means session continuity is ready, not that the overall project is complete. Do not force a session change or stop authorized work solely to request confirmation.
