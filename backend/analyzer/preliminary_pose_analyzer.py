import json
import numpy as np
from utils.stat_tests import stat_test

def analyze_pose_data(json_file='../backend/results/pose/pose_scores_threshold_15.json'):
    """
    Analyze pose data from JSON file and compute statistical tests.

    Parameters:
    - json_file: Path to the JSON file containing pose scores.

    Returns:
    - results: Dictionary formatted similarly to accuracy analyzer response.
    """
    with open(json_file, 'r') as file:
        data = json.load(file)

    # Extract data for ADHD and Non-ADHD groups
    adhd_with = [entry['With Distraction'] for entry in data['ADHD']]
    adhd_without = [entry['Without Distraction'] for entry in data['ADHD']]
    non_adhd_with = [entry['With Distraction'] for entry in data['Non-ADHD']]
    non_adhd_without = [entry['Without Distraction'] for entry in data['Non-ADHD']]

    # Perform statistical tests within each group (with vs without distraction)
    t_stat_adhd, p_val_adhd = stat_test(adhd_with, adhd_without, option='dep')
    t_stat_non_adhd, p_val_non_adhd = stat_test(non_adhd_with, non_adhd_without, option='dep')

    # Perform statistical tests between groups for each condition
    t_stat_between_with, p_val_between_with = stat_test(adhd_with, non_adhd_with, option='indep')
    t_stat_between_without, p_val_between_without = stat_test(adhd_without, non_adhd_without, option='indep')

    # Calculate mean and standard deviation
    adhd_mean_w, adhd_std_w = np.mean(adhd_with), np.std(adhd_with)
    adhd_mean_wo, adhd_std_wo = np.mean(adhd_without), np.std(adhd_without)
    non_adhd_mean_w, non_adhd_std_w = np.mean(non_adhd_with), np.std(non_adhd_with)
    non_adhd_mean_wo, non_adhd_std_wo = np.mean(non_adhd_without), np.std(non_adhd_without)

    # Structure results in the same format as the accuracy analyzer
    return {
        "p_value": {
            "within_group": {
                "title": "Pose Within-Group P-Value",
                "data": {
                    "ADHD": {
                        "Mean ± SD With Distraction": f"{adhd_mean_w:.2f} ± {adhd_std_w:.2f}",
                        "Mean ± SD Without Distraction": f"{adhd_mean_wo:.2f} ± {adhd_std_wo:.2f}",
                        "p_value_within": p_val_adhd
                    },
                    "Non-ADHD": {
                        "Mean ± SD With Distraction": f"{non_adhd_mean_w:.2f} ± {non_adhd_std_w:.2f}",
                        "Mean ± SD Without Distraction": f"{non_adhd_mean_wo:.2f} ± {non_adhd_std_wo:.2f}",
                        "p_value_within": p_val_non_adhd
                    }
                }
            },
            "between_group": {
                "title": "Pose Between-Group P-Value",
                "data": {
                    "With Distraction": {
                        "ADHD Mean ± SD": f"{adhd_mean_w:.2f} ± {adhd_std_w:.2f}",
                        "Non-ADHD Mean ± SD": f"{non_adhd_mean_w:.2f} ± {non_adhd_std_w:.2f}",
                        "p_value_between": p_val_between_with
                    },
                    "Without Distraction": {
                        "ADHD Mean ± SD": f"{adhd_mean_wo:.2f} ± {adhd_std_wo:.2f}",
                        "Non-ADHD Mean ± SD": f"{non_adhd_mean_wo:.2f} ± {non_adhd_std_wo:.2f}",
                        "p_value_between": p_val_between_without
                    }
                }
            }
        }
    }
