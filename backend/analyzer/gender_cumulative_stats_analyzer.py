from utils.stat_tests import stat_test
import json
import numpy as np

def analyze_cumulative_pvalues_from_json(json_file):
    """
    Analyze p-values and compute mean ± std for cumulative accuracy between gender group comparisons.

    Parameters:
    - json_file: Path to the JSON file containing cumulative accuracy data.

    Returns:
    - results: Dictionary containing p-values and mean ± std for each comparison.
    """
    # Load the JSON data
    with open(json_file, 'r') as file:
        data = json.load(file)["cumulative_accuracy"]

    # Initialize results dictionary
    results = {
        "ADHD_Male_vs_ADHD_Female": {"p_value": None, "mean_std": {}},
        "NonADHD_Male_vs_NonADHD_Female": {"p_value": None, "mean_std": {}},
        "ADHD_Male_vs_NonADHD_Male": {"p_value": None, "mean_std": {}},
        "ADHD_Female_vs_NonADHD_Female": {"p_value": None, "mean_std": {}},
    }

    # Define comparisons
    comparisons = [
        ("ADHD_Male", "ADHD_Female", "ADHD_Male_vs_ADHD_Female"),
        ("NonADHD_Male", "NonADHD_Female", "NonADHD_Male_vs_NonADHD_Female"),
        ("ADHD_Male", "NonADHD_Male", "ADHD_Male_vs_NonADHD_Male"),
        ("ADHD_Female", "NonADHD_Female", "ADHD_Female_vs_NonADHD_Female"),
    ]

    # Perform comparisons
    for group1, group2, comparison_key in comparisons:
        # Extract scores for each group
        group1_scores = list(data[group1].values())  # Scores are stored as participant-level data
        group2_scores = list(data[group2].values())

        # Perform statistical test
        _, p_val = stat_test(group1_scores, group2_scores)

        # Calculate mean and standard deviation
        group1_mean = np.mean(group1_scores)
        group1_std = np.std(group1_scores)
        group2_mean = np.mean(group2_scores)
        group2_std = np.std(group2_scores)

        # Store results
        results[comparison_key]["p_value"] = p_val
        results[comparison_key]["mean_std"] = {
            f"{group1.replace('-', '_')}": f"{group1_mean:.2f} ± {group1_std:.2f}",
            f"{group2.replace('-', '_')}": f"{group2_mean:.2f} ± {group2_std:.2f}"
        }

    return results


def analyze_cumulative_gender_accuracy():
    """
    Wrapper function to analyze cumulative gender accuracy and return results.

    Returns:
    - results: Dictionary containing p-values and mean ± std for each comparison.
    """
    print("Analyzing cumulative gender accuracy...")
    results = analyze_cumulative_pvalues_from_json("results/accuracy/cumulative_gender_accuracy.json")
    return results
