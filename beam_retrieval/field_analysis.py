import LightPipes as lp
import numpy as np
import matplotlib.pyplot as plt

def get_slice_metrics(F_behind, dist_to_focus, pixel_size, steps):
    metrics = {
        "Distance From Focus": [],
        "Peak Intensity": [],
        "Ideal Peak Intensity": [],
        "Strehl Ratio": [],
    }

    F_far = lp.PipFFT(F_behind)
    F_far = lp.SubPhase(F_far, 0)
    F_focus_ideal = lp.PipFFT(F_far, -1)

    for i in range(steps):
        dz = -2*dist_to_focus*i/(steps - 1)
        F_slice = lp.Forvard(F_behind, dz)
        metrics["Distance From Focus"].append(dist_to_focus + dz)

        intensity = lp.Intensity(F_slice)
        max_intensity = np.max(intensity)
        phase = lp.Phase(F_slice)
        mask = intensity < max_intensity/256
        phase[mask] = 0
        intensity[mask] = 0
        F_col = lp.SubPhase(F_slice, phase)
        metrics["Strehl Ratio"].append(lp.Strehl(F_col))
        metrics["Peak Intensity"].append(max_intensity)

        F_ideal_slice = lp.Forvard(F_focus_ideal, dz + dist_to_focus)
        max_ideal = np.max(lp.Intensity(F_ideal_slice))
        metrics["Ideal Peak Intensity"].append(max_ideal)

    
    return metrics