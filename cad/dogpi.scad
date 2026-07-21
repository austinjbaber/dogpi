////\\/\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//
// Author: Austin Baber (github.com/austinjbaber)
// DogPi enclosure v7 - vertical buttons, fixed ports
// Raspberry Pi Zero 2 W + 1.3" SH1106 OLED + 3x 12mm momentary buttons
//\\/\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//

$fn = 48;

// -----------------------------------------------------------------------------
// View controls
// -----------------------------------------------------------------------------
show_base = true;
show_lid = true;
show_assembled = false;   // false = exploded view
explode_gap = 16;

// -----------------------------------------------------------------------------
// Printer / fit tuning
// -----------------------------------------------------------------------------
fit = 0.30;                // general lid-to-base clearance
button_hole_clear = 0.20;  // extra diameter added to 12 mm button holes
oled_mount_hole_clear = 0.25; // extra diameter added to OLED M2.5 mounting holes

//\\/\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//
// General case params
//\\/\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//
wall = 2.4;      // base wall thickness
floor_t = 3.8;   // base floor thickness
face_t = 3.0;    // lid/control-deck shell thickness
skirt_t = 1.8;   // lid skirt wall thickness
skirt_h = 8;   // how far the lid overlaps down over the base
corner_r = 4.0;  // outside corner radius

base_x = 60;    // overall base width  (left/right)
base_y = 75;     // overall base depth  (front/back)
base_h = 25;   // overall base height

lid_inner_x = base_x + 2*fit;
lid_inner_y = base_y + 2*fit;
lid_x = lid_inner_x + 2*skirt_t;
lid_y = lid_inner_y + 2*skirt_t;

// Snap details
tab_t = 1.2;
tab_w = 10.0;
tab_gap = 1.2;
barb_depth = 0.8;
barb_h = 1.2;
barb_z = 1.8;

catch_w = 9.0;
catch_t = 0.9;
catch_h = 1.1;
catch_z = (base_h - skirt_h) + barb_z;

//\\/\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//
// Lid geometry / params
//\\/\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//

// -----------------------------------------------------------------------------
// Angled control deck geometry
// -----------------------------------------------------------------------------
panel_angle = 45;               // display/button plane angle
rear_deck_d = 12;             // flat rear band after slope ends
roof_low_top_z = skirt_h + 4.0; // top height at front edge of lid

// Slope starts immediately at the front edge
panel_rear_y = lid_y/2 - rear_deck_d;
panel_run_y = panel_rear_y + lid_y/2;

roof_high_top_z = roof_low_top_z + tan(panel_angle) * panel_run_y;

// Midpoint of the sloped section, used by panel_frame()
panel_mid_y = (-lid_y/2 + panel_rear_y) / 2;
panel_mid_z = (roof_low_top_z + roof_high_top_z) / 2;

// -----------------------------------------------------------------------------
// Raspberry Pi Zero 2 W
// -----------------------------------------------------------------------------
pi_x = 65.0;
pi_y = 30.0;
pi_hole_inset = 3.5;
pi_hole_dx = 58.0;
pi_hole_dy = 23.0;

pi_mount_clear_d = 2.8;

pi_counterbore_d = 5.0;   // counterbore diameter
pi_counterbore_h = 3.0;   // counterbore depth

pi_right_gap = 1;
pi_rear_gap = 2.5;
// Pi is rotated 90 degrees so ports face the right wall.
pi_origin_x =  base_x/2 - wall - pi_right_gap - pi_y;
pi_origin_y =  base_y/2 - wall - pi_rear_gap - pi_x;

// -----------------------------------------------------------------------------
// Port tunnel params (based on Pi drawing X positions)
// -----------------------------------------------------------------------------
side_tunnel_x = base_x/2 - wall - 0.6;
side_tunnel_depth = wall + 1.2;
side_port_clear = 0.50;
side_port_z = 5.1;

