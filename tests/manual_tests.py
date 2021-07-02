# %% Init
import sys
from matplotlib import image
import matplotlib.pyplot as plt
import LightPipes as lp

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

#%% Plotting

F_focus = lp.Forvard(F_behind, -dist_to_focus)
F = lp.Interpol(F_focus, pixel_size*50, 50)

print(lp.Strehl(F))
intensity = lp.Intensity(F)
plt.imshow(intensity)
# %%
