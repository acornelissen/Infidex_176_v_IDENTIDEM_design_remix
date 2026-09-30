# Changelog

Every release lists what changed, the commits behind it and which parts to reprint.

## Versioning

Versions follow [Semantic Versioning](https://semver.org), read for printed parts:

- **Major**: parts from the previous release no longer fit or mesh with the new ones, so a set of parts has to be reprinted together, or the bought hardware changes.
- **Minor**: new parts, variants, templates or tools. Existing builds are unaffected.
- **Patch**: fixes you pick up by reprinting only the listed parts, each on its own, plus re-exports, mesh repairs and documentation.

Releases are tagged `vX.Y.Z`. Changes that only touch the documentation go into the next release rather than getting a release of their own.

## [Unreleased]

## [2.2.0] - 2026-09-30

The drag dial now clicks onto each frame, and the repository gains tools that check the 3MFs against the STEP. Existing builds are unaffected.

**Reprint:** nothing, unless you want the new counter parts. For a drag dial that clicks onto each frame, reprint `drag-cover` and `drag-counter-face` (or `drag-counter-face-two-colour`) together. Reprint `cold-shoe` only if you want the ISO 518 shoe. The marker position and the knob arrows are cosmetic, so reprint the covers or knobs only for those if you want them.

### Added

- `drag-counter-face` has a detent flute under every frame marker: 25 vertical V-flutes, 120° included, 0.27 mm deep in a plain rim that replaces the ball groove. P7's ball seats on the flute's flanks and drops 0.15 mm, so the face settles with the number centred on the marker and clicks there firmly. [`a72c8d3`](https://github.com/acornelissen/Infidex_176_v_IDENTIDEM_design_remix/commit/a72c8d3), [`3f40a5f`](https://github.com/acornelissen/Infidex_176_v_IDENTIDEM_design_remix/commit/3f40a5f), [`0711087`](https://github.com/acornelissen/Infidex_176_v_IDENTIDEM_design_remix/commit/0711087)
- Engraved arrows on `advance-knob` and `rewind-knob` show which way each one turns. [`3f40a5f`](https://github.com/acornelissen/Infidex_176_v_IDENTIDEM_design_remix/commit/3f40a5f)
- `mise run verify`, `export`, `add`, `plates` and `clearance` check the 3MFs and the counter parts against the STEP, re-export or add parts in place, and manage the project's plates. `mise run guide` and `mise run figures` rebuild the hardware guide. CI runs the tests on every push and the 3MF checks when the CAD, 3MFs or tools change. See [`tools/README.md`](tools/README.md).
- The counter-train script takes a tooth count for each pinion.

### Changed

- The project file gives each counter choice its own plate: plate 10 `simple-cover`, 11 `drag-cover`, 12 the idlers, 13 `simple-counter-face`, 14 `drag-counter-face`. Print the plates for the dial you chose; there is nothing to delete first. The shared counter gears stay on Small parts 2, and with 14 plates Bambu Studio lays them out in four columns. [`71851bb`](https://github.com/acornelissen/Infidex_176_v_IDENTIDEM_design_remix/commit/71851bb)
- `drag-cover`'s tower and P7 sit 0.14 mm nearer the dial. P7 pushes the face across by that much until it meets the cover step, which the first flutes didn't allow for: the ball ran out of travel before it reached a flute, so the face rocked at every frame. [`0711087`](https://github.com/acornelissen/Infidex_176_v_IDENTIDEM_design_remix/commit/0711087)
- `cold-shoe` is drawn to ISO 518. It has the same footprint and the same two countersunk holes for S6–S7, so it fits the body as before. [`f9359b2`](https://github.com/acornelissen/Infidex_176_v_IDENTIDEM_design_remix/commit/f9359b2)
- `drag-cover` uses the same triangle marker as `simple-cover` instead of the arrow on the tower. On both covers the triangle moves 6° round the dial, to exactly five frames from P7, so the detent centres each number on it. `advance-knob`'s bore entry chamfer is 0.5 mm instead of 1 mm. [`3f40a5f`](https://github.com/acornelissen/Infidex_176_v_IDENTIDEM_design_remix/commit/3f40a5f)

### Fixed

- In the CAD, `viewfinder-var-1` sits on the cold-shoe floor like `viewfinder-var-2` instead of 0.03 mm into it. Its printed shape is unchanged, so there is nothing to reprint. [`3bfa478`](https://github.com/acornelissen/Infidex_176_v_IDENTIDEM_design_remix/commit/3bfa478)
- The README and hardware guide: insert sizes, the part file for each idler, where P7 goes in, and other wording. [`638c877`](https://github.com/acornelissen/Infidex_176_v_IDENTIDEM_design_remix/commit/638c877)

## [2.1.0] - 2026-09-27

A choice of counter dial: the existing free-running one, or a new one held by a ball plunger so it reads the same every time. Existing builds are unaffected.

**Reprint:** nothing. To switch to the drag option, print `drag-cover` and `drag-counter-face` as a pair and fit one more D2×3 ball plunger (P7).

### Added

- `drag-cover` and `drag-counter-face`, a matched pair offered as an alternative to the simple cover and counter face. A tower beside the dial, 0.2 mm clear of the face rim, holds a seventh ball plunger, P7, in the same Ø2.2 hole as the others. Its ball runs in a 0.12 mm groove round the rim. The friction keeps the backlash taken up so the dial stops in the same place and doesn't flutter. The marker for 25 is an arrow on top of the tower. [`13bc08e`](https://github.com/acornelissen/Infidex_176_v_IDENTIDEM_design_remix/commit/13bc08e)
- `drag-counter-face-two-colour.3mf`, with the same marker inlay as the simple face. [`13bc08e`](https://github.com/acornelissen/Infidex_176_v_IDENTIDEM_design_remix/commit/13bc08e)
- In the project file, `drag-cover` is on plate 7 beside the simple cover and `drag-counter-face` is on plate 8 beside the simple face. Print one of each pair. [`13bc08e`](https://github.com/acornelissen/Infidex_176_v_IDENTIDEM_design_remix/commit/13bc08e)
- The README and the hardware guide explain how to choose between the two dials, and the guide has a drawing of P7 (Figure 11). [`a93a39c`](https://github.com/acornelissen/Infidex_176_v_IDENTIDEM_design_remix/commit/a93a39c)

### Changed

- `cover` and `counter-face` are renamed `simple-cover` and `simple-counter-face`, in the STEP, the part 3MFs and the project file, and `counter-face-two-colour.3mf` becomes `simple-counter-face-two-colour.3mf`. Their geometry is unchanged. [`13bc08e`](https://github.com/acornelissen/Infidex_176_v_IDENTIDEM_design_remix/commit/13bc08e)
- The parametric counter-train model has the 2.0.2 idler bores, so it matches the main model again. [`d89cc10`](https://github.com/acornelissen/Infidex_176_v_IDENTIDEM_design_remix/commit/d89cc10)

## [2.0.2] - 2026-09-27

Closer-running counter idlers, and a sprocket that no longer binds in the body. The new parts fit a 2.0.1 build.

**Reprint:** `counter-coupling-gear`, `counter-idler-1` and `counter-idler-2`. Reprint your body (`body-solid`, or `body-top`) only if the sprocket binds in it.

### Fixed

- The idler bores are 0.2 mm over their pins, down from 0.4 mm: `counter-coupling-gear` from Ø4.4/Ø3.6 to Ø4.2/Ø3.4, `counter-idler-1` from Ø3.61 to Ø3.4 and `counter-idler-2` from Ø3.6 to Ø3.4. Face heights and outer dimensions are unchanged. [`3587f2b`](https://github.com/acornelissen/Infidex_176_v_IDENTIDEM_design_remix/commit/3587f2b)
- The body's hole for the sprocket shaft is Ø6.2, up from Ø5.8, which was tighter than the Ø6.0 shaft. [`26c1d61`](https://github.com/acornelissen/Infidex_176_v_IDENTIDEM_design_remix/commit/26c1d61)

### Changed

- The counter-train generator defaults match the new bores. [`3587f2b`](https://github.com/acornelissen/Infidex_176_v_IDENTIDEM_design_remix/commit/3587f2b)
- The README gives the idler bore sizes and how to free a tight idler.

## [2.0.1] - 2026-09-25

Tighter tolerances where printed parts showed gaps. The new parts fit a 2.0.0 build.

**Reprint:** `cover`, `sprocket` and `ratchet-coupling-gear`.

### Fixed

- Tighter tolerances on the `cover`, `sprocket` and `ratchet-coupling-gear`, which printed with gaps. Outer dimensions are unchanged. [`b55eabc`](https://github.com/acornelissen/Infidex_176_v_IDENTIDEM_design_remix/commit/b55eabc)
- I12 sits at Z 48.0, not 47.8, so S13 has 0.9 mm below its tip and 3.1 mm of thread. The thumbscrew recess is Ø6.0, not Ø5.8.
- S1–S5 figures are given with the cover screwed down: 0.2 mm below the tip and 3.8 mm of thread.

### Changed

- The hardware guide is rebuilt from a source in `docs/hardware-map/`, and its fitting order and the README's now include the counter gears. Figure 8 is redrawn from the current counter face.
- The README documents the cover's locating boss, the two-colour counter face and the flocking templates.

## [2.0.0] - 2026-09-24

The counter gear train is reworked so it turns freely with the cover screwed down. The body, the cover and the counter gears change together, so reprint them as a set.

**Reprint:** your body (`body-solid`, or `body-top` for the two-piece body), `cover`, `ratchet-coupling-gear`, `counter-coupling-gear`, `counter-idler-1`, `counter-idler-2`, `counter-gear` and `counter-face` (or `counter-face-two-colour`).

### Changed

- The cover sits 0.1 mm lower than drawn once it is screwed down. Every gear now keeps at least 0.3 mm of end float with the cover seated. The changes are higher pocket ceilings and underside reliefs in the cover, a relief under the dial sweep, bores through each idler, trimmed faces where gears stack, and a counter face bore that centres the dial wheel. [`a5eedc9`](https://github.com/acornelissen/Infidex_176_v_IDENTIDEM_design_remix/commit/a5eedc9)
- Deeper tooth engagement: the contact ratio rises from 1.22 to 1.32, and the backlash per mesh drops from 0.25 to 0.20 mm. [`db5c098`](https://github.com/acornelissen/Infidex_176_v_IDENTIDEM_design_remix/commit/db5c098), [`a5eedc9`](https://github.com/acornelissen/Infidex_176_v_IDENTIDEM_design_remix/commit/a5eedc9)
- A 25 mm boss on the body around the dial locates the cover in a 25.2 mm recess. [`390df7f`](https://github.com/acornelissen/Infidex_176_v_IDENTIDEM_design_remix/commit/390df7f)
- Idler pins: idler 2 turns on a single 3.2 mm pin in a 3.6 mm bore. The idler 3 pin stops level with the body's top face, so `body-top` prints flat. [`390df7f`](https://github.com/acornelissen/Infidex_176_v_IDENTIDEM_design_remix/commit/390df7f), [`91efaf5`](https://github.com/acornelissen/Infidex_176_v_IDENTIDEM_design_remix/commit/91efaf5), [`305fd5e`](https://github.com/acornelissen/Infidex_176_v_IDENTIDEM_design_remix/commit/305fd5e)
- Larger frame markers, from 0.5 x 0.8 mm up to 0.9 x 1.7 mm and 1.3 x 1.9 mm beside the numbers. Markers and numbers are now 0.4 mm deep, so they survive first-layer squish. [`4411970`](https://github.com/acornelissen/Infidex_176_v_IDENTIDEM_design_remix/commit/4411970)

### Added

- `counter-face-two-colour.3mf`, a flush inlay for printing the markers in a second filament. [`4411970`](https://github.com/acornelissen/Infidex_176_v_IDENTIDEM_design_remix/commit/4411970)
- The STEP includes the counter face inlay. [`390df7f`](https://github.com/acornelissen/Infidex_176_v_IDENTIDEM_design_remix/commit/390df7f)
- Counter-train generator: a contact ratio check, plus face heights, stepped bores and a tooth phase for every gear, with an axial clash check. Its defaults rebuild the gears in the main model. [`db5c098`](https://github.com/acornelissen/Infidex_176_v_IDENTIDEM_design_remix/commit/db5c098), [`c35d43b`](https://github.com/acornelissen/Infidex_176_v_IDENTIDEM_design_remix/commit/c35d43b), [`74720a9`](https://github.com/acornelissen/Infidex_176_v_IDENTIDEM_design_remix/commit/74720a9)

### Fixed

- A non-manifold edge under the chamber rear wall in `body-solid` and `body-bottom`, carried since 1.0.0. Nothing on the outside changes, and both meshes are now watertight. You don't need to reprint `body-bottom` for this. [`61afe50`](https://github.com/acornelissen/Infidex_176_v_IDENTIDEM_design_remix/commit/61afe50)

## [1.1.0] - 2026-09-22

**Reprint:** nothing.

### Added

- Flocking templates for the light chamber: a full-size A4 PDF and per-piece DXF outlines, sized for both bodies. [`66a04ff`](https://github.com/acornelissen/Infidex_176_v_IDENTIDEM_design_remix/commit/66a04ff)
- A pressure plate piece in the flocking templates. [`15b3fc9`](https://github.com/acornelissen/Infidex_176_v_IDENTIDEM_design_remix/commit/15b3fc9)

## [1.0.1] - 2026-09-21

**Reprint:** `cover`. Also `sprocket` and `ratchet-coupling-gear` if you printed them from the 1.0.0 3MFs.

### Fixed

- Tighter tolerances on the gear train cover. [`0768d04`](https://github.com/acornelissen/Infidex_176_v_IDENTIDEM_design_remix/commit/0768d04)
- `sprocket` and `ratchet-coupling-gear` 3MFs re-exported from the current CAD. The sprocket gains its through-all Ø3.2 hole for the I14 insert, and the ratchet-coupling-gear's Ø4 bore is 9.0 mm deep instead of 7.0 mm. [`67ad28a`](https://github.com/acornelissen/Infidex_176_v_IDENTIDEM_design_remix/commit/67ad28a)

### Changed

- The README points at the original assembly guide and the upstream lens mount options. [`c6bfee0`](https://github.com/acornelissen/Infidex_176_v_IDENTIDEM_design_remix/commit/c6bfee0)

## [1.0.0] - 2026-09-18

First release of the remix.

### Added

- Remixed camera CAD (Fusion and STEP) and the print-ready Bambu project. [`795b37c`](https://github.com/acornelissen/Infidex_176_v_IDENTIDEM_design_remix/commit/795b37c)
- One 3MF per part. [`1bbc604`](https://github.com/acornelissen/Infidex_176_v_IDENTIDEM_design_remix/commit/1bbc604)
- Parametric counter-train Fusion script with tests. [`35278fa`](https://github.com/acornelissen/Infidex_176_v_IDENTIDEM_design_remix/commit/35278fa)
- Hardware placement guide and section drawings. [`142e6cd`](https://github.com/acornelissen/Infidex_176_v_IDENTIDEM_design_remix/commit/142e6cd)
- README with parts, hardware and the full assembly procedure. [`96984c0`](https://github.com/acornelissen/Infidex_176_v_IDENTIDEM_design_remix/commit/96984c0), [`238e9ea`](https://github.com/acornelissen/Infidex_176_v_IDENTIDEM_design_remix/commit/238e9ea)
- Attribution notice for the original project. [`f6cef08`](https://github.com/acornelissen/Infidex_176_v_IDENTIDEM_design_remix/commit/f6cef08)

[Unreleased]: https://github.com/acornelissen/Infidex_176_v_IDENTIDEM_design_remix/compare/v2.2.0...HEAD
[2.2.0]: https://github.com/acornelissen/Infidex_176_v_IDENTIDEM_design_remix/compare/v2.1.0...v2.2.0
[2.1.0]: https://github.com/acornelissen/Infidex_176_v_IDENTIDEM_design_remix/compare/v2.0.2...v2.1.0
[2.0.2]: https://github.com/acornelissen/Infidex_176_v_IDENTIDEM_design_remix/compare/v2.0.1...v2.0.2
[2.0.1]: https://github.com/acornelissen/Infidex_176_v_IDENTIDEM_design_remix/compare/v2.0.0...v2.0.1
[2.0.0]: https://github.com/acornelissen/Infidex_176_v_IDENTIDEM_design_remix/compare/v1.1.0...v2.0.0
[1.1.0]: https://github.com/acornelissen/Infidex_176_v_IDENTIDEM_design_remix/compare/v1.0.1...v1.1.0
[1.0.1]: https://github.com/acornelissen/Infidex_176_v_IDENTIDEM_design_remix/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/acornelissen/Infidex_176_v_IDENTIDEM_design_remix/releases/tag/v1.0.0
