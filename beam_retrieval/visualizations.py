import LightPipes as lp
from matplotlib.widgets import Slider
from matplotlib import pyplot as plt
from matplotlib import widgets
import itertools 

def interactive_field(fig, F_behind, dist_to_focus, start=0):


    def get_image_plane(offset):
        F_plane = lp.Forvard(offset - 2*dist_to_focus, F_behind)
        plane_intensity = lp.Intensity(F_plane)
        plane_phase = lp.Phase(F_plane, unwrap = False)
        return plane_intensity

    def update(val):
        img.set_data(get_image_plane(slider.val))
        fig.canvas.draw()
    
    fig.subplots_adjust(left=0.25, bottom=0.25)
    ax = fig.add_subplot(111)
    axplane = fig.add_axes([0.25, 0.1, 0.65, 0.03])

    slider = Slider(axplane, 'Plane', 0, 2*dist_to_focus, valinit=start)
    slider.on_changed(update)

    first = get_image_plane(start)
    h, w = first.shape
    img = ax.imshow(first, extent=[0, w, h,0])
    fig.canvas.draw()


def plot_fields(fig, F_behind, dist_to_focus, unwrap = True):

    F_focus = lp.Forvard(-dist_to_focus, F_behind)
    F_before = lp.Forvard(-2*dist_to_focus, F_behind)

    plt.rcParams["figure.figsize"] = (10,10)

    plotting = {
        "Recovered Intensity Before Focus": lp.Intensity(F_before),
        "Recovered Phase Before Focus": lp.Phase(F_before, unwrap=unwrap),
        "Recovered Intensity Behind Focus": lp.Intensity(F_behind),
        "Recovered Phase Behind Focus": lp.Phase(F_behind, unwrap=unwrap),
        "Recovered Intensity At Focus": lp.Intensity(F_focus),
        "Recovered Phase At Focus": lp.Phase(F_focus, unwrap=unwrap),
    }

    plot_shape = (3, 2)

    fig, axs = plt.subplots(*plot_shape)

    for (i, j), (title, img) in zip(
            itertools.product(*[range(n) for n in plot_shape]),
            plotting.items()
        ):
        axs[i, j].title.set_text(title)
        axs[i, j].imshow(img)

    plt.show()