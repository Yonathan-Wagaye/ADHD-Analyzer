import os
import json
import numpy as np
from utils.stat_tests import stat_test


def analyze_gender_pose_pvalues(json_file="../backend/results/pose/pose_trendline_gender_stat_120_threshold_15.json"):
    """
    Analyze gender-based pose stability p-values and mean ± std for threshold 15.
    """
    with open(json_file, 'r') as file:
        data = json.load(file)

    results = {
                "ADHD_Male_vs_ADHD_Female": {"p_values": {}, "mean_std": {}},
                "NonADHD_Male_vs_NonADHD_Female": {"p_values": {}, "mean_std": {}},
                "ADHD_Male_vs_NonADHD_Male": {"p_values": {}, "mean_std": {}},
                "ADHD_Female_vs_NonADHD_Female": {"p_values": {}, "mean_std": {}},
    }

    for session in range(1, 9):
        session_key = f"Session {session}"

        # Extract data for each group
        adhd_male = [score for block in data["M-ADHD"][session_key] for score in block]
        adhd_female = [score for block in data["F-ADHD"][session_key] for score in block]
        nonadhd_male = [score for block in data["M-nonADHD"][session_key] for score in block]
        nonadhd_female = [score for block in data["F-nonADHD"][session_key] for score in block]

        # Perform statistical tests and calculate mean ± std
        for comp, (group1, group2) in {
            "ADHD_Male_vs_ADHD_Female": (adhd_male, adhd_female),
            "NonADHD_Male_vs_NonADHD_Female": (nonadhd_male, nonadhd_female),
            "ADHD_Male_vs_NonADHD_Male": (adhd_male, nonadhd_male),
            "ADHD_Female_vs_NonADHD_Female": (adhd_female, nonadhd_female)
        }.items():
            _, p_val = stat_test(group1, group2)
            results[comp]["p_values"][session_key] = p_val
            results[comp]["mean_std"][session_key] = {
                comp.split('_vs_')[0]: f"{np.mean(group1):.2f} ± {np.std(group1):.2f}",
                comp.split('_vs_')[1]: f"{np.mean(group2):.2f} ± {np.std(group2):.2f}"
            }

    return results
