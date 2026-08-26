////\\/\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//
// Author: Austin Baber (github.com/austinjbaber)
// DogPi enclosure v8 - front tuck-tabs and rear screw closure
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

// -----------------------------------------------------------------------------
// Serviceable lid closure
// -----------------------------------------------------------------------------
// Two rigid tongues on the low/front lid skirt enter matching receivers in the
// base. The rear then pivots down and is retained by two horizontal M2.5 screws
// threaded into drop-in captive nuts.
front_tab_x = 17.0;            // left/right tab centers
front_tab_w = 11.0;
front_tab_depth = 2.1;         // projection from the lid skirt into the base
front_tab_t = 1.6;
front_tab_lid_z = 1.4;         // low placement leaves room for the lid to pivot
front_tab_root_overlap = 0.40;
front_tab_nose_bevel = 0.45;

front_tab_xy_clear = 0.25;     // receiver clearance at each tab side
front_tab_z_clear = 0.60;      // total vertical receiver clearance
front_receiver_depth = 2.4;    // blind pocket depth permits pivot-and-slide travel
front_receiver_boss_w = 14.5;
front_receiver_boss_d = 1.5;
front_receiver_boss_h = 5.0;
front_skirt_bevel = 1.00;      // lower-inner clearance during pivot-and-slide

closure_screw_x = 18.0;        // left/right screw centers
closure_screw_d = 3.0;         // horizontal M2.5 clearance for FDM printing
closure_screw_z = base_h - skirt_h/2; // base/global Z = 21 mm
closure_screw_lid_z = closure_screw_z - (base_h - skirt_h);

// M2.5 nut dimensions
closure_nut_af = 4.8;          // width across flats
closure_nut_t = 2.0;
closure_nut_clear = 0.25;
closure_nut_af_clear = closure_nut_af + closure_nut_clear;
closure_nut_t_clear = closure_nut_t + closure_nut_clear;
closure_nut_corner_d = closure_nut_af / cos(30);
closure_nut_y = base_y/2 - 2.5;

closure_boss_wall = 1.4;
closure_boss_w = closure_nut_af_clear + 2*closure_boss_wall;
closure_boss_d = closure_nut_t_clear + 2*1.2;
closure_boss_h = 8.0;

closure_bearing_pad_d = 7.0;
closure_bearing_pad_depth = 0.20;
pivot_path_max_angle = 6.5;
pivot_preview_angle = 3.75;     // middle of the validated assembly path
pivot_preview_slide = 0.27;    // peak temporary +Y travel while lowering rear
interference_test_gap = 0.01; // ignores the intentional stop-lip/rim contact

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

// Connector opening sizes before applying side_port_clear in Y.
mini_hdmi_w = 13.0;
mini_hdmi_h = 7.0;
micro_usb_w = 10.0;
micro_usb_h = 7.5;

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
stop_lip_shell_overlap = 0.15;

//\\/\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//
// Helpers
//\\/\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//

module lid_inner_stop_lip_3sided() {
    // Bottom lands at local Z=skirt_h, or global Z=base_h when assembled.
    zc = skirt_h + stop_lip_h/2;
    lip_t = stop_lip_inset + stop_lip_shell_overlap;

    // rear lip
    translate([
        0,
        lid_inner_y/2 - (stop_lip_inset - stop_lip_shell_overlap)/2,
        zc
    ])
        cube([
            lid_inner_x + 2*stop_lip_shell_overlap,
            lip_t,
            stop_lip_h
        ], center=true);

    // left/right lips
    for (sx = [-1, 1])
        translate([
            sx*(lid_inner_x/2 - (stop_lip_inset - stop_lip_shell_overlap)/2),
            0,
            zc
        ])
            cube([
                lip_t,
                lid_inner_y + 2*stop_lip_shell_overlap,
                stop_lip_h
            ], center=true);
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

// -----------------------------------------------------------------------------
// Closure helpers
// -----------------------------------------------------------------------------
front_tab_global_z = (base_h - skirt_h) + front_tab_lid_z;
front_receiver_w = front_tab_w + 2*front_tab_xy_clear;
front_receiver_h = front_tab_t + front_tab_z_clear;

closure_boss_y_min = base_y/2 - closure_boss_d;
closure_nut_slot_bottom = closure_screw_z - closure_nut_corner_d/2;

module base_front_receiver_bosses() {
    for (x = [-front_tab_x, front_tab_x])
        translate([
            x,
            -base_y/2 + wall + front_receiver_boss_d/2 - 0.10,
            front_tab_global_z
        ])
            cube([
                front_receiver_boss_w,
                front_receiver_boss_d + 0.20,
                front_receiver_boss_h
            ], center=true);
}

module base_front_receiver_slots() {
    for (x = [-front_tab_x, front_tab_x])
        translate([
            x - front_receiver_w/2,
            -base_y/2 - 0.50,
            front_tab_global_z - front_receiver_h/2
        ])
            cube([
                front_receiver_w,
                front_receiver_depth + 0.50,
                front_receiver_h
            ]);
}

module base_rear_closure_bosses() {
    for (x = [-closure_screw_x, closure_screw_x])
        translate([
            x,
            base_y/2 - closure_boss_d/2,
            base_h - closure_boss_h/2
        ])
            cube([closure_boss_w, closure_boss_d, closure_boss_h], center=true);
}

module base_rear_closure_cutouts() {
    for (x = [-closure_screw_x, closure_screw_x]) {
        // Horizontal clearance bore from the rear exterior into the cavity.
        translate([x, base_y/2 + 1, closure_screw_z])
            rotate([90, 0, 0])
                cylinder(
                    h=(base_y/2 + 1) - (closure_boss_y_min - 0.50),
                    d=closure_screw_d,
                    $fn=32
                );

        // Support-free top-loading slot. The nut's vertical points seat at the
        // calculated bottom while its flats are restrained along X.
        translate([
            x - closure_nut_af_clear/2,
            closure_nut_y - closure_nut_t_clear/2,
            closure_nut_slot_bottom
        ])
            cube([
                closure_nut_af_clear,
                closure_nut_t_clear,
                base_h - closure_nut_slot_bottom + 0.20
            ]);
    }
}

module lid_front_tuck_tabs() {
    front_inner_y = -lid_inner_y/2;
    body_end_y = front_inner_y + front_tab_depth - front_tab_nose_bevel;
    tip_y = front_inner_y + front_tab_depth;
    body_start_y = front_inner_y - front_tab_root_overlap;
    body_z0 = front_tab_lid_z - front_tab_t/2;
    nose_t = front_tab_t - 2*front_tab_nose_bevel;

