# %% Parameters and Input

from matplotlib import pyplot as plt
from matplotlib import image
FOLDER = '../testfiles/ast and coma correction'

before_focus = image.imread(f'{FOLDER}/m30_A.bmp')
behind_focus = image.imread(f'{FOLDER}/p30_A.bmp')

N_y, N_x = before_focus.shape
Z = 0.03  #Distance to the geometrical focus in m
Delta_Z = Z    #This is the distance from the estimated geometrical focus to the other side.

# %% Show input images
plt.imshow(before_focus)
plt.figure()
plt.imshow(behind_focus)
plt.show()

# %%


