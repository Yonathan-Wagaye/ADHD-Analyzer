import os
import json
import pandas as pd
import pickle
import numpy as np
from utils.constants import EXCLUDED_PARTICIPANTS


def extract_pose_scores(base_path, session, participants, threshold, n=120):
    """
    Extract pose stability scores for a given session and list of participants.
    """
    num_blocks = 120 // n
    session_scores = {'w': [[] for _ in range(num_blocks)], 'wo': [[] for _ in range(num_blocks)]}

    for participant_id in participants:
        if participant_id in EXCLUDED_PARTICIPANTS:
            continue
        file_path = os.path.join(base_path, f"Pose/threshold_{threshold}/P{participant_id}/expt_{participant_id}_session_{session}_list.pkl")
        try:
            with open(file_path, 'rb') as file:
                poses = pickle.load(file)

            for i in range(0, 120, n):
                block_poses = poses[i:i + n]
                total_frames = len(block_poses)
                pose_changes = sum(1 for j in range(1, total_frames) if block_poses[j] != block_poses[j - 1])
                score = (1 - (pose_changes / total_frames)) * 100 if total_frames > 0 else 0

                if session in [4, 5, 8]:  # 'w' sessions
                    session_scores['w'][i // n].append(score)
                else:  # 'wo' sessions
                    session_scores['wo'][i // n].append(score)

        except FileNotFoundError:
            print(f"File not found: {file_path}")
        except Exception as e:
            print(f"Error processing {file_path}: {e}")

    return session_scores


def compute_pose_group_scores(base_path, participants, thresholds, n=120):
    """
    Compute pose scores for all sessions and thresholds.
    """
    pose_scores = {threshold: {group: {f"Session {i}": {'w': [[] for _ in range(120 // n)], 'wo': [[] for _ in range(120 // n)]}
                                      for i in range(1, 9)}
                               for group in participants}
                   for threshold in thresholds}

    for threshold in thresholds:
        for group, participant_ids in participants.items():
            for session in range(1, 9):  # Sessions 1 to 8
                session_scores = extract_pose_scores(base_path, session, participant_ids, threshold, n)
                for block_index in range(len(session_scores['w'])):
                    pose_scores[threshold][group][f"Session {session}"]['w'][block_index].extend(session_scores['w'][block_index])
                    pose_scores[threshold][group][f"Session {session}"]['wo'][block_index].extend(session_scores['wo'][block_index])

    return pose_scores


def save_pose_scores_to_json(base_path, pre_experiment_csv, output_dir, thresholds, n=120):
    """
    Save computed pose scores to JSON for analysis.
    """
    pre_experiment_df = pd.read_csv(pre_experiment_csv)
    participants = {
        "ADHD": pre_experiment_df[pre_experiment_df["ADHD Indication"] == True]["Participant number:"].tolist(),
        "Non-ADHD": pre_experiment_df[pre_experiment_df["ADHD Indication"] == False]["Participant number:"].tolist()
    }

    pose_scores = compute_pose_group_scores(base_path, participants, thresholds, n)

    os.makedirs(output_dir, exist_ok=True)
    for threshold, data in pose_scores.items():
        output_file = os.path.join(output_dir, f"pose_trendline_stats_threshold_{threshold}.json")
        with open(output_file, "w") as json_file:
            json.dump(data, json_file, indent=4)
        print(f"Saved pose trendline stats to {output_file}")


def preprocess_pose_trendline_stats(base_dir):
    """
    Preprocess pose data for p-value analysis and save results.
    """
    pre_experiment_csv = os.path.join(base_dir, "Pre-Experiment Questionnaire.csv")
    output_dir = '../backend/results/pose'
    thresholds = [15]
    save_pose_scores_to_json(base_dir, pre_experiment_csv, output_dir, thresholds)
