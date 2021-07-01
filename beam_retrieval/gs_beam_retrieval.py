import math
import numpy as np
import LightPipes as lp

def gs_beam_retrieval(before_focus_intensity, behind_focus_intensity, dist_to_focus, pixel_size, wavelength, iterations=100):

    #Threshhold, pad edges.
    before_focus_global = _preprocess_image(before_focus_intensity)
    behind_focus_global = _preprocess_image(behind_focus_intensity)

    #Cut out square local fields using the largest dimension.
    fx, fy, fw, fh = _local_field_coords(before_focus_global)
    hx, hy, hw, hh = _local_field_coords(behind_focus_global)
    s = max(fw, fh, hw, hh)
    before_focus = before_focus_global[fx-s:fx+s, fy-s:fy+s]
    behind_focus = behind_focus_global[hx-s:hx+s, hy-s:hy+s]

    #Local field image size.
    image_size = before_focus.shape[0]
    local_size = image_size*pixel_size

    #perform phase retrieval
    F_behind = _symmetric_gerchberg_saxton(
        before_focus,
        behind_focus,
        dist_to_focus,
        local_size,
        wavelength,
        iterations,
    )

    return F_behind

def _preprocess_image(img):
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

def _local_field_coords(img):
    width = img.shape[0]
    #Create temporary field to extract beam centroid/moment
    F = lp.Begin(width, 1, width)
    F = lp.SubIntensity(img, F)
    *_, y, x = lp.Centroid(F)
    sx, sy = lp.D4sigma(F)
    w, h = round(sx), round(sy)
    return (x, y, w, h)

def _symmetric_gerchberg_saxton(before_focus, behind_focus, dist_to_focus, local_size, wavelength, iterations=100):
    F = lp.Begin(local_size, wavelength, before_focus.shape[0])

    F = lp.Lens(F, -dist_to_focus)

    for i in range(iterations):
        F = lp.SubIntensity(behind_focus, F)
        F = lp.Forvard(-2*dist_to_focus, F)
        F = lp.SubIntensity(before_focus, F)
        F = lp.Forvard(2*dist_to_focus, F)

    return F