// Connector widths
mini_hdmi_w = 12.1;
mini_hdmi_h = 5.5;

micro_usb_w = 8.1;
micro_usb_h = 4.5;

// Board-view connector center X positions (from the Pi drawing/blueprint)
mini_hdmi_c = 12.4;
usb1_c      = 41.4;
usb2_c      = 54.0;

// -----------------------------------------------------------------------------
// OLED module
// -----------------------------------------------------------------------------
oled_hole_d = 2.5 + oled_mount_hole_clear;
oled_hole_dx = 30.4;
oled_hole_dy = 28.5;

// Target physical window opening in lid
oled_window_x = 34.0;
oled_window_y = 18.0;

oled_window_center_y = 11.25 - oled_window_y/2;  // = 2.25
oled_window_offset_x = 0.0;

// OLED centered on the angled deck
// In local panel coordinates: x is left/right across case, y is up/down along the deck.
oled_lx = -10;
oled_ly = 0;

// -----------------------------------------------------------------------------
// 12 mm panel buttons
// -----------------------------------------------------------------------------
button_panel_hole = 12.0 + button_hole_clear;

// single vertical button column to the right of the OLED
btn_col_x  = 19;
btn_step_y = 16.0;   // center-to-center spacing from middle to top/bottom

btn_up_y   =  btn_step_y;
btn_sel_y  =  0;
btn_down_y = -btn_step_y;

// shared list so placement only lives in one place
button_positions = [
    [btn_col_x, btn_up_y],
    [btn_col_x, btn_sel_y],
    [btn_col_x, btn_down_y]
];

// -----------------------------------------------------------------------------
// Lid branding / button markers / pill recess
// -----------------------------------------------------------------------------

// font sampler: change this index and re-render
// if one doesn't exist on your system, try another
font_options = [
    "Arial:style=Bold",
    "Verdana:style=Bold",
    "Trebuchet MS:style=Bold",
    "Segoe UI:style=Bold",
    "Bahnschrift:style=Bold",
    "Liberation Sans:style=Bold",
    "DejaVu Sans:style=Bold",
    "Helvetica:style=Bold",
    "Lucida Console:style=Bold",
    "Consolas:style=Regular",
    "Consolas:style=Bold"
];
font_i = 9;
brand_font = font_options[min(max(font_i, 0), len(font_options)-1)];

brand_text = "dogpi";
brand_size = 7;
brand_spacing = 1.0;
brand_depth = 0.40;

// local panel coordinates
// x = left/right across lid
// y = along the sloped deck
brand_x = -10;
brand_y = btn_up_y + 15.0;   // above select button

tri_enable = true;
tri_depth = 0.35;
tri_w = 4.2;
tri_h = 3.3;
tri_x = btn_col_x;   // aligned with button column

under_oled_recess_enable = true;
under_oled_recess_depth  = 0.35;
under_oled_recess_x      = oled_lx;
under_oled_recess_y      = oled_ly - oled_hole_dy/2;
under_oled_recess_w      = 22.0;
under_oled_recess_h      = 4.0;
under_oled_recess_r      = 2;

// -----------------------------------------------------------------------------
// Inner stop lip (3-sided)
// -----------------------------------------------------------------------------
stop_lip_inset  = 0.9;   // how far the lip projects inward
stop_lip_h      = 0.7;   // lip thickness upward from z = skirt_h

//\\/\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//
// Helpers
//\\/\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//

module lid_inner_stop_lip_3sided() {
    zc = skirt_h + stop_lip_h/2 + 1; // extra lift so stop lip reaches the inner diagonal corner

    // rear lip
    translate([0, lid_inner_y/2 - stop_lip_inset/2, zc])
        cube([lid_inner_x, stop_lip_inset, stop_lip_h], center=true);

