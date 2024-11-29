import os
import json
import pandas as pd
import pickle
import numpy as np
from utils.constants import EXCLUDED_PARTICIPANTS

def preprocess_cumulative_pose_stability(baseDir):
    """
    Preprocess cumulative pose stability data and save it to a JSON file.

    Parameters:
    - baseDir: Base directory containing pose data and participant information.
    """
    # Load participant data
    pre_experiment_file = os.path.join(baseDir, "Pre-Experiment Questionnaire.csv")
    pre_experiment_df = pd.read_csv(pre_experiment_file)

    # Extract gender and ADHD groups
    gender_groups = {
        "ADHD_Male": pre_experiment_df[
            (pre_experiment_df['Gender'] == 'Male') & (pre_experiment_df['ADHD Indication'] == True)
        ]['Participant number:'].tolist(),
        "ADHD_Female": pre_experiment_df[
            (pre_experiment_df['Gender'] == 'Female') & (pre_experiment_df['ADHD Indication'] == True)
        ]['Participant number:'].tolist(),
        "NonADHD_Male": pre_experiment_df[
            (pre_experiment_df['Gender'] == 'Male') & (pre_experiment_df['ADHD Indication'] == False)
        ]['Participant number:'].tolist(),
        "NonADHD_Female": pre_experiment_df[
            (pre_experiment_df['Gender'] == 'Female') & (pre_experiment_df['ADHD Indication'] == False)
        ]['Participant number:'].tolist()
    }

    # Remove excluded participants
    for group in gender_groups:
        gender_groups[group] = [pid for pid in gender_groups[group] if pid not in EXCLUDED_PARTICIPANTS]

    cumulative_pose_stability = {group: {} for group in gender_groups}

    # Process pose data for each participant
    for group, participants in gender_groups.items():
        for participant_id in participants:
            participant_scores = []
            for session in range(3, 9):  # Sessions 3 to 8
                pose_file_path = os.path.join(
                    baseDir, f'Pose/threshold_15/P{participant_id}/expt_{participant_id}_session_{session}_list.pkl'
                )
                try:
                    with open(pose_file_path, 'rb') as file:
                        poses = pickle.load(file)

                    total_frames = len(poses)
                    pose_changes = sum(1 for i in range(1, total_frames) if poses[i] != poses[i - 1])
                    score = (1 - (pose_changes / total_frames)) * 100 if total_frames > 0 else 0

                    participant_scores.append(score)

                except FileNotFoundError:
                    print(f"Pose data file not found: {pose_file_path}")
                except Exception as e:
                    print(f"Error processing file {pose_file_path}: {e}")

            if participant_scores:
                cumulative_score = sum(participant_scores) / len(participant_scores)
                cumulative_pose_stability[group][str(participant_id)] = cumulative_score

    # Aggregate group accuracies (mean ± std)
    aggregated_pose_stability = {}
    for group, participants in cumulative_pose_stability.items():
        scores = list(participants.values())
        mean_score = np.mean(scores)
        std_score = np.std(scores)
        aggregated_pose_stability[group] = f"{mean_score:.2f} ± {std_score:.2f}"

    # Save to JSON
    output_data = {
        "cumulative_pose_stability": cumulative_pose_stability,
        "aggregated_pose_stability": aggregated_pose_stability
    }
    output_file = os.path.join('../backend/results/pose', 'cumulative_gender_pose_stability.json')
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w") as json_file:
        json.dump(output_data, json_file, indent=4)
    print(f"Cumulative pose stability saved to {output_file}")
