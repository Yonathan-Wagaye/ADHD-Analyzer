import os
import pickle
import pandas as pd
import json
from utils.constants import EXCLUDED_PARTICIPANTS

def get_participant_groups(pre_experiment_csv):
    """
    Extract ADHD and Non-ADHD participant IDs from the Pre-Experiment Questionnaire CSV file.

    Parameters:
    - pre_experiment_csv: Path to the Pre-Experiment Questionnaire CSV file.

    Returns:
    - adhd_participants: List of participant IDs with ADHD.
    - non_adhd_participants: List of participant IDs without ADHD.
    """
    df = pd.read_csv(pre_experiment_csv)
    adhd_participants = df[df['ADHD Indication'] == True]['Participant number:'].tolist()
    non_adhd_participants = df[df['ADHD Indication'] == False]['Participant number:'].tolist()

    # Exclude participants from the EXCLUDED_PARTICIPANTS list
    adhd_participants = [p for p in adhd_participants if p not in EXCLUDED_PARTICIPANTS]
    non_adhd_participants = [p for p in non_adhd_participants if p not in EXCLUDED_PARTICIPANTS]

    return adhd_participants, non_adhd_participants


def read_pkl_file(base_path, participants, num_sessions):
    """
    Read pose data pickle files for specified participants and sessions.

    Parameters:
    - base_path: Base directory containing pose data.
    - participants: List of participant IDs to process.
    - num_sessions: Total number of sessions to process.

    Returns:
    - final_data: Dictionary containing pose data for each participant and session.
    """
    final_data = {}
    for participant in participants:
        for session in range(1, num_sessions + 1):  # Only sessions 3 to 8
            filename = os.path.expanduser(f"{base_path}/P{participant}/expt_{participant}_session_{session}_list.pkl")
            try:
                with open(filename, 'rb') as file:
                    data = pickle.load(file)
                final_data[f'e_{participant}_s_{session}'] = data
            except FileNotFoundError:
                print(f"File not found: {filename}")
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
    return final_data


def calculate_cumulative_pose_scores(data, participants, num_sessions):
    """
    Calculate cumulative pose stability scores for participants.

    Parameters:
    - data: Dictionary containing pose data.
    - participants: List of participant IDs.
    - num_sessions: Total number of sessions.

    Returns:
    - cumulative_scores: List of cumulative scores for each participant.
    """
    cumulative_scores = []

    for participant in participants:
        w_scores = []
        wo_scores = []

        for session in range(1, num_sessions + 1):  # Sessions 3 to 8
            poses = data.get(f'e_{participant}_s_{session}', [])
            total_frames = len(poses)

            pose_changes = sum(1 for j in range(1, total_frames) if poses[j] != poses[j - 1])

            score = 100 * (1 - (pose_changes / total_frames)) if total_frames > 0 else 0

            if session in [1, 4, 5, 8]:  # With distraction
                w_scores.append(score)
            else:  # Without distraction
                wo_scores.append(score)

        cumulative_scores.append({
            "Participant": participant,
            "With Distraction": sum(w_scores) / len(w_scores) if w_scores else 0,
            "Without Distraction": sum(wo_scores) / len(wo_scores) if wo_scores else 0
        })

    return cumulative_scores


def save_pose_scores_to_json(output_folder, threshold, adhd_scores, non_adhd_scores):
    """
    Save pose stability scores to a JSON file.

    Parameters:
    - output_folder: Directory to save the JSON file.
    - threshold: Threshold value for the pose analysis.
    - adhd_scores: List of cumulative scores for ADHD participants.
    - non_adhd_scores: List of cumulative scores for Non-ADHD participants.
    """
    os.makedirs(output_folder, exist_ok=True)
    output_path = os.path.join(output_folder, f"pose_scores_threshold_{threshold}.json")
    result = {
        "ADHD": adhd_scores,
        "Non-ADHD": non_adhd_scores
    }
    with open(output_path, 'w') as file:
        json.dump(result, file, indent=4)
    print(f"Saved pose scores to {output_path}")


def preprocess_pose(baseDir,  output_folder='../backend/results/pose', num_experiments=59, num_sessions=8, thresholds=[15]):
    """
    Preprocess pose data and save cumulative scores to JSON files.

    Parameters:
    - base_path: Base directory containing pose data.
    - pre_experiment_csv: Path to the Pre-Experiment Questionnaire CSV file.
    - output_folder: Directory to save output JSON files.
    - num_experiments: Total number of experiments (participants).
    - num_sessions: Total number of sessions.
    - thresholds: List of thresholds for pose data.
    """
    pre_experiment_csv = os.path.join(baseDir, "Pre-Experiment Questionnaire.csv")
    adhd_participants, non_adhd_participants = get_participant_groups(pre_experiment_csv)

    for threshold in thresholds:
        threshold_path = os.path.join(baseDir, f"Pose/threshold_{threshold}")

        # Read data
        adhd_data = read_pkl_file(threshold_path, adhd_participants, num_sessions)
        non_adhd_data = read_pkl_file(threshold_path, non_adhd_participants, num_sessions)

        # Calculate cumulative scores
        adhd_scores = calculate_cumulative_pose_scores(adhd_data, adhd_participants, num_sessions)
        non_adhd_scores = calculate_cumulative_pose_scores(non_adhd_data, non_adhd_participants, num_sessions)

        # Save results to JSON
        save_pose_scores_to_json(output_folder, threshold, adhd_scores, non_adhd_scores)
