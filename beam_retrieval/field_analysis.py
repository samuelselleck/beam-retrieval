import LightPipes as lp
import numpy as np

def get_slice_metrics(F_behind, dist_to_focus, steps):
    metrics = {
        "Distance From Focus": [],
        "Peak Intensity": [],
        "Strehl Ratio": [],
    }
    for i in range(steps):
        dz = -2*dist_to_focus*i/(steps - 1)
        F_slice = lp.Forvard(F_behind, dz)
        metrics["Distance From Focus"].append(dist_to_focus + dz)
        metrics["Strehl Ratio"].append(lp.Strehl(F_slice))
        metrics["Peak Intensity"].append(np.max(lp.Intensity(F_slice)))
    
    return metrics