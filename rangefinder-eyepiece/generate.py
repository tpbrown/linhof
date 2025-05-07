#!/usr/bin/env python

"""Generate a 3D model of an M18 to M16 threaded adapter using Build123d."""

"""
Dependencies:
    pip install build123d
"""


from build123d import *
from bd_warehouse.thread import IsoThread

lens_mount_diameter = 18.0 * MM  # M18 thread major diameter
camera_screw_diameter = 16.0 * MM  # M16 thread major diameter
pitch = 0.75 * MM  # Thread pitch (same for both sides)

thread_turns = 4  # Minimal thread engagement
wall_thickness = 1 * MM

lens_mount_depth = 5 * MM
lens_mount_thread_depth = pitch + thread_turns
camera_screw_length = pitch * thread_turns + 2 * MM

camera_screw_radius = camera_screw_diameter / 2
camera_screw_bore_radius = camera_screw_radius - (wall_thickness / 2)
lens_mount_external_radius = (lens_mount_diameter + wall_thickness) / 2


def save_exports(thing, basename: str):
    export_stl(thing, f"{basename}.stl")
    export_step(thing, f"{basename}.step")


def main():
    camera_mount_height = camera_screw_length
    adapter_body_height = camera_mount_height * 1.33
    adapter_body_top_radius = lens_mount_external_radius

    thread_depth = 0.6134 * pitch
    camera_root_radius = (camera_screw_diameter - 2 * thread_depth) / 2

    with BuildPart() as assembly:
        assembly.label = "Camera mount and adapter"
        with BuildSketch():
            Circle(radius=camera_root_radius)
            Circle(radius=camera_screw_bore_radius, mode=Mode.SUBTRACT)
        extrude(amount=camera_mount_height)
        IsoThread(
            major_diameter=camera_screw_diameter,
            pitch=pitch,
            length=camera_screw_length,
            external=True,
            # end_finishes=("chamfer", "chamfer"),
            hand="right",
            interference=0,
            rotation=(0, 0, 180),
        )
        Cone(
            bottom_radius=camera_screw_radius,
            top_radius=adapter_body_top_radius,
            height=adapter_body_height,
            rotation=(180, 0, 0),
        )
        Cone(
            bottom_radius=camera_screw_radius - (wall_thickness / 2),
            top_radius=adapter_body_top_radius - (wall_thickness / 2),
            height=adapter_body_height,
            mode=Mode.SUBTRACT,
            rotation=(180, 0, 0),
        )

    lens = Cylinder(
        radius=lens_mount_external_radius,
        height=lens_mount_depth + wall_thickness,
        align=(Align.CENTER, Align.CENTER, Align.MAX),
    )
    lens -= Cylinder(
        radius=lens_mount_diameter / 2,
        height=lens_mount_depth + wall_thickness,
        mode=Mode.SUBTRACT,
        align=(Align.CENTER, Align.CENTER, Align.MAX),
    )

    lens = IsoThread(
        major_diameter=lens_mount_diameter,
        pitch=pitch,
        length=lens_mount_thread_depth,
        external=False,
        # end_finishes=("chamfer", "chamfer"),
        hand="right",
        align=(Align.CENTER, Align.CENTER, Align.MAX),
        interference=0,
    ).fuse(lens)

    eyepiece = Compound(
        label="eyepiece",
        children=[assembly.part, lens.located(Location((0, 0, -3.33)))],
    )

    # print(eyepiece.show_topology())
    save_exports(eyepiece, "m18x075_f_to_m16x075_diopter_mount")


if __name__ == "__main__":
    main()
