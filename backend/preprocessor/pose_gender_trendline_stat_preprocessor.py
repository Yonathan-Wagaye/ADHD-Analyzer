import os
import json
import pandas as pd
import pickle
from utils.constants import EXCLUDED_PARTICIPANTS


def read_pkl_file(base_path, num_experiments, num_sessions):
    """
    Read pose data pickle files for all participants and sessions.
    """
    final_data = {}
    for i in range(1, num_experiments + 1):
        if i in EXCLUDED_PARTICIPANTS:
            continue
        for j in range(1, num_sessions + 1):
            filename = os.path.expanduser(f"{base_path}/P{i}/expt_{i}_session_{j}_list.pkl")
            try:
                with open(filename, 'rb') as file:
                    data = pickle.load(file)
                final_data[f'e_{i}_s_{j}'] = data
            except FileNotFoundError as e:
                print(f"File not found: {filename}")
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
    return final_data


def preprocess_pose_stability_by_gender(baseDir, num_experiments=59, num_sessions=8, threshold=15, n=120):
    """
    Preprocess pose stability data and save it to JSON files organized by gender groups.
    """
    # Load participant information
    pre_experiment_file = os.path.join(baseDir, "Pre-Experiment Questionnaire.csv")
    pre_experiment_df = pd.read_csv(pre_experiment_file)

    # Extract gender and ADHD groups
    gender_groups = {
        "M-ADHD": pre_experiment_df[
            (pre_experiment_df['Gender'] == 'Male') & (pre_experiment_df['ADHD Indication'] == True)
        ]['Participant number:'].tolist(),
        "F-ADHD": pre_experiment_df[
            (pre_experiment_df['Gender'] == 'Female') & (pre_experiment_df['ADHD Indication'] == True)
        ]['Participant number:'].tolist(),
        "M-nonADHD": pre_experiment_df[
            (pre_experiment_df['Gender'] == 'Male') & (pre_experiment_df['ADHD Indication'] == False)
        ]['Participant number:'].tolist(),
        "F-nonADHD": pre_experiment_df[
            (pre_experiment_df['Gender'] == 'Female') & (pre_experiment_df['ADHD Indication'] == False)
        ]['Participant number:'].tolist()
    }

    # Remove excluded participants
    for group in gender_groups:
        gender_groups[group] = [pid for pid in gender_groups[group] if pid not in EXCLUDED_PARTICIPANTS]

    # Read pose data
    threshold_path = os.path.join(baseDir, f"Pose/threshold_{threshold}")
    pose_data = read_pkl_file(threshold_path, num_experiments, num_sessions)

    # Initialize data structure
    gender_pose_data = {
        group: {f"Session {i}": [[] for _ in range(120 // n)] for i in range(1, num_sessions + 1)}
        for group in gender_groups
    }

    # Process data
    for experiment in range(1, num_experiments + 1):
        if experiment in EXCLUDED_PARTICIPANTS:
            continue

        group = None
        for g, participants in gender_groups.items():
            if experiment in participants:
                group = g
                break
        if not group:
            continue

        for session in range(1, num_sessions + 1):
            key = f'e_{experiment}_s_{session}'
            if key not in pose_data:
                continue

            poses = pose_data[key]
            for i in range(0, 120, n):
                block_poses = poses[i:i + n]
                if not block_poses:
                    continue
                pose_changes = sum(1 for j in range(1, len(block_poses)) if block_poses[j] != block_poses[j - 1])
                score = 100 * (1 - pose_changes / len(block_poses))
                gender_pose_data[group][f'Session {session}'][i // n].append(score)

    # Save results to JSON
    output_path = "../backend/results/pose/pose_trendline_gender_stat_120_threshold_15.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as outfile:
        json.dump(gender_pose_data, outfile, indent=4)
    print(f"Pose stability data saved to {output_path}")
