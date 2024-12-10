import os
import json
import pandas as pd
from utils.constants import EXCLUDED_PARTICIPANTS

def extractErrors(file_path):
    """
    Extract errors (Incorrect Pass and Incorrect Click) from a response time file.

    Parameters:
    - file_path: Path to the response time file.

    Returns:
    - incorrect_click_list: List of incorrect clicks.
    - incorrect_pass_list: List of incorrect passes.
    """
    with open(file_path, 'r') as file:
        content = file.read()

    data_content, _ = content.split('Distraction Data:')
    data = json.loads(data_content)

    incorrect_click_list = []
    incorrect_pass_list = []

    for entry in data.values():
        if entry["Evaluation"] == "Incorrect Pass":
            incorrect_pass_list.append(1)
            incorrect_click_list.append(0)
        elif entry["Evaluation"] == "Incorrect Click":
            incorrect_pass_list.append(0)
            incorrect_click_list.append(1)
        else:
            incorrect_pass_list.append(0)
            incorrect_click_list.append(0)

    return incorrect_click_list, incorrect_pass_list


def compute_cumulative_accuracy(baseDir, gender_groups):
    """
    Compute cumulative accuracy for each participant in each gender group from session 3 to session 8.

    Parameters:
    - baseDir: Base directory containing session data.
    - gender_groups: Dictionary of gender-based groups.

    Returns:
    - cumulative_accuracy: Dictionary containing cumulative accuracy data for each participant in each group.
    """
    cumulative_accuracy = {group: {} for group in gender_groups}

    for session in range(1, 9):  # Sessions 3 to 8
        for group, participants in gender_groups.items():
            for participant_id in participants:
                file_path = os.path.join(baseDir, f'Accuracy/P{participant_id}/expt_{participant_id}_session_{session}_Response_Time.txt')

                # Extract errors for the current participant and session
                incorrect_click, incorrect_pass = extractErrors(file_path)
                total_errors = sum(incorrect_click) + sum(incorrect_pass)
                trials = len(incorrect_click)  # Assuming each session has a fixed number of trials
                accuracy_percentage = ((trials - total_errors) / trials) * 100

                # Append the accuracy percentage to the participant's cumulative list
                if participant_id not in cumulative_accuracy[group]:
                    cumulative_accuracy[group][participant_id] = []
                cumulative_accuracy[group][participant_id].append(accuracy_percentage)

    # Compute the cumulative average for each participant across sessions
    for group, participants in cumulative_accuracy.items():
        for participant_id, accuracies in participants.items():
            cumulative_accuracy[group][participant_id] = sum(accuracies) / len(accuracies)  # Average accuracy

    return cumulative_accuracy


def aggregate_group_accuracies(cumulative_accuracy):
    """
    Aggregate cumulative accuracies to compute group averages and standard deviations.

    Parameters:
    - cumulative_accuracy: Dictionary containing cumulative accuracy data for each participant in each group.

    Returns:
    - aggregated_accuracy: Dictionary with mean ± std for each group.
    """
    aggregated_accuracy = {}
    for group, participants in cumulative_accuracy.items():
        accuracies = list(participants.values())
        mean_accuracy = sum(accuracies) / len(accuracies)
        std_accuracy = (sum((x - mean_accuracy) ** 2 for x in accuracies) / len(accuracies)) ** 0.5
        aggregated_accuracy[group] = f"{mean_accuracy:.2f} ± {std_accuracy:.2f}"

    return aggregated_accuracy


def save_cumulative_accuracy_to_json(baseDir, pre_experiment_csv, output_file="../backend/results/accuracy/cumulative_gender_accuracy.json"):
    """
    Save the cumulative accuracy for gender groups to a JSON file.

    Parameters:
    - baseDir: Base directory containing session data.
    - pre_experiment_csv: Path to the pre-experiment CSV file containing participant data.
    - output_file: Path to save the JSON output.
    """
    # Load participant data from pre-experiment CSV
    pre_experiment_df = pd.read_csv(pre_experiment_csv)

    # Extract gender and ADHD groups
    gender_groups = {
        "ADHD_Male": pre_experiment_df[(pre_experiment_df['Gender'] == 'Male') & (pre_experiment_df['ADHD Indication'] == True)]['Participant number:'].tolist(),
        "ADHD_Female": pre_experiment_df[(pre_experiment_df['Gender'] == 'Female') & (pre_experiment_df['ADHD Indication'] == True)]['Participant number:'].tolist(),
        "NonADHD_Male": pre_experiment_df[(pre_experiment_df['Gender'] == 'Male') & (pre_experiment_df['ADHD Indication'] == False)]['Participant number:'].tolist(),
        "NonADHD_Female": pre_experiment_df[(pre_experiment_df['Gender'] == 'Female') & (pre_experiment_df['ADHD Indication'] == False)]['Participant number:'].tolist()
    }
    for g in ["ADHD_Male", "ADHD_Female", "NonADHD_Male", "NonADHD_Female"]:
        gender_groups[g] = [e for e in gender_groups[g] if e not in EXCLUDED_PARTICIPANTS]

    # Compute cumulative accuracy for each participant
    cumulative_accuracy = compute_cumulative_accuracy(baseDir, gender_groups)

    # Aggregate group accuracies (mean ± std)
    aggregated_accuracy = aggregate_group_accuracies(cumulative_accuracy)

    # Save to JSON
    output_data = {
        "cumulative_accuracy": cumulative_accuracy,
        "aggregated_accuracy": aggregated_accuracy
    }
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w") as json_file:
        json.dump(output_data, json_file, indent=4)
    print(f"Cumulative accuracy saved to {output_file}")


def preprocess_cumulative_gender_accuracy(baseDir):
    PRE_EXPERIMENT_FILE = os.path.join(baseDir, "Pre-Experiment Questionnaire.csv")
    save_cumulative_accuracy_to_json(baseDir, PRE_EXPERIMENT_FILE)