    for (x = [-front_tab_x, front_tab_x]) {
        translate([x - front_tab_w/2, body_start_y, body_z0])
            cube([
                front_tab_w,
                body_end_y - body_start_y + 0.02,
                front_tab_t
            ]);

        hull() {
            translate([x - front_tab_w/2, body_end_y, body_z0])
                cube([front_tab_w, 0.02, front_tab_t]);

            translate([
                x - front_tab_w/2,
                tip_y - 0.02,
                front_tab_lid_z - nose_t/2
            ])
                cube([front_tab_w, 0.02, nose_t]);
        }
    }
}

module lid_front_skirt_pivot_bevel() {
    front_inner_y = -lid_inner_y/2;

    yz_profile_extrude([
        [front_inner_y - front_skirt_bevel, -0.02],
        [front_inner_y + 0.02, -0.02],
        [front_inner_y + 0.02, front_skirt_bevel]
    ], lid_x + 2);
}

module lid_rear_bearing_pads() {
    for (x = [-closure_screw_x, closure_screw_x])
        translate([x, lid_inner_y/2 + 0.01, closure_screw_lid_z])
            rotate([90, 0, 0])
                cylinder(
                    h=closure_bearing_pad_depth + 0.02,
                    d=closure_bearing_pad_d,
                    $fn=36
                );
}

module lid_rear_screw_holes() {
    for (x = [-closure_screw_x, closure_screw_x])
        translate([x, lid_y/2 + 0.50, closure_screw_lid_z])
            rotate([90, 0, 0])
                cylinder(
                    h=skirt_t + fit + closure_bearing_pad_depth + 1.0,
                    d=closure_screw_d,
                    $fn=32
                );
}


//\\/\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//
// Base
//\\/\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//
module base_part() {
    difference() {
        union() {
            // Hollow shell first, then add closure bosses so the main cavity
            // subtraction does not erase their inward projections.
            difference() {
                rounded_prism([base_x, base_y], base_h, corner_r);

                translate([0, 0, floor_t])
                    rounded_prism(
                        [base_x - 2*wall, base_y - 2*wall],
                        base_h,
                        max(0.1, corner_r - wall)
                    );

                for (sx=[0, pi_hole_dx])
                    for (sy=[0, pi_hole_dy]) {
                        px = pi_origin_x + pi_hole_inset + sy;
                        py = pi_origin_y + (pi_x - pi_hole_inset - sx);

                        // Through-hole for M2.5 screw.
                        translate([px, py, -0.01])
                            cylinder(h=floor_t + 0.02, d=pi_mount_clear_d);

                        // Counterbore from the exterior bottom.
                        translate([px, py, -0.01])
                            cylinder(h=pi_counterbore_h + 0.02, d=pi_counterbore_d);
                    }

                // Right-side port tunnels: mini HDMI + 2x micro USB.
                side_port_tunnel_center(mini_hdmi_c, side_port_z, mini_hdmi_w, mini_hdmi_h);
                side_port_tunnel_center(usb1_c,      side_port_z, micro_usb_w, micro_usb_h);
                side_port_tunnel_center(usb2_c,      side_port_z, micro_usb_w, micro_usb_h);
            }

            base_front_receiver_bosses();
            base_rear_closure_bosses();
        }

        base_front_receiver_slots();
        base_rear_closure_cutouts();
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

module lid_outer_body() {
    yz_profile_extrude(outer_profile, lid_x);
}

module lid_inner_cavity() {
    yz_profile_extrude(inner_profile, lid_inner_x);
}

module lid_part() {
    difference() {
        union() {
            difference() {
                lid_outer_body();

                // Main hollow underside.
                lid_inner_cavity();

                // OLED window through the sloped deck.
                panel_frame()
                    translate([
                        oled_lx + oled_window_offset_x,
                        oled_ly + oled_window_center_y,
                        0
                    ])
                        cube([oled_window_x, oled_window_y, 30], center=true);

                // OLED mounting holes through the sloped deck.
                panel_frame()
                    xy_hole_grid(oled_lx, oled_ly, oled_hole_dx, oled_hole_dy)
                        cylinder(h=30, d=oled_hole_d, center=true);

                // Button holes through the same sloped deck plane.
                panel_frame()
                    for (p = button_positions)
                        translate([p[0], p[1], 0])
                            cylinder(h=30, d=button_panel_hole, center=true);

                lid_markings();
                lid_front_skirt_pivot_bevel();
            }

            // Add closure features after hollowing so they project into the
            // cavity and remain joined to the skirt.
            lid_front_tuck_tabs();
            lid_rear_bearing_pads();
            lid_inner_stop_lip_3sided();
        }

        lid_rear_screw_holes();
    }
}


//\\/\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//
// Scene
//\\/\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//\\//

lid_color  = "silver";
base_color = "black";
// CLI-friendly selector: 0=scene, 1=base, 2=lid, 3=assembly,
// 4=closure section, 5=assembly interference, 6=pivot preview,
// 7=pivot interference. Numeric values avoid shell quoting differences.
render_target = 0;

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

module closure_section() {
    section_w = 3.0;
    section_h = roof_high_top_z + base_h + 10;
    section_gap = interference_test_gap;
    // Avoid an exact symmetry plane through cylindrical facets; the small
    // offset prevents a known CGAL 4.11 non-manifold sectioning artefact.
    section_x = closure_screw_x + 0.071;

    color(base_color)
        intersection() {
            base_part();
            translate([section_x, 0, section_h/2 - 1])
                cube([section_w, lid_y + 10, section_h], center=true);
        }

    color(lid_color)
        intersection() {
            // The same modelling epsilon used by the collision diagnostic
            // separates intentionally seated faces in this render-only view.
            translate([0, 0, base_h - skirt_h + section_gap]) lid_part();
            translate([section_x, 0, section_h/2 - 1])
                cube([section_w, lid_y + 10, section_h], center=true);
        }

    color("gold")
        intersection() {
            translate([0, 0, section_gap]) closure_hardware_preview();
            translate([section_x, 0, section_h/2 - 1])
                cube([section_w, lid_y + 10, section_h], center=true);
        }
}

module closure_hardware_preview() {
    screw_l = 8.0;
    screw_head_d = 5.0;
    screw_head_h = 2.0;

    for (x = [-closure_screw_x, closure_screw_x]) {
        translate([x, lid_y/2, closure_screw_z])
            rotate([90, 0, 0])
                cylinder(h=screw_l, d=2.5, $fn=32);

        // A small overlap keeps the illustrative head and shaft a valid union.
        translate([x, lid_y/2 + screw_head_h - 0.05, closure_screw_z])
            rotate([90, 0, 0])
                cylinder(h=screw_head_h, d=screw_head_d, $fn=32);

        translate([x, closure_nut_y, closure_screw_z])
            rotate([90, 0, 0])
                rotate([0, 0, 30])
                    cylinder(
                        h=closure_nut_t,
                        d=closure_nut_corner_d,
                        center=true,
                        $fn=6
                    );
    }
}

function pivot_slide_for_angle(angle) =
    pivot_preview_slide * sqrt(max(0, sin(
        min(max(angle, 0), pivot_path_max_angle) / pivot_path_max_angle * 180
    )));

module positioned_lid(angle=0, slide_y=0) {
    pivot_y = -base_y/2;
    pivot_z = front_tab_global_z;

    translate([0, slide_y, 0])
        translate([0, pivot_y, pivot_z])
            rotate([angle, 0, 0])
                translate([0, -pivot_y, -pivot_z])
                    translate([0, 0, base_h - skirt_h])
                        lid_part();
}

module assembly_interference() {
    intersection() {
        base_part();
        // Lift by a modelling epsilon so the intended lip/rim seating plane is
        // not reported as a false collision.
        translate([0, 0, interference_test_gap]) positioned_lid();
    }
}

module pivot_interference() {
    intersection() {
        base_part();
        positioned_lid(
            pivot_preview_angle,
            pivot_slide_for_angle(pivot_preview_angle)
        );
    }
}

if (render_target == 1) {
    base_part();
} else if (render_target == 2) {
    lid_part();
} else if (render_target == 3) {
    color(base_color) base_part();
    color(lid_color) positioned_lid();
} else if (render_target == 4) {
    closure_section();
} else if (render_target == 5) {
    assembly_interference();
} else if (render_target == 6) {
    color(base_color) base_part();
    color(lid_color)
        positioned_lid(
            pivot_preview_angle,
            pivot_slide_for_angle(pivot_preview_angle)
        );
} else if (render_target == 7) {
    pivot_interference();
} else {
    scene();
}
