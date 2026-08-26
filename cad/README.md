# DogPi enclosure CAD

This directory contains the printable enclosure for DogPi. The enclosure is
designed around a **Raspberry Pi Zero 2 W**, a **1.3-inch SH1106 OLED**, and
three **12 mm momentary panel-mount buttons** arranged vertically on the angled
control deck. Dimensions in the OpenSCAD source are in millimetres.

## Files

| File | Description |
| --- | --- |
| `dogpi.scad` | Parametric OpenSCAD source for the base, lid, cutouts, and markings. |
| `dogpi_base.stl` | Ready-to-slice base. Its mesh bounds are 60 × 75 × 25 mm. |
| `dogpi_lid.stl` | Ready-to-slice lid. Its mesh bounds are approximately 64.2 × 79.2 × 79.2 mm. |

## Intended hardware

### Raspberry Pi

The model uses the Raspberry Pi Zero 2 W board outline and mounting pattern:

| Feature | Modelled value |
| --- | ---: |
| PCB outline | 65 × 30 mm |
| Mounting-hole spacing | 58 × 23 mm |
| Hole inset from PCB edges | 3.5 mm |
| Printed clearance-hole diameter | 2.8 mm |
| Exterior screw-head counterbore | 5 mm diameter × 3 mm deep |

The Pi is rotated 90 degrees inside the base so the mini-HDMI and two micro-USB
connectors face the right wall. The port cutouts are based on connector center
positions from the Pi drawing.

### OLED

The lid is intended for a 1.3-inch, 128 × 64 SH1106 I2C OLED module with this
mounting geometry:

| Feature | Modelled value |
| --- | ---: |
| Visible-window opening | 34 × 18 mm |
| Mounting-hole spacing | 30.4 × 28.5 mm |
| Printed mounting-hole diameter | 2.75 mm |

The window is intentionally smaller than the module PCB. Compare these values
with the drawing or a physical measurement of your module before printing;
boards sold as “1.3-inch SH1106” may not all use the same PCB or hole pattern.

### Buttons

The control deck accepts three nominal 12 mm panel-mount momentary buttons:

| Feature | Modelled value |
| --- | ---: |
| Printed panel-hole diameter | 12.2 mm |
| Vertical centre-to-centre spacing | 16 mm |
| Arrangement | UP / SELECT / DOWN |

Check the diameter of the threaded barrel rather than the button-cap diameter.

### Fasteners

The complete enclosure uses:

- 8 × M2.5 × 8 mm screws
- 2 × M2.5 × 6 mm screws for the lid closure
- 10 × M2.5 nuts
- 4 × M2.5 washers, 1 mm thick, one at each Pi mounting point

Four screw-and-nut sets mount the Raspberry Pi and four mount the OLED. The
1 mm washers provide the intended spacing for the Pi board. The remaining two
nuts drop into the rear closure pockets. An M2.5 × 8 mm screw can be used for
the closure if that is what the standoff kit provides, but it extends about
2.4 mm beyond the captive nut and roughly 1.25 mm into the wiring cavity. A
6 mm screw avoids most of that projection. Confirm all hardware dimensions and
thread engagement against the actual kit before final assembly.

### Lid closure and assembly

The former side snaps have been replaced with two rigid front tuck tabs and two
rear captive-nut screws. The front in these instructions is the low edge below
the angled control deck; the tall vertical wall is the rear.

1. Drop one M2.5 nut into each open slot in the two rear base bosses.
2. Hold the rear of the lid slightly raised and insert both front tabs into the
   matching blind receiver slots.
3. Pivot the rear of the lid down. Around the middle of the motion, allow the
   tabs to slide about 0.3 mm deeper into their pockets so the rear bearing pads
   pass the base rim, then let the lid settle forward again as it closes.
   Do not force the lid as a fixed hinge. Continue until the three-sided internal
   stop lip rests on the base rim.
4. Insert an M2.5 screw through each rear lid hole and tighten it into the
   captive nut. The screw heads remain externally accessible and slightly proud.

The closure screws use the same M2.5 hardware family as the Pi mounts. Their
printed clearance holes are 3.0 mm rather than the Pi holes' 2.8 mm because the
rear screws pass horizontally through two printed walls and need reliable FDM
clearance. The rear holes are not counterbored.

Each default front tab is 11 mm wide, and each receiver is 11.5 mm wide for
0.25 mm clearance at either side. The two independent receivers tolerate minor
front-wall bowing better than one long mating feature.

## Important OpenSCAD parameters

Commonly adjusted values are near the top of `dogpi.scad`.