    // left/right lips
    for (sx = [-1, 1])
        translate([sx*(lid_inner_x/2 - stop_lip_inset/2), 0, zc])
            cube([stop_lip_inset, lid_inner_y, stop_lip_h], center=true);
}
module panel_recess(depth=0.6) {
    // Cuts downward into the sloped panel from the outer surface
    translate([0, 0, -depth])
        linear_extrude(height=depth + 0.04, center=false)
            children();
}

module marker_triangle_2d(w=4.8, h=3.8, up=true) {
    polygon(points =
        up
        ? [[-w/2, -h/2], [ w/2, -h/2], [0, h/2]]
        : [[-w/2,  h/2], [ w/2,  h/2], [0,-h/2]]
    );
}

module lid_markings() {
    panel_frame() {
        translate([brand_x, brand_y, 0])
            panel_recess(brand_depth)
                text(
                    brand_text,
                    size=brand_size,
                    font=brand_font,
                    halign="center",
                    valign="center",
                    spacing=brand_spacing
                );

        if (tri_enable) {
            translate([tri_x, btn_up_y + 12, 0])
                panel_recess(tri_depth)
                    marker_triangle_2d(tri_w, tri_h, true);

            translate([tri_x, btn_down_y - 12, 0])
                panel_recess(tri_depth)
                    marker_triangle_2d(tri_w, tri_h, false);
        }
        if (under_oled_recess_enable)
            translate([under_oled_recess_x, under_oled_recess_y, 0])
                panel_recess(under_oled_recess_depth)
                    rounded_rect_2d(
                        [under_oled_recess_w, under_oled_recess_h],
                        under_oled_recess_r
                    );
    }
}
module side_port_tunnel_center(x_center_from_pi_left, z0, w, h) {
    // Preserve connector left-to-right order when viewed on the right wall.
    y_center_side = pi_origin_y + x_center_from_pi_left;

    translate([
        side_tunnel_x,
        y_center_side - w/2 - side_port_clear,
        z0
    ])
        cube([
            side_tunnel_depth,
            w + 2*side_port_clear,
            h
        ], center=false);
}

module rounded_rect_2d(sz=[10,10], r=2) {
    w = sz[0];
    h = sz[1];
    rr = min(r, min(w, h)/2 - 0.01);
    hull() {
        for (sx = [-1, 1])
            for (sy = [-1, 1])
                translate([sx*(w/2 - rr), sy*(h/2 - rr)]) circle(r=rr);
    }
}

module rounded_prism(sz=[10,10], h=2, r=2) {
    linear_extrude(height=h)
        rounded_rect_2d(sz, r);
}

module xy_hole_grid(cx=0, cy=0, dx=10, dy=10) {
    for (sx=[-1,1])
        for (sy=[-1,1])
            translate([cx + sx*dx/2, cy + sy*dy/2, 0]) children();
}

// Profile is specified in [y,z] points and extruded across X.
module yz_profile_extrude(profile_pts, width) {
    rotate([90,0,90])
        linear_extrude(height=width, center=true, convexity=10)
            polygon(points=profile_pts);
}

// Local coordinate system for the angled control deck.
// local x = left/right across case
// local y = along the sloped panel
// local z = panel normal
module panel_frame() {
    translate([0, panel_mid_y, panel_mid_z])
        rotate([panel_angle, 0, 0])
            children();
}


