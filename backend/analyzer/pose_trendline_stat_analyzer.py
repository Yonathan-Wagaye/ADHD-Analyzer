import os
import json
import numpy as np
from utils.stat_tests import stat_test


def analyze_pose_pvalues(json_file='../backend/results/pose/pose_trendline_stats_threshold_15.json'):
    """
    Analyze p-values and mean ± std for combined pose trendline data (ADHD vs Non-ADHD).
    """
    with open(json_file, 'r') as file:
        data = json.load(file)
    
    results = {
        "ADHD_vs_NonADHD": {"p_values": {}, "mean_std": {}}
    }

    for session in range(1, 9):  # Sessions 1 to 8
        session_key = f"Session {session}"

        # Combine "With Distraction" and "Without Distraction" scores for each group
        adhd_scores = np.concatenate(data["ADHD"][session_key]["w"] + data["ADHD"][session_key]["wo"])
        non_adhd_scores = np.concatenate(data["Non-ADHD"][session_key]["w"] + data["Non-ADHD"][session_key]["wo"])

        # Perform statistical test
        _, p_val = stat_test(adhd_scores, non_adhd_scores)

        # Calculate mean ± std
        adhd_mean, adhd_std = np.mean(adhd_scores), np.std(adhd_scores)
        non_adhd_mean, non_adhd_std = np.mean(non_adhd_scores), np.std(non_adhd_scores)

        # Save results
        results["ADHD_vs_NonADHD"]["p_values"][session_key] = p_val
        results["ADHD_vs_NonADHD"]["mean_std"][session_key] = {
            "ADHD": f"{adhd_mean:.2f} ± {adhd_std:.2f}",
            "Non-ADHD": f"{non_adhd_mean:.2f} ± {non_adhd_std:.2f}"
        }

    return results


def get_pose_pvalues_array(json_file='../backend/results/pose/pose_trendline_stats_threshold_15.json'):
    """
    Get an array of p-values for ADHD vs Non-ADHD pose trendline data.

    Parameters:
    - json_file: Path to the JSON file containing trendline stats.

    Returns:
    - p_values_array: List of p-values for sessions 1 to 8.
    """
    results = analyze_pose_pvalues(json_file)
    p_values_dict = results["ADHD_vs_NonADHD"]["p_values"]

    # Convert p-values to a list, ordered by session
    p_values_array = [p_values_dict[f"Session {session}"] for session in range(1, 9)]

    return p_values_array
