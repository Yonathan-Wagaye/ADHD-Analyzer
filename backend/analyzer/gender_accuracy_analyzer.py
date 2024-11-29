from utils.stat_tests import stat_test, chi_square_test
import json
import numpy as np



def analyze_pvalues_from_json(json_file):
    """
    Analyze p-values for different group comparisons from a JSON file.

    Parameters:
    - json_file: Path to the JSON file containing group-specific accuracy data.

    Returns:
    - results: Dictionary containing p-values and mean ± std for each comparison.
    """
    # Load the JSON data
    with open(json_file, 'r') as file:
        data = json.load(file)

    # Initialize results dictionary
    results = {
        "ADHD_Male_vs_ADHD_Female": {"p_values": {}, "mean_std": {}},
        "NonADHD_Male_vs_NonADHD_Female": {"p_values": {}, "mean_std": {}},
        "ADHD_Male_vs_NonADHD_Male": {"p_values": {}, "mean_std": {}},
        "ADHD_Female_vs_NonADHD_Female": {"p_values": {}, "mean_std": {}},
    }

    # Perform comparisons for each session
    for session in range(1, 9):
        session_key = f"Session {session}"

        # Extract data for each group
        adhd_male_scores = data["M-ADHD"][session_key]["w"][0] + data["M-ADHD"][session_key]["wo"][0]
        non_adhd_male_scores = data["M-nonADHD"][session_key]["w"][0] + data["M-nonADHD"][session_key]["wo"][0]
        adhd_female_scores = data["F-ADHD"][session_key]["w"][0] + data["F-ADHD"][session_key]["wo"][0]
        non_adhd_female_scores = data["F-nonADHD"][session_key]["w"][0] + data["F-nonADHD"][session_key]["wo"][0]

        # ADHD Male vs ADHD Female
        _, p_val = stat_test(adhd_male_scores, adhd_female_scores)
        results["ADHD_Male_vs_ADHD_Female"]["p_values"][session_key] = p_val
        results["ADHD_Male_vs_ADHD_Female"]["mean_std"][session_key] = {
            "ADHD_Male": f"{np.mean(adhd_male_scores):.2f} ± {np.std(adhd_male_scores):.2f}",
            "ADHD_Female": f"{np.mean(adhd_female_scores):.2f} ± {np.std(adhd_female_scores):.2f}"
        }

        # Non-ADHD Male vs Non-ADHD Female
        _, p_val = stat_test(non_adhd_male_scores, non_adhd_female_scores)
        results["NonADHD_Male_vs_NonADHD_Female"]["p_values"][session_key] = p_val
        results["NonADHD_Male_vs_NonADHD_Female"]["mean_std"][session_key] = {
            "NonADHD_Male": f"{np.mean(non_adhd_male_scores):.2f} ± {np.std(non_adhd_male_scores):.2f}",
            "NonADHD_Female": f"{np.mean(non_adhd_female_scores):.2f} ± {np.std(non_adhd_female_scores):.2f}"
        }

        # ADHD Male vs Non-ADHD Male
        _, p_val = stat_test(adhd_male_scores, non_adhd_male_scores)
        results["ADHD_Male_vs_NonADHD_Male"]["p_values"][session_key] = p_val
        results["ADHD_Male_vs_NonADHD_Male"]["mean_std"][session_key] = {
            "ADHD_Male": f"{np.mean(adhd_male_scores):.2f} ± {np.std(adhd_male_scores):.2f}",
            "NonADHD_Male": f"{np.mean(non_adhd_male_scores):.2f} ± {np.std(non_adhd_male_scores):.2f}"
        }

        # ADHD Female vs Non-ADHD Female
        _, p_val = stat_test(adhd_female_scores, non_adhd_female_scores)
        results["ADHD_Female_vs_NonADHD_Female"]["p_values"][session_key] = p_val
        results["ADHD_Female_vs_NonADHD_Female"]["mean_std"][session_key] = {
            "ADHD_Female": f"{np.mean(adhd_female_scores):.2f} ± {np.std(adhd_female_scores):.2f}",
            "NonADHD_Female": f"{np.mean(non_adhd_female_scores):.2f} ± {np.std(non_adhd_female_scores):.2f}"
        }

    return results


# Analyze the JSON file and print results


def analyze_gender_accuracy():
    print("before result")
    result = analyze_pvalues_from_json("results/accuracy/gender_stat_accuracy.json")
    return result