import LightPipes as lp
import numpy as np
import matplotlib.pyplot as plt

def get_slice_metrics(F_behind, dist_to_focus, pixel_size, steps):
    metrics = {
        "Distance From Focus": [],
        "Peak Intensity": [],
        "Peak Ideal Intensity": [],
        "Width X": [],
        "Width Y": [],
    }

    #Calculate the ideal focus, used for strehl ratio
    r, _ = lp.Intensity(F_behind).shape
    F_focus = lp.Forvard(F_behind, -dist_to_focus)
    F_far = lp.PipFFT(F_focus)
    intensity = lp.Intensity(F_far)
    intensity[intensity < np.max(intensity)*0.01] = 0
    F_far = lp.SubIntensity(F_far, intensity)

    F_far_ideal = lp.SubPhase(F_far, 0)
    F_focus_ideal = lp.PipFFT(F_far_ideal, -1)
    F_focus = lp.PipFFT(F_far, -1)

    debug = [F_focus_ideal, F_focus]

    for i in range(steps):
        dz = -2*dist_to_focus*i/(steps - 1)
        F_slice = lp.Forvard(F_behind, dz)
        F_slice_ideal = lp.Forvard(F_focus_ideal, dz + dist_to_focus)
        F_slice_thresh = lp.Forvard(F_focus, dz + dist_to_focus)

        metrics["Distance From Focus"].append(dist_to_focus + dz)

        w, h = lp.D4sigma(F_slice)
        metrics["Width X"].append(w)
        metrics["Width Y"].append(h)

        intensity = lp.Intensity(F_slice_thresh)
        max_intensity = np.max(intensity)
        intensity_ideal = lp.Intensity(F_slice_ideal)
        max_intensity_ideal = np.max(intensity_ideal)
        metrics["Peak Ideal Intensity"].append(max_intensity_ideal)
        metrics["Peak Intensity"].append(max_intensity)
    
    global_max_intensity_ideal  = np.max(metrics["Peak Ideal Intensity"])
    metrics["Peak Ideal Intensity"] /= global_max_intensity_ideal
    metrics["Peak Intensity"] /= global_max_intensity_ideal

    return metrics, debug