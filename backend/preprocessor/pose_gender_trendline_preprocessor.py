import os
import pandas as pd
import json
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


def compute_pose_trendlines_by_gender(base_dir, num_experiments, num_sessions, thresholds, n):
    """Compute pose trendlines for all sessions, thresholds, and gender groups."""
    all_trendlines = {}
    pre_experiment_file = os.path.join(base_dir, "Pre-Experiment Questionnaire.csv")
    pre_experiment_df = pd.read_csv(pre_experiment_file)

    # Define gender groups
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

    for threshold in thresholds:
        threshold_path = os.path.join(base_dir, f"Pose/threshold_{threshold}")
        pose_data = read_pkl_file(threshold_path, num_experiments, num_sessions)

        session_scores = {
            group: {f'Session {i}': [0] * (120 // n) for i in range(1, num_sessions + 1)}
            for group in gender_groups
        }

        for experiment in range(1, num_experiments + 1):
            if experiment in EXCLUDED_PARTICIPANTS:
                continue

            participant_group = None
            for group, participants in gender_groups.items():
                if experiment in participants:
                    participant_group = group
                    break
            if participant_group is None:
                continue

            for session in range(1, num_sessions + 1):
                key = f'e_{experiment}_s_{session}'
                if key not in pose_data:
                    continue

                poses = pose_data[key]
                block_scores = [
                    1 - (sum(1 for j in range(1, len(poses[i:i + n])) if poses[i + j] != poses[i + j - 1]) / n)
                    for i in range(0, 120, n)
                ]

                for i, score in enumerate(block_scores):
                    session_scores[participant_group][f'Session {session}'][i] += score

        for group, participants in gender_groups.items():
            num_participants = len(participants)
            if num_participants == 0:
                continue
            for session in range(1, num_sessions + 1):
                for i in range(len(session_scores[group][f'Session {session}'])):
                    session_scores[group][f'Session {session}'][i] *= (100 / num_participants)

        all_trendlines[threshold] = session_scores

    return all_trendlines


def preprocess_and_save_pose_trendlines_by_gender(base_dir, num_experiments=59, num_sessions=8, thresholds=[15, 20, 25]):
    """Preprocess and save pose trendline data by gender for n=12 and n=120."""
    for n in [12, 120]:
        trendlines = compute_pose_trendlines_by_gender(base_dir, num_experiments, num_sessions, thresholds, n=n)
        for threshold, data in trendlines.items():
            output_file = f"../backend/results/pose/pose_trendline_gender_{n}_threshold_{threshold}.json"
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            with open(output_file, 'w') as outfile:
                json.dump(data, outfile, indent=4)
            print(f"Saved pose trendline data to {output_file}")
