# %% Parameters and Input

from matplotlib import pyplot as plt
from matplotlib import image
import math
from matplotlib import widgets
import numpy as np
import LightPipes as lp
import itertools
from scipy.signal import medfilt2d
from matplotlib.widgets import Slider

FOLDER = 'G:/Atto/Data/LASC/kHz/atom-atto31/data2/2021-06-30'

#Input images
before_focus_raw = image.imread(f'{FOLDER}/m30_uncorrected.bmp')
behind_focus_raw = image.imread(f'{FOLDER}/p30_uncorrected.bmp')

# Q: questiions
# TODO: routines to implement
# ref: uses other matlab file

# Q: AWGS?

#Parameters
Z = 0.03  #Distance to the geometrical focus in m
dz = Z    #This is the distance from the estimated geometrical focus to the other side.
f = 0.5    #Focal length in m. This is important for the near-field/far-field transforms.
far_field_cutting_radius = 0.0075  #We cut in the far-field at this radius. Otherwise the unabberated back-propagation goes wrong.
pixel_size = 6e-6   #Pixel size of the older IDS camera in m (640x480 pixels on a 6.4*4.8mm chip)
wavelength = 800e-9 #Wavelength in m


# %% Preprossess and cut out local images

def preprocess_image(img):
    image_height, image_width = img.shape
    h_diff = (image_width - image_height)/2

    norm = img.astype('float')/np.max(img)
    norm[norm < 0.05] = 0
    #morm = medfilt2d(norm)
    return np.vstack([
        np.zeros((math.floor(h_diff), image_width)),
        norm,
        np.zeros((math.ceil(h_diff), image_width))
    ])

def local_field_coords(img):
    width = img.shape[0]
    #create temporary field to extract beam centroid/moment
    F = lp.Begin(width, wavelength, width)
    F = lp.SubIntensity(img, F)
    *_, y, x = lp.Centroid(F)
    sx, sy = lp.D4sigma(F)
    w, h = round(sx), round(sy) 
    return (x, y, w, h)

before_focus_global = preprocess_image(before_focus_raw)
behind_focus_global = preprocess_image(behind_focus_raw)

fx, fy, fw, fh = local_field_coords(before_focus_global)
hx, hy, hw, hh = local_field_coords(behind_focus_global)

#smallest power of 2 that is larger or equal maximum
s = 1<<(max(fw, fh, hw, hh)-1).bit_length()

before_focus = before_focus_global[fx-s:fx+s, fy-s:fy+s]
behind_focus = behind_focus_global[hx-s:hx+s, hy-s:hy+s]

#circular mask for local fields (used during propagation)
image_size = before_focus.shape[0]
local_size = image_size*pixel_size


# %% GS Iteration

F = lp.Begin(local_size, wavelength, image_size)
F = lp.Lens(F, -dz/2)

for i in range(100):
    #F = lp.RandomPhase(F, i, math.pi/(i + 1))
    F = lp.SubIntensity(behind_focus, F)
    F = lp.Forvard(-dz, F)
    F = lp.SubIntensity(before_focus, F)
    F = lp.Forvard(dz, F)

F_behind = F
F_focus = lp.Forvard(-dz/2, F)
F_before = lp.Forvard(-dz, F)

#TODO add remove_background flag (line: 95) - Q: ASML data?

#TODO remove isolated hot pixels (line: 103)

# %% Interactive Field Visualization

%matplotlib qt

start = 0

#Get image plane propagated from focus interactively

def get_image_plane(offset):
    F_plane = lp.Forvard(-dz/2 + offset, F_focus)
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

slider = Slider(axplane, 'Plane', 0, dz, valinit=start)
slider.on_changed(update)

img = ax.imshow(get_image_plane(start))

plt.show()


# %% Show input images

plt.rcParams["figure.figsize"] = (10,10)

unwrap = True

plotting = {
    "Before Focus": before_focus,
    "Behind Focus": behind_focus,
    "Recovered Intensity Before Focus": lp.Intensity(F_before),
    "Recovered Intensity Behind Focus": lp.Intensity(F_behind),
    "Recovered Phase Before Focus": lp.Phase(F_before, unwrap=unwrap),
    "Recovered Phase Behind Focus": lp.Phase(F_behind, unwrap=unwrap),
    "Recovered Intensity At Focus": lp.Intensity(F_focus),
    "Recovered Phase At Focus": lp.Phase(F_focus, unwrap=unwrap),
}

plot_shape = (4, 2)

fig, axs = plt.subplots(*plot_shape)

for (i, j), (title, img) in zip(
        itertools.product(*[range(n) for n in plot_shape]),
        plotting.items()
    ):
    axs[i, j].title.set_text(title)
    axs[i, j].imshow(img)

plt.show()
# %% Zernike Decomposition

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

# %%
