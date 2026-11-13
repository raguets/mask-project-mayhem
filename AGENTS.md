# Art production instructions

## Autorisation générale d’interprétation — 2026-11-13

L’utilisateur autorise désormais toujours une interprétation réaliste des personnages d’après les références fournies, ainsi que des cockpits non montrés. Cette autorisation s’applique notamment à Miles Mayhem et au cockpit de Switchblade. Ne pas redemander cette autorisation ; distinguer les formes observées des détails/anatomie/dimensions interprétés, sans prétendre reproduire une personne réelle.

## Switchblade / Miles / Viper — 2026-11-13

- Fiche transformation à lire avant images. Catégorie hélicoptère / avion : stationnaire et atterrissage en hélicoptère ; pas de stationnaire en avion. Tous les mécanismes commencent ensemble.
- Verrière basse au niveau de la partie arrière, large à l’arrière sur toute la largeur du cockpit puis se rétrécissant légèrement vers l’avant. Nez prolongeant sa pente et le dessous du cockpit ; dessous massif, modérément bombé avec fond plus plat. Fermer les jours aux côtés arrière du vitrage et entre les parties haute/basse du cockpit.
- Ailes repliées suivant les bords de la queue, légèrement plus larges près du cockpit et convergentes vers l’arrière ; elles rejoignent les petites ailes latérales. Déployées : bord arrière perpendiculaire au corps (constant X), bord avant oblique réduisant la corde vers l’extérieur. Dernière correction de planforme prioritaire sur les anciennes approximations.
- Les faces EXTÉRIEURES des ailes stockées remontent pour devenir leur DESSUS déployé. Contrôler l’ouverture dès ses premières phases contre la queue. Charnières et liaisons d’ailes ne doivent pas être visibles ; ne pas laisser de pièces rapportées au-dessus de la verrière.
- Les deux pales se superposent sur la queue. La dérive remonte en pivotant PAR L’ARRIÈRE dans le plan longitudinal vertical, pas latéralement.
- Les patins deviennent des canons SOUS les ailes ; partie arrière des rails légèrement allongée. Garder les mêmes pièces persistantes.
- Miles garde un seul corps/tête/rig pour les poses ; Viper indépendant et amovible. Ajuster le bord inférieur de Viper sur les épaules réelles et vérifier son suivi dans les deux poses.
- Corrections suivantes du13/11 : cacher le support/pivot visible de la dérive ; dérive avion au bord arrière vertical/plat et bord avant oblique. Supports de patins plus étroits et courbes, balayés vers l’arrière, couverts par les ailes en avion. Peintures présentes sur grandes ailes ET petites ailes avant, visibles dans le viewport et les rendus.
- Élargir légèrement les deux pales. Une fois leur repli terminé, abaisser leur base pour les plaquer contre le pont derrière le cockpit. Réduire encore le ventre avant : quille plus anguleuse remontant vers le nez, nez gardant de l’épaisseur dessous. Supprimer les pièces latérales du vitrage qui flottent sans liaison ; ajouter les deux prises d’air métalliques aux flancs supérieurs vers le milieu.
- Dernières proportions du13/11 : supports de patins plus larges, patins légèrement reculés ; grandes ailes un peu plus larges avec bord avant davantage balayé pour continuer les petites ailes de cockpit ; deux ailerons arrière légèrement agrandis. Nez plus large au bout, sans cassure de pente : dessus prolonge le dernier plan du vitrage, dessous prolonge la quille avant en ligne droite.
- Dernière correction de courbure : les supports descendent de l’AVANT vers l’ARRIÈRE ; seule leur convexité intermédiaire pointe vers l’AVANT. Ne pas inverser toute la pièce. Petites ailes avant plus larges à l’arrière et davantage obliques, avec terminaison droite : dernière demande les prolonge un peu pour toucher les ailes principales, sans les croiser. Deux canons escamotables intégrés dans leur avant. Prises d’air métalliques légèrement plus proéminentes.

## Raven glazing and roof corrections — 2026-11-11

