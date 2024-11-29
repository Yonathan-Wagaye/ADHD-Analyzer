from utils.stat_tests import stat_test, chi_square_test
import os
import json
import pandas as pd

def analyze_session_accuracy(json_file):
    """
    Reads a JSON file containing session-wise ADHD and Non-ADHD accuracies, 
    performs statistical tests for each session, and outputs the p-values.

    Parameters:
    - json_file: Path to the JSON file.

    Returns:
    - p_values: Dictionary of p-values for each session.
    """
    # Load the JSON file
    with open(json_file, 'r') as file:
        data = json.load(file)

    p_values = {}

    # Perform statistical test for each session
    for session, scores in data.items():
        adhd_scores = [block for participant in scores['ADHD'] for block in participant]
        non_adhd_scores = [block for participant in scores['Non-ADHD'] for block in participant]

        # Perform the statistical test
        _, p_val = stat_test(adhd_scores, non_adhd_scores)
        p_values[session] = p_val

    return p_values

def save_p_values_to_json(p_values, output_file="../backend/results/accuracy/trendline_accuracy_pValue.json"):
    """
    Saves the computed p-values to a JSON file.

    Parameters:
    - p_values: Dictionary containing session-wise p-values.
    - output_file: Path to the output JSON file.
    """
    with open(output_file, 'w') as file:
        json.dump(p_values, file, indent=4)
    print(f"P-values saved to {output_file}.")

def analyze_chi_square(json_file):
    """
    Reads a JSON file containing session-wise ADHD and Non-ADHD accuracies,
    organizes data into observed frequencies based on accuracy scores,
    and performs a chi-square analysis.

    Parameters:
    - json_file: Path to the JSON file.

    Returns:
    - chi_square_results: Dictionary of chi-square test results for each session.
    """
    # Load the JSON file
    with open(json_file, 'r') as file:
        data = json.load(file)

    chi_square_results = {}

    for session, scores in data.items():
        # Extract ADHD and Non-ADHD accuracies
        adhd_scores = [score for participant in scores['ADHD'] for score in participant]
        non_adhd_scores = [score for participant in scores['Non-ADHD'] for score in participant]

        # Calculate observed frequencies (rounding to nearest integer for discrete counts)
        adhd_observed = round(sum(adhd_scores))
        non_adhd_observed = round(sum(non_adhd_scores))

        # Total counts (assumes equal distribution across groups as null hypothesis)
        total_observed = adhd_observed + non_adhd_observed
        expected = [total_observed / 2, total_observed / 2]

        # Observed frequencies
        observed = [adhd_observed, non_adhd_observed]

        # Perform chi-square test
        try:
            chi2, p_val = chi_square_test(observed, expected)
            chi_square_results[session] = {
                "chi2": chi2,
                "p_value": p_val,
                "observed": observed,
                "expected": expected
            }
        except ValueError as e:
            chi_square_results[session] = {
                "error": str(e),
                "observed": observed,
                "expected": expected
            }

    return chi_square_results



def save_chi_square_results(chi_square_results, output_file="../backend/results/accuracy/trendline_accuracy_chiSquare.json"):
    """
    Saves the computed chi-square results to a JSON file.

    Parameters:
    - chi_square_results: Dictionary containing session-wise chi-square results.
    - output_file: Path to the output JSON file.
    """
    with open(output_file, 'w') as file:
        json.dump(chi_square_results, file, indent=4)
    print(f"Chi-square results saved to {output_file}.")


def analyze_accruacy_pvalues(acc_json_file):
    p_values = analyze_session_accuracy(acc_json_file)
    return p_values

def analyze_accuracy_chiSquare():
    print('hello')
    chi_square_results = analyze_chi_square('../backend/results/accuracy/stat_accuracy.json')
    return chi_square_results