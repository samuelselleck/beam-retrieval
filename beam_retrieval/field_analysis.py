import LightPipes as lp
import numpy as np
import matplotlib.pyplot as plt

def get_slice_metrics(F_behind, dist_to_focus, pixel_size, steps):
    metrics = {
        "Distance From Focus": [],
        "Peak Intensity": [],
        "Peak Ideal Intensity": [],
        "Strehl Ratio": [],
    }


    #Calculate the ideal focus, used for strehl ratio
    r, _ = lp.Intensity(F_behind).shape
    F_focus = lp.Forvard(F_behind, -dist_to_focus)
    F_far = lp.PipFFT(F_focus)
    F_far = lp.CircAperture(F_far, pixel_size*r/6,0,0)
    F_far_ideal = lp.SubPhase(F_far, 0)
    F_focus_ideal = lp.PipFFT(F_far_ideal, -1)

    debug = [F_focus_ideal, F_focus]

    for i in range(steps):
        dz = -2*dist_to_focus*i/(steps - 1)
        F_slice = lp.Forvard(F_behind, dz)
        F_slice_ideal = lp.Forvard(F_focus_ideal, dz + dist_to_focus)
        metrics["Distance From Focus"].append(dist_to_focus + dz)

        intensity = lp.Intensity(F_slice)
        max_intensity = np.max(intensity)
        intensity_ideal = lp.Intensity(F_slice_ideal)
        max_intensity_ideal = np.max(intensity_ideal)

        metrics["Peak Ideal Intensity"].append(max_intensity_ideal)
        metrics["Peak Intensity"].append(max_intensity)
    
    global_max_intensity_ideal  = np.max(metrics["Peak Ideal Intensity"])
    metrics["Peak Ideal Intensity"] /= global_max_intensity_ideal
    metrics["Peak Intensity"] /= global_max_intensity_ideal

    return metrics, debug