| Parameter | Default | Purpose |
| --- | ---: | --- |
| `$fn` | `48` | Curved-feature resolution. |
| `show_base`, `show_lid` | `true`, `true` | Select which parts are rendered or exported. |
| `show_assembled` | `false` | Switch between assembled and exploded preview. |
| `explode_gap` | `16` | Preview separation between the base and lid. |
| `render_target` | `0` | CLI/export selector described below. |
| `fit` | `0.30` | Lid clearance per side; the lid cavity grows by `2 * fit` in X and Y. |
| `button_hole_clear` | `0.20` | Extra diameter added to each nominal 12 mm button hole. |
| `oled_mount_hole_clear` | `0.25` | Extra diameter added to each nominal 2.5 mm OLED hole. |
| `wall` | `2.4` | Base wall thickness. |
| `floor_t` | `3.8` | Base floor thickness. |
| `face_t` | `3.0` | Lid/control-deck shell thickness. |
| `skirt_t`, `skirt_h` | `1.8`, `8` | Lid skirt wall thickness and overlap. |
| `panel_angle` | `45` | Control-deck angle in degrees. |
| `pi_mount_clear_d` | `2.8` | Pi mounting-hole diameter. |
| `side_port_clear` | `0.50` | Clearance added around the side connector openings. |
| `oled_window_x`, `oled_window_y` | `34`, `18` | OLED viewing-window dimensions. |
| `oled_hole_dx`, `oled_hole_dy` | `30.4`, `28.5` | OLED mounting-hole centre spacing. |
| `btn_col_x` | `19` | Horizontal location of the button column. |
| `btn_step_y` | `16` | Button center spacing along the sloped deck. |
| `font_i` | `9` | Selects the font used for the recessed `dogpi` marking. |

The closure can be tuned with `front_tab_w`, `front_tab_depth`, `front_tab_t`,
`front_tab_xy_clear`, `front_tab_z_clear`, `front_receiver_depth`,
`pivot_preview_slide`, `closure_screw_d`, `closure_nut_af`, `closure_nut_t`, and
`closure_nut_clear`. Receiver depth, tab depth, and slide travel are coupled:
keep each receiver deeper than the tab projection by at least the slide travel
plus the desired back clearance. Measure the nuts in the intended hardware kit
before changing their pocket dimensions. Change tab clearances in small
increments and test both tabs together.

## Rendering and exporting

Open `dogpi.scad` in OpenSCAD and use a full render (`F6`) before exporting.
For an interactive preview, leave `render_target = 0` and use the existing
`show_base`, `show_lid`, and `show_assembled` controls. For deterministic CLI
rendering and exports, set `render_target` to one of these values:

- `1`: base at its manufacturing origin
- `2`: lid at its manufacturing origin
- `3`: closed assembly
- `4`: closure section with representative M2.5 hardware
- `5`: closed-assembly interference diagnostic
- `6`: front-tab pivot-and-slide preview at the selected path angle
- `7`: interference diagnostic at the same selected path angle

Targets `5` and `7` should be empty; any visible solid represents an overlap.
Target `7` defaults to the middle of the assembly path (`3.75` degrees). For a
full path check, override `pivot_preview_angle` and repeat target `7` at intervals
from `0` through `pivot_path_max_angle` (`6.5` degrees). OpenSCAD's "current top
level object is empty" message is the passing result for these diagnostics.

The committed base and lid STLs are exported from targets `1` and `2`. Both have
a minimum Z coordinate of 0 and can be imported directly into a slicer.

## Known fit and tolerance limitations

- Clearances are tuned parametrically, not guaranteed for every printer,
  material, layer height, or shrink rate. Print a small fit test or be prepared
  to adjust `fit` in gradual steps.
- The front tabs are rigid locating features, not flexing snaps. PETG can add
  toughness and impact tolerance, but it does not remove the need to tune tab
  and nut-pocket clearances for a particular printer. PLA can also be used.
- The default captive-nut pockets assume a 4.8 mm across-flats, 2.0 mm thick
  M2.5 nut with 0.25 mm modelled clearance. Supplied nuts vary; measure them.
- The OLED opening and 30.4 × 28.5 mm hole pattern fit only matching modules.
  Connector position, PCB outline, and glass placement vary among SH1106 boards.
- The 12.2 mm button holes assume a nominal 12 mm mounting barrel. Panel buttons
  with keyed bodies or unusually thick retaining nuts may not fit.
- Side access is provided for mini-HDMI and two micro-USB connectors. Oversized
  cable shells may need more than the default 0.5 mm port clearance.
- There is no external microSD-card opening in the current model.
- The branding font depends on fonts installed on the computer rendering the
  SCAD file. If the selected font is unavailable, choose another `font_i` and
  verify the resulting text before export.
- The supplied STLs contain the current parameter values only. Changing the
  SCAD source does not update them; re-render and re-export both affected parts.

Dry-fit the Pi, OLED, buttons, and all cables before tightening the hardware.
Avoid overtightening against both printed plastic and the PCBs.
