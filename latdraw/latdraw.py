"""Main module."""


from math import copysign

import matplotlib.patches as patches
import matplotlib.pyplot as plt
from adjustText import adjust_text

import latdraw.lattice as lattice

MAGNET_WIDTH = 0.1

DEFAULT_COLOUR_MAP = {lattice.Quadrupole: "red",
                      lattice.SBend: "blue",
                      lattice.RBend: "blue",
                      lattice.RFCavity: "gray",
                      lattice.Marker: None,
                      lattice.Drift: None,
                      lattice.Monitor: None,
                      lattice.HKicker: "purple",
                      lattice.VKicker: "purple",
                      lattice.Kicker: "purple",
                      lattice.Cavity: "orange",
                      lattice.Collimator: "black",
                      lattice.GenericMap: "gray",
                      lattice.Solenoid: "pink",
                      lattice.Sextupole: "green",
                      lattice.TransverseDeflectingCavity: "orange",
                      lattice.Undulator: "cyan"
}

def draw(fig, axes, sequence, colour_map=None, annotate=True, dimension="x", magnet_width=MAGNET_WIDTH, **drawlinekw):

    draw_line(axes, sequence, dimension=dimension,  **drawlinekw)
    if colour_map is None:
        colour_map = DEFAULT_COLOUR_MAP

    patch_ids_to_annotations = {}

    for element in sequence:
        colour = DEFAULT_COLOUR_MAP[type(element)]
        alpha = 1

        if not element.is_powered():
            alpha = 0.25

        if colour is None:
            alpha = 0.0

        # This is the end basically.
        pos = element.position
        x, y, z = pos
        if dimension == "y":
            x = y
        elif dimension != "x":
            raise ValueError(f"Unrecognised dimension type {dimension}.")


        length = element.length
        patch_start_x = z - length
        patch_width = length
        patch_start_y = x - 2 * magnet_width
        patch_height = 4 * magnet_width

        try:
            patch_height = copysign(patch_height * 0.5, element.strength())
        except AttributeError:
            pass
        else:
            patch_start_y = x

        # from IPython import embed; embed()

        rectx = patches.Rectangle((patch_start_x, patch_start_y),
                                  patch_width,
                                  patch_height,
                                  linewidth=0.1,
                                  # label=label,
                                  edgecolor='white',
                                  facecolor=colour,
                                  alpha=alpha)
        axes.add_patch(rectx)

        if annotate:
            element_type = type(element).__name__

            annotation = axes.annotate(
                f"{element_type}: {element.name}",
                xy=(z, x),  # xycoords='data',
                xytext=(z, x), textcoords='data',
                horizontalalignment="left",
                arrowprops=dict(arrowstyle="simple", connectionstyle="arc3,rad=+0.2"),
                bbox=dict(boxstyle="round", facecolor="w", edgecolor="0.5", alpha=0.9),
                fontsize=18
            )
            # by default, disable the annotation visibility
            annotation.set_visible(False)
            patch_ids_to_annotations[id(rectx)] = annotation
            rectx.set_picker(True)


    def on_pick(event):
        annotation = patch_ids_to_annotations[id(event.artist)]
        annotation.set_visible(not annotation.get_visible())
        # adjust_text([a for a in patch_ids_to_annotations.values()
        #              if a.get_visible()])
        fig.canvas.draw_idle(# text_from_points=False
                             )
        # plt.draw()

    def on_press(event):
        if event.key == 'c': # press c to clear the annotations.
            for annotation in patch_ids_to_annotations.values():
                annotation.set_visible(False)
        fig.canvas.draw_idle()

    fig.canvas.mpl_connect('pick_event', on_pick)
    fig.canvas.mpl_connect('key_press_event', on_press)


def draw_line(axes, sequence, dimension="x", **plotkw):
    positions = [t.position for t in sequence]
    z = [point[2] for point in positions]

    if dimension == "x":
        x = [point[0] for point in positions]
    elif dimension == "y":
        x = [point[1] for point in positions]
    else:
        raise ValueError(f"Unrecognised dimension value: {dimension}")

    axes.plot(z, x, **plotkw)
    axes.set_ylim(-3, 3)
