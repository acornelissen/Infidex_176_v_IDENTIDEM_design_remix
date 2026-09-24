# Changelog

Every release lists what changed, the commits behind it and which parts to reprint.

## Versioning

Versions follow [Semantic Versioning](https://semver.org), read for printed parts:

- **Major**: parts from the previous release no longer fit or mesh with the new ones, so a set of parts has to be reprinted together, or the bought hardware changes.
- **Minor**: new parts, variants, templates or tools. Existing builds are unaffected.
- **Patch**: fixes you pick up by reprinting only the listed parts, each on its own, plus re-exports, mesh repairs and documentation.

Releases are tagged `vX.Y.Z`. Changes that only touch the documentation go into the next release rather than getting a release of their own.

## [Unreleased]

Documentation only. **Reprint:** nothing.

### Changed

- The hardware guide is rebuilt from a source in `docs/hardware-map/`, and its fitting order and the README's now include the counter gears. Figure 8 is redrawn from the current counter face.
- The README documents the cover's locating boss, the two-colour counter face and the flocking templates.

### Fixed

- I12 sits at Z 48.0, not 47.8, so S13 has 0.9 mm below its tip and 3.1 mm of thread. The thumbscrew recess is Ø6.0, not Ø5.8.
- S1–S5 figures are given with the cover screwed down: 0.2 mm below the tip and 3.8 mm of thread.

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

[Unreleased]: https://github.com/acornelissen/Infidex_176_v_IDENTIDEM_design_remix/compare/v2.0.0...HEAD
[2.0.0]: https://github.com/acornelissen/Infidex_176_v_IDENTIDEM_design_remix/compare/v1.1.0...v2.0.0
[1.1.0]: https://github.com/acornelissen/Infidex_176_v_IDENTIDEM_design_remix/compare/v1.0.1...v1.1.0
[1.0.1]: https://github.com/acornelissen/Infidex_176_v_IDENTIDEM_design_remix/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/acornelissen/Infidex_176_v_IDENTIDEM_design_remix/releases/tag/v1.0.0