//\\/\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//
// Base
//\\/\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//
module base_part() {
    difference() {
        union() {
            rounded_prism([base_x, base_y], base_h, corner_r);

            for (side=[-1,1]) {
                translate([
                    side*(base_x/2 + catch_t/2 - 0.01),
                    0,
                    catch_z + catch_h/2
                ])
                cube([catch_t, catch_w, catch_h], center=true);
            }
        }

        translate([0, 0, floor_t])
            rounded_prism([base_x - 2*wall, base_y - 2*wall], base_h, max(0.1, corner_r - wall));


        for (sx=[0, pi_hole_dx])
            for (sy=[0, pi_hole_dy]) {
                px = pi_origin_x + pi_hole_inset + sy;
                py = pi_origin_y + (pi_x - pi_hole_inset - sx);

                // through-hole for M2.5 screw
                translate([px, py, -0.01])
                    cylinder(h=floor_t + 0.02, d=pi_mount_clear_d);

                // counterbore from the exterior bottom
                translate([px, py, -0.01])
                    cylinder(h=pi_counterbore_h + 0.02, d=pi_counterbore_d);
    }

        // Right-side port tunnels: mini HDMI + 2x micro USB
        side_port_tunnel_center(mini_hdmi_c, side_port_z, mini_hdmi_w, mini_hdmi_h);
        side_port_tunnel_center(usb1_c,      side_port_z, micro_usb_w, micro_usb_h);
        side_port_tunnel_center(usb2_c,      side_port_z, micro_usb_w, micro_usb_h);

    }
}

//\\/\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//
// Lid
//\\/\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//
outer_profile = [
    [-lid_y/2, 0],
    [ lid_y/2, 0],
    [ lid_y/2, roof_high_top_z],
    [ panel_rear_y, roof_high_top_z],
    [-lid_y/2, roof_low_top_z]
];

inner_profile = [
    [-lid_inner_y/2, -0.01],
    [ lid_inner_y/2, -0.01],
    [ lid_inner_y/2, roof_high_top_z - face_t],
    [ panel_rear_y - skirt_t, roof_high_top_z - face_t],
    [-lid_inner_y/2, roof_low_top_z - face_t]
];

module lid_tab_slots() {
    for (side=[-1,1])
        let (x0 = side*(lid_inner_x/2 + skirt_t/2))
            for (yy=[-(tab_w + tab_gap)/2, +(tab_w + tab_gap)/2])
                translate([x0, yy, skirt_h/2])
                    cube([skirt_t + 0.8, tab_gap, skirt_h + 0.2], center=true);
}

module lid_tabs() {
    for (side=[-1,1])
        let (x_center = side*(lid_inner_x/2 + tab_t/2))
            union() {
                translate([x_center, 0, (skirt_h + 0.01)/2])
                    cube([tab_t, tab_w, skirt_h + 0.01], center=true);

                translate([
                    x_center + side*(barb_depth/2),
                    0,
                    barb_z + barb_h/2
                ])
                    cube([barb_depth, tab_w - 1.5, barb_h], center=true);
            }
}

module lid_outer_body() {
    yz_profile_extrude(outer_profile, lid_x);
}

module lid_inner_cavity() {
    yz_profile_extrude(inner_profile, lid_inner_x);
}

module lid_part() {
    union() {
        difference() {
            union() {
                lid_outer_body();
                lid_tabs();
            }

            // Main hollow underside
            lid_inner_cavity();

            // OLED window through the sloped deck
            panel_frame()
                translate([
                    oled_lx + oled_window_offset_x,
                    oled_ly + oled_window_center_y,
                    0
                ])
                    cube([oled_window_x, oled_window_y, 30], center=true);

            // OLED mounting holes through the sloped deck
            panel_frame()
                xy_hole_grid(oled_lx, oled_ly, oled_hole_dx, oled_hole_dy)
                    cylinder(h=30, d=oled_hole_d, center=true);

            // Button holes through the same sloped deck plane
            panel_frame()
                for (p = button_positions)
                    translate([p[0], p[1], 0])
                        cylinder(h=30, d=button_panel_hole, center=true);

            lid_markings();
            lid_tab_slots();
        }

        lid_inner_stop_lip_3sided();
    }
}


//\\/\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//
// Scene
//\\/\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//

lid_color  = "silver";
base_color = "black";

module scene() {
    if (show_base) {
        color(base_color)
            base_part();
    }

    if (show_lid) {
        lid_z = show_assembled ? (base_h - skirt_h) : (base_h + explode_gap);
        color(lid_color)
            translate([0, 0, lid_z]) lid_part();
    }
}

scene();
