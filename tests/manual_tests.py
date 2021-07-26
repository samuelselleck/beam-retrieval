# %% Init
import sys
from matplotlib import image
import matplotlib.pyplot as plt
import LightPipes as lp
import numpy as np
import math
sys.path.insert(1, '../beam_retrieval')

import field_retrieval as retrieval
import field_analysis

before_src = "G:/Atto/Data/LASC/kHz/atom-atto31/data2/2021-06-30/m30_uncorrected.bmp"
behind_src = "G:/Atto/Data/LASC/kHz/atom-atto31/data2/2021-06-30/p30_uncorrected.bmp"

before_raw = image.imread(before_src)
behind_raw = image.imread(behind_src)

dist_to_focus = 0.03
pixel_size = 6e-6
wavelength = 800e-9

# %% GS Field Retrieval

F_behind = retrieval.mgsa_field_retrieval(before_raw, behind_raw, dist_to_focus, pixel_size, wavelength)

# %%
%matplotlib qt

r, _ = lp.Intensity(F_behind).shape

F_behind_highres = lp.Interpol(F_behind, r*pixel_size, r)

F_focus_highres = lp.Forvard(F_behind_highres, -dist_to_focus)
F_far = lp.PipFFT(F_focus_highres)

F_far = lp.CircAperture(F_far, pixel_size*r/10,0,0)

#intensity = lp.Intensity(F_far)
#intensity[intensity < 0.003*np.max(intensity)] = 0
#F_far = lp.SubIntensity(F_far, intensity)

F_far_ideal = lp.SubPhase(F_far, 0)

F_focus_ideal = lp.PipFFT(F_far_ideal, -1)

intensities = []
iwp = 10
x = np.concatenate((
    np.linspace(-dist_to_focus, -dist_to_focus/iwp, 10),
    np.linspace(-dist_to_focus/iwp, dist_to_focus/iwp, 31),
    np.linspace(dist_to_focus/iwp, dist_to_focus, 10)
))
for dz in x:
    F = lp.Forvard(F_focus_ideal, dz)
    intensities.append(np.max(lp.Intensity(F)))

plt.figure()
plt.plot(x, intensities)
plt.show()

# %%
