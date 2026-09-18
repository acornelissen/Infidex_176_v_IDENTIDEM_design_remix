# Infidex 176 V x IDENTIDEM.design Remix

> **This is a remix of someone else's design.** The Infidex 176 V is an open source 3D-printed panoramic 35mm camera by **Denis Aminev (Time to Waste)**. Everything here builds on his work.
>
> - Original project: **[Infidex 176 V on GitHub](https://github.com/max05210238/Infidex_176_V)**
> - Original designer: **[Denis Aminev — Time to Waste on YouTube](https://www.youtube.com/@time_to_waste)**
> - This remix: **[IDENTIDEM.design](https://IDENTIDEM.design)**
>
> Print the original first if you want the camera as Denis designed it. Attribution stays with him; please keep it with any further remix.

![The remixed camera, back three-quarter view](docs/hero_iso.png)

## What this remix is

The camera is unchanged where it counts: same 3:1 panoramic frame on 35mm film, same Mamiya TLR taking lens, same overall shape. What changed is how it goes together and how you know where you are on the roll.

| | Original | This remix |
|---|---|---|
| Body | One piece | Reworked, and supplied two ways: in one piece, or as two halves glued together with a light-tight lip and alignment pegs |
| Frame counting | Count as you wind | Sprocket-driven gear train and a numbered counter face, starting at 25 |
| Rewind knob | Spring detent | Three ball plungers |
| Take-up coupling | Dog coupling | Ratchet-inner with three ball plungers for wind and rewind, magnets optional |
| Spool retention | Glued washer | Printed split collar that clicks into the groove |
| Pressure plate | Foam | Printed leaf-spring platen, bonded to the door at both ends |
| Fixings | Glue and press fits | Heat-set inserts and screws throughout |
| Viewfinder | Separate | Cold-shoe viewfinder coupled to the focus helicoid |

![Front three-quarter view with the lens standard and viewfinder](docs/hero_back.png)

## Specifications

Carried over from the original design:

- **Format:** 3:1 panoramic, 72 × 24 mm on 35mm (135) film
- **Frames:** 18 per 36-exposure roll, or 19 if you load in darkness
- **Lens:** Mamiya TLR taking lens, 80mm or 55mm, from the C2/22/220 or C3/33/330 series
- **Body:** about 168 × 67 × 38 mm
- **Filament:** under 600 g for a camera
- **Tripod mount:** 3/8"-16 thread printed straight into the base, five turns and 8.5 mm deep. Most tripods and quick-release plates are 1/4"-20, so fit a 3/8" to 1/4" bushing and leave it in. Start it by hand: a printed thread strips if you drive it with a tool.

Specific to this remix:

- **Frame counter:** 50:1 spur train, module 0.6, four meshes (12:32, 12:30, 12:30, 12:36), one counter-face turn per 25 frames
- **Counter face:** starts at 25 as the loading position, then reads 1, 2, 3 and on as you wind; friction-fitted under a thumbscrew, reset by loosening it and turning 25 back to the marker

## Files

| File | What it is |
|---|---|
| `Infidex176V-IDENTIDEM.design-remix.step` | Full assembly, STEP, for any CAD package |
| `Infidex176V-IDENTIDEM.design-remix.f3d` | Fusion source for the camera |
| `Infidex176V-IDENTIDEM.design-remix-counter-train.f3d` | Fusion source for the parametric counter gear train |
| `Infidex176V-IDENTIDEM.design-remix.3mf` | Print-ready project, parts laid out |
| `Infidex-Hardware-Map.pdf` | Hardware placement and assembly guide, 6 pages |
| `tools/InfidexCounterTrain/` | Fusion script that rebuilds the counter train from parameters, see [`tools/README.md`](tools/README.md) |
| `docs/` | Section drawings used in this README |
| `NOTICE.md` | Denis's redistribution notice, and the remix notice |

## Printing

Print settings follow the original profile and work well in PETG:

- 0.4 mm nozzle, 0.2 mm layer height
- 4 perimeters, up to 25% infill
- Denis printed the original in ABS. PETG works well and is easier to live with
- Both halves of the two-piece body sit flat on their seam face, which puts the largest surface on the bed. Add supports wherever your slicer flags overhangs
- The one-piece body prints as in the original if you would rather not glue

The counter train gears are the finest parts in the model. Print them with the rest of the camera, check the teeth before assembly, and reprint if a tooth is short.

## Hardware

Full placement, hole sizes and fitting order are in [`Infidex-Hardware-Map.pdf`](Infidex-Hardware-Map.pdf). In short:

| Item | Qty | Where |
|---|---|---|
| M2 × 4 heat-set inserts | 10 | Top cover ×5, cold shoe ×2, counter gear, ratchet-inner, sprocket |
| M3 × 4 heat-set inserts | 4 | Lens standard, front face |
| M2 × 6 countersunk screws | 6 | Top cover ×5, advance knob |
| M2 × 4 countersunk screws | 2 | Cold shoe |
| M3 × 4 cap or countersunk screws | 4 | Lens standard |
| M2 × 6 cap or countersunk screw | 1 | Sprocket gear to sprocket |
| M2 × 4 thumbscrew | 1 | Counter face |
| D2×3 flanged ball plungers | 6 | Rewind bore ×3, take-up bore ×3 |
| Ø5 × 2 magnet | 1 | Ratchet-inner (optional, recommended) |
| Ø4 × 2 magnets | 2 | Take-up spool head (optional, recommended) |
| 3/8" to 1/4" tripod bushing | 1 | Base, in the printed 3/8"-16 socket |

Fit the inserts first, then the plungers, then the magnets, so the soldering iron never reaches a magnet or a pressed-in plunger.

These are carried over from Denis's build and are not in the printed files, but the remix still needs all of them: black flocked self-adhesive paper for the film chambers and the inside of the door, black light-seal foam where the door closes, 0.6–0.8 mm rigid stainless wire for the springs and linkages, and superglue. Flocking and foam go on last, after a dry run with the back open.

![Body from above with insert and plunger positions](docs/fig1_body_top.png)

### Screws and inserts in section

Each screw length is the longest that stays inside its insert without bottoming out. The guide shows the head seats and hole bottoms taken straight from the CAD.

![Screws seated in their inserts](docs/fig9_screws.png)

### Take-up axis

The advance knob screws down into the ratchet-inner, which sits over the spool head. The optional magnets hold the two together, and the split collar under the body stops the spool lifting.

![Section through the take-up axis](docs/fig5_takeup_stack.png)

### Ball plungers

Three plungers around the rewind bore and three around the take-up bore, each fitted from inside the bore with the ball pointing at the shaft.

![Take-up bore in the top cover with three plunger holes](docs/fig2_cover_plungers.png)

### Pressure plate

One printed part: a rigid platen on a single thin leaf, glued to the door at the two end pads only. Closing the door flexes the leaf and that flex is the pressure on the film.

![Pressure plate in the door](docs/fig10_pressure_plate.png)

## Body: one piece or two

Both bodies are remixed parts, not the original. The one-piece body carries all the changes above and needs no gluing. The two-piece body is the same part split horizontally through the middle, which suits a smaller printer and puts both halves flat on the bed, seam face down.

If you print the two-piece body, the halves meet on a flat seam about 34 mm above the base. A 2 mm ridge on the bottom half runs into a groove in the top half all the way around the film chambers and the film path, so light coming in along the glue line has to climb over a step to reach the film. Four Ø3.8 × 2 mm pegs in the top half's groove drop into Ø4 mm holes in the ridge and set the halves. Fit every insert, plunger and magnet while the halves are still apart, then glue on the flat land outside the ridge. Dry-fit first: if the halves rock, the ridge is not seating.

The hardware is the same either way.

## Parametric counter train

`Infidex176V-IDENTIDEM.design-remix-counter-train.f3d` holds the counter gear train as a parametric model, so you can change it without redrawing the gears. The sprocket and dial axes stay fixed where the body needs them; the two idler axes follow from the centre distances. Module, tooth counts, profile shift, backlash, face width and bores are all parameters, so a different reduction or a coarser module is a table edit and a rebuild.

Start from the values in the file if you are only nudging it: the train is 50:1 in four meshes and the gears are already near the limit of what a 0.4 mm nozzle resolves.

`tools/InfidexCounterTrain/` is a Fusion script that builds the same train from a table of `ct_*` user parameters, so you can change module, tooth counts, backlash or the idler positions and rerun it rather than redrawing the gears. It refuses to build a layout that cannot close or that would clash with the sprocket hub or the dial disc. The gear maths sits in plain Python next to it with tests you can run outside Fusion. See [`tools/README.md`](tools/README.md).

## Credits and licence

Original design by **Denis Aminev (Time to Waste)**: [YouTube](https://www.youtube.com/@time_to_waste) · [Infidex 176 V repository](https://github.com/max05210238/Infidex_176_V).

There is no formal licence on either the original or this remix. Denis gave permission to redistribute the project files on any platform, with attribution to him kept intact, and the same terms apply here: use it, print it, sell prints of it, fork it, but keep the credit and keep [`NOTICE.md`](NOTICE.md) with it.

Remix, hardware guide and drawings by [IDENTIDEM.design](https://IDENTIDEM.design).
