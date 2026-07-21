# DogPi enclosure CAD

This directory contains the printable enclosure for DogPi. The enclosure is
designed around a **Raspberry Pi Zero 2 W**, a **1.3-inch SH1106 OLED**, and
three **12 mm momentary panel-mount buttons** arranged vertically on the angled
control deck. Dimensions in the OpenSCAD source are in millimetres.

## Files

| File | Description |
| --- | --- |
| `dogpi.scad` | Parametric OpenSCAD source for the base, lid, cutouts, and markings. |
| `dogpi_base.stl` | Ready-to-slice base. Its mesh bounds are approximately 61.78 × 75 × 25 mm, including the snap catches. |
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
- 8 × M2.5 nuts
- 4 × M2.5 washers, 1 mm thick, one at each Pi mounting point

Four screw-and-nut sets mount the Raspberry Pi and four mount the OLED. The
1 mm washers provide the intended spacing for the Pi board. Confirm that an
8 mm screw provides adequate thread engagement with your actual PCB, washer,
and nut stack before final assembly.

## Important OpenSCAD parameters

Commonly adjusted values are near the top of `dogpi.scad`.

| Parameter | Default | Purpose |
| --- | ---: | --- |
| `$fn` | `48` | Curved-feature resolution. |
| `show_base`, `show_lid` | `true`, `true` | Select which parts are rendered or exported. |
| `show_assembled` | `false` | Switch between assembled and exploded preview. |
| `explode_gap` | `16` | Preview separation between the base and lid. |
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

Advanced snap-fit controls include `tab_t`, `tab_w`, `tab_gap`, `barb_depth`,
`barb_h`, `catch_t`, `catch_h`, and `stop_lip_inset`. Change these in small
increments when tuning.

## Rendering and exporting

Open `dogpi.scad` in OpenSCAD and use a full render (`F6`) before exporting.
Export only one part at a time:

- Base: set `show_base = true;` and `show_lid = false;`.
- Lid: set `show_base = false;` and `show_lid = true;`.

The committed lid STL retains the exploded-preview translation and therefore
has a minimum Z coordinate of 41 mm. Use the slicer's **drop to bed/place on
face** command before slicing.

## Known fit and tolerance limitations

- Clearances are tuned parametrically, not guaranteed for every printer,
  material, layer height, or shrink rate. Print a small fit test or be prepared
  to adjust `fit` in gradual steps.
- The snap tabs and catches are sensitive to material stiffness and print
  orientation.
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
