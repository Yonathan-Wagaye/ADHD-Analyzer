import os
import json
import pandas as pd
import pickle
from utils.constants import EXCLUDED_PARTICIPANTS


def read_pkl_file(base_path, num_experiments, num_sessions):
    """Read pickle files and return pose data for all experiments and sessions."""
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


def compute_pose_trendlines(base_dir, num_experiments, num_sessions, threshold, n):
    """Compute pose trendlines for a specific threshold and n value."""
    trendlines = {
        'ADHD': {f'Session {i}': [0] * (120 // n) for i in range(1, num_sessions + 1)},
        'Non-ADHD': {f'Session {i}': [0] * (120 // n) for i in range(1, num_sessions + 1)}
    }

    # Load participant classifications
    pre_experiment_file = os.path.join(base_dir, "Pre-Experiment Questionnaire.csv")
    pre_experiment_df = pd.read_csv(pre_experiment_file)
    adhd_list = pre_experiment_df[pre_experiment_df['ADHD Indication'] == True]['Participant number:'].tolist()
    non_adhd_list = pre_experiment_df[pre_experiment_df['ADHD Indication'] == False]['Participant number:'].tolist()

    adhd_list = [pid for pid in adhd_list if pid not in EXCLUDED_PARTICIPANTS]
    non_adhd_list = [pid for pid in non_adhd_list if pid not in EXCLUDED_PARTICIPANTS]

    # Read pose data
    threshold_path = os.path.join(base_dir, f"Pose/threshold_{threshold}")
    pose_data = read_pkl_file(threshold_path, num_experiments, num_sessions)

    # Process pose data
    for experiment in range(1, num_experiments + 1):
        if experiment in EXCLUDED_PARTICIPANTS:
            continue

        for session in range(1, num_sessions + 1):
            key = f'e_{experiment}_s_{session}'
            if key not in pose_data:
                continue

            poses = pose_data[key]
            total_frames = len(poses)
            block_scores = []

            for i in range(0, 120, n):
                block_poses = poses[i:i + n]
                block_changes = sum(1 for j in range(1, len(block_poses)) if block_poses[j] != block_poses[j - 1])
                block_score = 1 - (block_changes / len(block_poses)) if len(block_poses) > 0 else 0
                block_scores.append(block_score)

            participant_type = 'ADHD' if experiment in adhd_list else 'Non-ADHD'
            for i, score in enumerate(block_scores):
                trendlines[participant_type][f'Session {session}'][i] += score

    # Normalize scores
    adhd_count = len(adhd_list)
    non_adhd_count = len(non_adhd_list)
    for participant_type in ['ADHD', 'Non-ADHD']:
        count = adhd_count if participant_type == 'ADHD' else non_adhd_count
        for session in range(1, num_sessions + 1):
            for i in range(len(trendlines[participant_type][f'Session {session}'])):
                trendlines[participant_type][f'Session {session}'][i] *= (100 / count)

    return trendlines


def preprocess_and_save_pose_trendlines(base_dir, num_experiments=59, num_sessions=8, threshold=15):
    """Preprocess and save pose trendline data for n=12 and n=120."""
    for n in [12, 120]:
        trendlines = compute_pose_trendlines(base_dir, num_experiments, num_sessions, threshold, n)
        output_file = f"../backend/results/pose/pose_trendline_{n}_threshold_{threshold}.json"
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w') as outfile:
            json.dump(trendlines, outfile, indent=4)
        print(f"Saved pose trendline data to {output_file}")
