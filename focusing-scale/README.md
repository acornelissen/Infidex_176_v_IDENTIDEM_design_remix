# Infidex 176 V — Focusing Scale Generator

A generator for the focusing scale strip on the
[Infidex 176 V](https://github.com/max05210238/Infidex_176_V) helicoid. The strip is drawn
against a millimetre rule so you can read its real length at a glance, the focus
ring can be turned to check the marks land where you expect, and the export is a
1:1 SVG ready to print and wrap.

Derived values are shown in brackets, as reference dimensions are on a real
drawing.

## Running it

It is one static page with no build step. Open `index.html`, or serve the
directory with anything:

```
python3 -m http.server
```

## Where the numbers come from

The helicoid figures were measured off the printed parts rather than assumed:

| | |
|---|---|
| Thread lead | 5.0005 mm per turn, single start |
| Focus ring diameter | 61.00 mm |
| Grip band height | 13.5 mm |

The lead was taken by cross-correlating the focus ring's bore profile between
heights: the profile rotates −71.99°/mm and repeats with exactly 0.00° of
rotation at Δz = 5.00 mm.

Extension follows from rotation, `extension = lead × rotation / 360`, and the
subject distance from the thin-lens relation `e = f² / (u − f)`. At the default
340° that gives ∞ to 1.44 m with the 80 mm lens, or ∞ to 0.70 m with the 55 mm.

The two inner rings in the Infidex STL set — 41.70 mm for the 55 mm lens, 36.10 mm
for the 80 mm — position each lens so infinity still lands, so focal length is the
only thing that changes between the two builds.

## Gerber output

The Gerber button produces a zip of the same scale as a flexible PCB, which
gives you a far more durable strip than paper: white silkscreen on black
coverlay is exactly the artefact.

Order it as **1 layer, flexible, black coverlay, white silkscreen**. The set is
one layer only so the fab's parser doesn't read it as two.

| File | |
|---|---|
| `.GTL` | copper, a plain pour inset 0.5 mm from the edge |
| `.GTS` | soldermask, deliberately empty |
| `.GTO` | silkscreen, the scale itself |
| `.GKO` | board outline |
| `.DRL` | drill, no holes |
| `Bottom Stiffener.GBR` | where the 3M468 adhesive goes |

If you take the 3M468 tape option under Stiffener, JLC need the stiffener *area*
as well as the order option — selecting one without the other gets the file
queried. That layer marks the whole back face, inset 0.3 mm so it cannot
overhang after routing. There is no standard extension for a stiffener layer, so
the filename says what it is, since a person reads it. Order without the tape and
you should delete that file.

The empty soldermask layer is the trick: Gerber's mask layer defines *openings*,
not coverage, so an empty one means the coverlay covers everything.

The copper does nothing electrically. It is there so the fab builds a normal
flex stack rather than laminating coverlay onto bare polyimide, which their
checks may query. It bends fine at a 30 mm radius for a one-time install.

The scale numerals are set in F5.6 by Sora Sagano, a face built from the same
engraving constraints as Leica's lens lettering. Its outlines are embedded in the
page, so the tape, the SVG, the Gerber and the dial all draw the same numerals and
nothing depends on installed fonts. Gerber has no text primitive, so each numeral
is a filled region with its counters cleared. At the default 13 mm strip the cap
height is 2.86 mm and the strokes 0.39 mm, well over JLCPCB's 0.15 mm silkscreen
minimum; the page warns if a strip height takes them under it. The zero's slash
is removed, since Leica doesn't slash its zeros and on a lens it reads as Ø. F5.6
has no ∞, so that is a Gerono lemniscate drawn at the font's stem weight.

The ∞ and the `m` sit beside their index bars rather than on them, on both the
SVG and the PCB. Silkscreen has no black ink, so a mark on a bar would be white
on white.

## Second turn

The printed helicoid focuses a full revolution past the first strip. Choose
**Band → 2nd turn** to show and export a second strip for that range. It sits at
the same barrel positions one revolution later, so both strips read against the
same index and are the same length. The 340°–360° stretch at the end of each turn
falls in the barrel gap and stays unlabelled.

Each turn has its own height field, so you can run both at full height on
different parts of the barrel, or halve them to stack on the 13.5 mm band.
Exports are named `-band1` and `-band2` and are ordered separately.

The second turn's labels are chosen differently. Distance is close to linear in
angle there, so rounding fixed angles gives values like 1.23 m. It picks round
distances instead, roundest first, and keeps only those with room for a label.

## Which way round

The strip has two independent flips, and confusing them is how you end up with
upside-down numerals:

- **Ticks on → top / bottom.** Which long edge the ticks run from, i.e. which
  side your index mark sits on.
- **Close focus turns → ACW / CW**, seen from the front. Which way ∞ runs round
  the barrel.

Rotating a printed strip 180° to fix the direction does *both* at once, and
drags the numerals round with it. Setting them separately keeps the numbers
upright whichever combination you need.

The defaults are the combination the built camera actually needed: ticks on the
bottom edge, close focus clockwise. Check yours before committing to anything —
set the helicoid to infinity, turn toward close focus, and watch which way the
ring travels past the index. The marks after ∞ must be on the side that arrives
next.

View A is drawn from the front, so it shows you the direction you have picked.
It does not show the tick edge: that is an axial choice, and a plan view has no
axis to show it on.

## Before you cut

Infinity is assumed to sit at the zero-rotation stop. Check it on ground glass
first. If the helicoid racks in past infinity, put the residual extension in the
"Extension at infinity" field and the whole scale shifts to match.

Keep the strip height at or under 13.5 mm — that is the smooth band on the focus
ring, measured from where the flutes sit on the ribbed variant of the part.

## Licences

Page © Albert Cornelissen / IDENTIDEM.design.

Saira Semi Condensed and Azeret Mono are subset and self-hosted, and F5.6's
numeral outlines are embedded, all under the SIL Open Font License 1.1; the
licence texts are in `assets/fonts/`.

## Credits

The camera is [Infidex 176 V](https://github.com/max05210238/Infidex_176_V), an
open source 3D printed panoramic film camera by
[Denis Aminev (Time to Waste)](https://www.youtube.com/@time_to_waste).

The scale arithmetic follows [Parametric Focusing Scale for 17–31 mm, M65 and
M77](https://www.printables.com/model/1610905-parametric-focusing-scale-for-17-31-mm-m65-and-m77)
on Printables, adapted here for the Infidex helicoid.

The idea for using a Flex PCB for decals comes from
[Oscar Oweson](https://panomicron.com).

Scale numerals are set in [F5.6](https://dotcolon.net/fonts/f5_6/) by Sora
Sagano, after Leica's engraving face.