- Roof width is approximately three equal parts: left door roof wing, fixed center, right door roof wing. The side roof parts follow their doors and become winglets when opened.
- Inspect `Images de reference/Raven et Calhous Burns/s-l500.jpg` for the curved trapezoidal windshield outline; do not substitute a rectangle.
- Rear hatch glass has a rounded outline, is very dark, and extends down/back to the reactor cassette. Keep a black structural pillar between each door rear edge and this glass. Preserve the gentler windshield/roof transition and horizontal rear cassette roof.
- Round the transition between each door window and its roof wing. The wing becomes slightly narrower towards the front, producing a taper; keep it integral to the same door hinge.

User instruction recorded 2026-11-11: each vehicle/character/mask reference folder now contains `Fiche transformation.txt`. Read this file FIRST, before inspecting the images or defining the asset's transformation. Treat it as the user's mechanism specification and still inspect the supplied images for visible geometry.

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

## Raven requirements recorded 2026-11-11

- Read `Images de reference/Raven et Calhous Burns/Fiche transformation.txt` FIRST. Use the inspected Raven toy images, Corvette C4 photographs and Calhoun illustration/figurine as distinct reference categories.
- User explicitly authorizes realistic interpretation of Calhoun's anatomy/face and unshown cockpit geometry, without likeness to a real person. Keep one articulated character/head for standing/driving, with a separately visible mask and independent editable sources.
- All transformation mechanisms move simultaneously: doors fold down on their lower hinges as wings; hood flips around its longitudinal axis; front wheels fold onto the hood, rear wheels under the trunk; four reactors are revealed above the fixed rear lamps. The orange serrated front disc is an independent weapon. Air/water use is intended, not a validated simulation.
- User corrections: only a SHORT rear section moves VERTICALLY, without hinging/tilting. Doors must be visibly curved, not flat boards. The small black wheel cannons lie in the rim planes as diametric bars, not axle-aligned stubs; deployment is slight.
- Later corrections supersede the separate-hood interpretation: the ENTIRE FRONT UNIT rotates longitudinally, carrying front bodywork/bumper/lamps AND wheels. The front wheels then only need a secondary tilt onto the inverted unit. Rim cannons are RECESSED at rest and rise45degrees on deployment, pointing forward; do not leave them floating above the wheel face.
- Finishing corrections: the COMPLETE four-reactor cassette rises only enough to reveal the jets; its black body skin is just the HORIZONTAL top and side walls with rounded transitions, not an independent lifting lid over fixed jets. Do not end the tail with a sloping panel. Keep the hood rigid, smooth and flush with the fender shoulders; remove the fixed projecting cowl ahead of the windscreen and shorten the fixed cabin floor before the rolling front. Close unintended panel slits while preserving functional joints. Double all four rim-gun widths and their recesses. Windshield/roof/rear glass need gentle continuity, with a small front fillet rather than a strongly rounded bubble.

## Condor requirements recorded 2026-11-12

