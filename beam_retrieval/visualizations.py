import LightPipes as lp
from matplotlib.widgets import Slider
from matplotlib import pyplot as plt
from matplotlib import widgets
import itertools 
import numpy as np
import field_analysis

def set_fig_images(fig, *images, extent=None):
    images = [im for im in images if im is not None]
    fig.clear()
    fig.subplots(1, len(images))
    for i in range(len(images)):
        h, w = images[i].shape
        if extent is None:
            extent = [0, w, h,0]
        fig.axes[i].imshow(images[i], extent=extent)
    fig.set_tight_layout(True)
    fig.canvas.draw()

def interactive_field(fig, F_behind, dist_to_focus, start=0):
    def get_image_plane(offset):
        F_plane = lp.Forvard(offset - 2*dist_to_focus, F_behind)
        plane_intensity = lp.Intensity(F_plane)
        return plane_intensity/np.max(plane_intensity)

    def update(val):
        img.set_data(get_image_plane(slider.val))
        fig.canvas.draw()

    fig.clear()
    fig.subplots_adjust(left=0.25, bottom=0.25)
    ax = fig.add_subplot(111)
    axplane = fig.add_axes([0.25, 0.1, 0.65, 0.03])

    slider = Slider(axplane, 'Plane', 0, 2*dist_to_focus, valinit=start)
    slider.on_changed(update)

    first = get_image_plane(start)
    h, w = first.shape
    img = ax.imshow(first, extent=[0, w, h,0])
    fig.canvas.draw()
    ax.set_title(f"Normalized Field")
    


def plot_fields(fig, F_behind, dist_to_focus, unwrap = True):
    F_focus = lp.Forvard(-dist_to_focus, F_behind)
    F_before = lp.Forvard(-2*dist_to_focus, F_behind)

    plotting = {
        "Intensity Before Focus": lp.Intensity(F_before),
        "Phase Before Focus": lp.Phase(F_before, unwrap=unwrap),
        "Intensity Behind Focus": lp.Intensity(F_behind),
        "Phase Behind Focus": lp.Phase(F_behind, unwrap=unwrap),
        "Intensity At Focus": lp.Intensity(F_focus),
        "Phase At Focus": lp.Phase(F_focus, unwrap=unwrap),
    }

    rows = 2
    cols = int(len(plotting)/rows)

    fig.clear()
    axs = fig.subplots(rows, cols)

    for i, (title, img) in enumerate(plotting.items()):
        r = i % 2
        c = int(i / 2)
        axs[r, c].set_title(title, fontsize=8)
        axs[r, c].imshow(img)
    
    fig.set_tight_layout(True)
    fig.canvas.draw()

def plot_profile(fig, F_behind, dist_to_focus, pixel_size, threshold):
    metrics, _ = field_analysis.get_slice_metrics(F_behind, dist_to_focus, pixel_size, threshold, steps=100)
    fig.clear()
    plots = [
        {"metrics": ["Width X", "Width Y"], "colors": ["tab:red", "tab:blue"]},
        {"metrics": ["Peak Ideal Intensity", "Peak Intensity"], "colors": ["tab:green", "tab:purple"]},
    ]
    fig.subplots(1, len(plots))

    x_name = "Distance From Focus"
    for i, plot in enumerate(plots):
        ax = fig.axes[i]
        ax.set_xlabel(x_name)
        ax.set_ylabel("Metics")
        for i in range(len(plot["metrics"])):
            y_name = plot["metrics"][i]
            style = plot["colors"][i]
            ax.plot(metrics[x_name], metrics[y_name], color=style)
        ax.legend(plot["metrics"])

    ax.text(0.1, 0.9, f'Strehl: {np.max(metrics["Peak Intensity"]):.2f}', transform=ax.transAxes)

    fig.set_tight_layout(True)
    fig.canvas.draw()

def plot_farfield(fig, F_behind, dist_to_focus, pixel_size):

    F_far = lp.PipFFT(F_behind)
    image, r = _extract_beam_image(F_far, pixel_size)
    set_fig_images(fig, lp.Intensity(F_far), image)

def _extract_beam_image(F, pixel_size):
    *_, y, x = lp.Centroid(F)
    sx, sy = lp.D4sigma(F)
    r = max(sx, sy)/2
    s = round(r/pixel_size)
    intensity = lp.Intensity(F)
    return (intensity[x-s:x+s,y-s:y+s], r)


