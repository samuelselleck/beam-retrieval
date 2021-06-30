from matplotlib import pyplot as plt
from matplotlib import image
import math
from matplotlib import widgets
import numpy as np
import LightPipes as lp
import itertools
from matplotlib.widgets import Slider

def main():
    FOLDER = 'G:/Atto/Data/LASC/kHz/atom-atto31/data2/2021-06-30'

    #Input images
    before_focus_raw = image.imread(f'{FOLDER}/m30_uncorrected.bmp')
    behind_focus_raw = image.imread(f'{FOLDER}/p30_uncorrected.bmp')

    #Parameters
    Z = 0.03  #Distance to the geometrical focus in m
    dist_to_focus = Z/2
    f = 0.5    #Focal length in m. This is important for the near-field/far-field transforms.
    pixel_size = 6e-6   #Pixel size of the older IDS camera in m (640x480 pixels on a 6.4*4.8mm chip)
    wavelength = 800e-9 #Wavelength in m

    F_behind = beam_field_retrieval(before_focus_raw, behind_focus_raw, dist_to_focus, pixel_size, wavelength)
    F_focus = lp.Forvard(-dist_to_focus, F_behind)
    F_before = lp.Forvard(-Z, F_behind)

    interactive_field(F_focus, dist_to_focus)
    plot_fields(F_before, F_focus, F_behind)

def beam_field_retrieval(before_focus_intensity, behind_focus_intensity, dist_to_focus, pixel_size, wavelength):
    #Threshhold, pad edges.
    before_focus_global = preprocess_image(before_focus_intensity)
    behind_focus_global = preprocess_image(behind_focus_intensity)

    #Cut out square local fields using the largest dimension.
    fx, fy, fw, fh = local_field_coords(before_focus_global)
    hx, hy, hw, hh = local_field_coords(behind_focus_global)
    s = max(fw, fh, hw, hh)
    before_focus = before_focus_global[fx-s:fx+s, fy-s:fy+s]
    behind_focus = behind_focus_global[hx-s:hx+s, hy-s:hy+s]

    #Local field image size.
    image_size = before_focus.shape[0]
    local_size = image_size*pixel_size

    #perform phase retrieval
    F_behind = symmetric_gerchberg_saxton(
        before_focus,
        behind_focus,
        dist_to_focus,
        local_size,
        wavelength
    )

    return F_behind


def preprocess_image(img):
    image_height, image_width = img.shape
    h_diff = (image_width - image_height)/2

    norm = img.astype('float')/np.max(img)
    norm[norm < 0.05] = 0
    square = np.vstack([
        np.zeros((math.floor(h_diff), image_width)),
        norm,
        np.zeros((math.ceil(h_diff), image_width))
    ])
    return np.pad(square, image_width)

def local_field_coords(img):
    width = img.shape[0]
    #Create temporary field to extract beam centroid/moment
    F = lp.Begin(width, 1, width)
    F = lp.SubIntensity(img, F)
    *_, y, x = lp.Centroid(F)
    sx, sy = lp.D4sigma(F)
    w, h = round(sx), round(sy) 
    return (x, y, w, h)

def symmetric_gerchberg_saxton(before_focus, behind_focus, dist_to_focus, local_size, wavelength, iterations=100):
    F = lp.Begin(local_size, wavelength, before_focus.shape[0])

    #Initial phase guess
    F = lp.Lens(F, -dist_to_focus)

    for i in range(iterations):
        #F = lp.RandomPhase(F, i, math.pi/(i + 1))
        F = lp.SubIntensity(behind_focus, F)
        F = lp.Forvard(-2*dist_to_focus, F)
        F = lp.SubIntensity(before_focus, F)
        F = lp.Forvard(2*dist_to_focus, F)

    return F

def interactive_field(F_focus, dist_to_focus, start=None):

    if start is None:
        start = -dist_to_focus

    def get_image_plane(offset):
        F_plane = lp.Forvard(offset, F_focus)
        plane_intensity = lp.Intensity(F_plane)
        plane_phase = lp.Phase(F_plane, unwrap = False)
        return plane_intensity

    def update(val):
        img.set_data(get_image_plane(slider.val))
        fig.canvas.draw()
        
    fig = plt.figure()
    fig.subplots_adjust(left=0.25, bottom=0.25)
    ax = fig.add_subplot(111)
    axplane = fig.add_axes([0.25, 0.1, 0.65, 0.03])

    slider = Slider(axplane, 'Plane', -dist_to_focus, dist_to_focus, valinit=start)
    slider.on_changed(update)

    img = ax.imshow(get_image_plane(start))

    plt.show()


def plot_fields(F_before, F_focus, F_behind, unwrap = True):
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

if __name__ == "__main__":
    main()

def zernike_decomposition():
    #TODO cleanup and fix
    phase_result = image.imread(f'{FOLDER}/phase_result.bmp')
    F_focus = lp.Begin(real_size, wavelength, phase_result.shape[0])
    F_focus = lp.SubPhase(F_focus, phase_result)

    R = real_size/2 #TODO ??? how to choose?
    zernike_index , zernike_amplitudes = lp.ZernikeFit(F_focus, 9, R)#units='rad')

    fig, ax = plt.subplots()

    hbars = ax.barh(zernike_index, zernike_amplitudes, align='center')
    ax.set_yticks(zernike_index)
    ax.set_yticklabels([lp.ZernikeName(i).title() for i in zernike_index])
    ax.invert_yaxis()
    ax.set_xlabel('Optical Path Difference (m)')
    ax.set_title('Zernike Decompostiion')

    plt.show()