- Read `Images de reference/Condor et Brad Turner/Fiche transformation.txt` before the images. Original toy, modern reissue, cartoon captures and illustrated Brad portrait are distinct reference categories.
- Condor is road / helicopter: maximum airborne braking permits stationary hover; forward flight pitches the nose slightly down. Rhino/Hurricane are road / road, Thunderhawk/Raven road / airplane with no stationary hover. Asset controls describe this intent; gameplay integration needs separate validation.
- Major transformations start simultaneously: skids deploy while seat descends, side rotor supports pivot upward from low behind the seat and then blades unfold, rear wheel pivots aft into the tail rotor, cannon extends from the front opening.
- Rear cowl is one continuous block with planar/chamfered faces, narrower and thinner aft; lower edge slopes down toward the seat base. No tubular tail. Blades fold against that block alongside their pivoting supports, never extending aft as stored blades.
- Front has slightly pronounced planar faces and a single square opening for the retractable cannon; no twin headlights. Windshield has a central facet and two angled side returns extending down to the green chassis.
- Brad realistic anatomy/face interpretation explicitly authorized 2026-11-12 without likeness to a real person. Keep one editable character/head/rig for standing/riding with independent removable Hocus Pocus mask. Black visor belongs to the mask and completely closes the eye opening; retain the face beneath.
- Further corrections: front nose tapers more; rear road wheel sits slightly farther forward. The rear wheel fork must stay attached to a fixed chassis pivot throughout deployment. Hocus Pocus covers the WHOLE face; mouth/chin shell must be compact and closely fitted, not a bulky open frame.
- Shorten the whole green rear block and adapt rotor storage/supports accordingly. Seat and landing skids belong to the same descending block. Nose must be short and follow the windshield's descending profile.
- Hocus Pocus must be one continuous piece, including a diving-goggle-shaped black visor and a flared lower part fitting the upper shoulders. Preserve head/shoulder weighting for both poses; no open eye or mouth frame.
- Rear block must narrow progressively aft, allowing rotor-support arms to converge instead of staying parallel. A central rotating hub at their top must visibly carry both blades. Whole front/windshield must be narrower and finer. Mask neck must not pinch; provide an integrated raised vocal grille before the mouth, in the spirit of Darth Vader's mask.
- Front weapon-opening face tilts slightly upward (lower edge farther forward). Helmet front/side transition is squarer with softened corners; diving-goggle visor stays ONLY on front face, never wraps onto the yellow sides.
- Latest correction supersedes simultaneous wheel start: rear wheel must tuck well under the green tail in road mode; raise the rotor support partially BEFORE swinging the wheel aft, with geometric wheel/support clearance checks. All visible wheel meshes must follow the actual wheel hub, not merely an empty controller.
- Landing skids must sit directly below the seat cassette and remain rigidly attached to that same moving block; no independent lateral spread. Reduce helmet posterior bulk and add raised vertical black rods on both yellow sides, keeping one connected mask mesh.
- Rear wheel swing arms are TWO wider, flat bars mounted INBOARD beneath the rear chassis, hidden externally when stored. Keep their hinges below the body skin, not as external rods or exposed upper mounts.

## Condor gameplay corrections — 2026-11-12

- Allow conversion while driving, with mechanism clearance still checked. Do not require a stop for Condor.
- Road/airplane and road/helicopter return must descend directly and promptly, with a short near-ground flare. Condor must brake promptly when returning to road and accelerate more readily in flight.
- Retain motorcycle cornering lean but damp left/right oscillations. Check alternating turns, not only straight driving.
- User reports folded rotor support entering the road. Check actual ground clearance under suspension, pitch and lean; a static source bounding box alone is insufficient evidence of a fix.

## Session handoff requirements

User preference recorded 2026-11-09:

- At the end of every substantial milestone or work batch (implementation, asset production, validation, or documented blocker), update `HANDOFF.md` at the workspace root before reporting the result. Also update it when the user requests a session handoff. Do not require another confirmation for this documentation.
- The canonical handoff is `G:/DEV/mask-project-mayhem/HANDOFF.md`. The Unreal Git repository is nested under `VehicularCombat`; distinguish workspace paths from repository-relative paths. A new session must read the handoff, then inspect the current repository state before continuing.
- Base each update on the conversation AND actual files: inspect Git status, staged/unstaged diffs, branch and relevant commits, affected files, test reports, and any unfinished processes or unsaved work. Preserve unrelated changes and editable sources.
- Keep the handoff concise and operational (ideally 400–800 words): objective, verified/partial/not-started state, technical decisions, exact paths and roles, uncommitted changes, actual commands/results, known issues and hypotheses, and ordered next steps. Link detailed reports instead of copying code or narrating the conversation. Never imply that a whole milestone passed because only compilation or saving passed.
- End `HANDOFF.md` with “Première action recommandée” and an immediately executable next action. Record running task identifiers/logs and how to recover them if a batch cannot finish; do not claim a safe checkpoint while unrecorded or unsaved state remains essential.
- Once the handoff is current and a resumable checkpoint is established, explicitly tell the user in French: “Le handoff est à jour ; tu peux changer de session Codex.” Link `HANDOFF.md` and give a short resume instruction. This means session continuity is ready, not that the overall project is complete. Do not force a session change or stop authorized work solely to request confirmation.
