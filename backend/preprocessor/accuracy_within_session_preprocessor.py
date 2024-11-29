# preprocessor/accuracy_within_session_preprocessor.py

import os
import pandas as pd
import json
import re
from utils.constants import EXCLUDED_PARTICIPANTS

def calculate_adhd_score(row):
    score = 0
    response_mapping_one = { 'Never': 0, 'Rarely': 0, 'Sometimes': 1, 'Often': 1, 'Very Often': 1}
    response_mapping_two = {'Never': 0, 'Rarely': 0, 'Sometimes': 0, 'Often': 1, 'Very Often': 1 }
    for q in ['Q0', 'Q1', 'Q2']:
        score += response_mapping_one.get(row[q], 0)
    for q in ['Q3', 'Q4', 'Q5']:
        score += response_mapping_two.get(row[q], 0)
    return score

def process_pre_experiment_questionnaire(pre_expt_file_path):
    df = pd.read_csv(pre_expt_file_path)
    df = df.iloc[:, 2:]  # Adjust if needed based on your CSV structure

    new_columns = {df.columns[i+1]: f'Q{i}' for i in range(18)}
    df = df.rename(columns=new_columns)

    # Remove excluded participants
    df = df[~df['Participant number:'].isin(EXCLUDED_PARTICIPANTS)]

    df['Part_A_Score'] = df.apply(calculate_adhd_score, axis=1)
    df['ADHD_Indication'] = df['Part_A_Score'] >= 4
    return df[['Participant number:', 'ADHD_Indication']]

def read_distraction_data(base_dir, num_participants, num_sessions):
    all_data = {}
    for participant in range(1, num_participants + 1):
        if participant in EXCLUDED_PARTICIPANTS:
            continue
        participant_data = []
        for session in range(1, num_sessions + 1):
            filename = os.path.join(base_dir, f'P{participant}/expt_{participant}_session_{session}_Response_Time.txt')
            if os.path.exists(filename):
                with open(filename, 'r') as file:
                    content = file.read()
                start_index = content.find("Distraction Data:")
                if start_index != -1:
                    json_data = content[start_index + len("Distraction Data:"):].strip()
                    distraction_data = json.loads(json_data)
                    distractions = {
                        'Distraction Type': ['Yawn', 'Sneeze', 'Sing'],
                        'Time': [
                            distraction_data.get('yawn', ''),
                            distraction_data.get('sneeze', ''),
                            distraction_data.get('sing', '')
                        ]
                    }
                    distraction_df = pd.DataFrame(distractions)
                    distraction_df['Distraction Time'] = distraction_df['Time'].apply(
                        lambda x: re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', x).group(1)
                        if re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', x) else None
                    )
                    distraction_df['Trial Number'] = distraction_df['Time'].apply(
                        lambda x: int(re.search(r'\(trial: (\d+)\)', x).group(1))
                        if re.search(r'\(trial: (\d+)\)', x) else None
                    )
                    distraction_df.drop(columns=['Time'], inplace=True)
                    participant_data.append(distraction_df)
        if participant_data:
            all_data[f'Participant_{participant}'] = participant_data
    return all_data

def extract_errors(file_path, distraction_data, participant_id, session_index):
    incorrect_w = 0
    incorrect_wo = 0
    with open(file_path, 'r') as file:
        content = file.read()
    data_content, _ = content.split('Distraction Data:')
    data = json.loads(data_content)

    full_distraction_trials = []
    participant_key = f'Participant_{participant_id}'
    if participant_key in distraction_data and session_index < len(distraction_data[participant_key]):
        session_data = distraction_data[participant_key][session_index]
        for i in range(3):
            if i < len(session_data):
                distraction_point = session_data['Trial Number'][i]
                if pd.isna(distraction_point):
                    continue
                distraction_point = int(distraction_point)
                current_dist = distraction_point
                if i != 2:
                    full_distraction_trials.extend(range(current_dist, min(current_dist + 5, 121)))
                else:
                    full_distraction_trials.extend(range(current_dist, min(current_dist + 26, 121)))

    total_w_trials = len(full_distraction_trials)
    total_trials = 120
    total_wo_trials = total_trials - total_w_trials

    for key, entry in data.items():
        trial_num = int(key)
        if trial_num in full_distraction_trials:
            if entry["Evaluation"] in ["Incorrect Pass", "Incorrect Click"]:
                incorrect_w += 1
        else:
            if entry["Evaluation"] in ["Incorrect Pass", "Incorrect Click"]:
                incorrect_wo += 1

    accuracy_w = 1 - incorrect_w / total_w_trials if total_w_trials > 0 else 1
    accuracy_wo = 1 - incorrect_wo / total_wo_trials if total_wo_trials > 0 else 1

    return accuracy_w, accuracy_wo

def extract_all_participants(base_dir, distraction_data, num_participants, num_sessions):
    results = []
    for participant in range(1, num_participants + 1):
        if participant in EXCLUDED_PARTICIPANTS:
            continue
        accuracies_w = []
        accuracies_wo = []
        for session in range(1, num_sessions + 1):
            file_path = os.path.join(base_dir, f'P{participant}/expt_{participant}_session_{session}_Response_Time.txt')
            if os.path.exists(file_path):
                accuracy_w, accuracy_wo = extract_errors(file_path, distraction_data, participant, session - 1)
                accuracies_w.append(accuracy_w)
                accuracies_wo.append(accuracy_wo)
        total_accuracy_w = sum(accuracies_w) / len(accuracies_w) if accuracies_w else 0
        total_accuracy_wo = sum(accuracies_wo) / len(accuracies_wo) if accuracies_wo else 0

        results.append({
            'Participant number:': participant,
            'w_accuracy': total_accuracy_w,
            'wo_accuracy': total_accuracy_wo
        })
    return pd.DataFrame(results)

def preprocess_within_session_accuracy(base_dir, num_participants=59, num_sessions=8):
    distraction_data = read_distraction_data(base_dir, num_participants, num_sessions)
    accuracy_df = extract_all_participants(base_dir, distraction_data, num_participants, num_sessions)
    pre_expt_file_path = os.path.join(base_dir, 'Pre-Experiment Questionnaire.csv')
    pre_expt_df = process_pre_experiment_questionnaire(pre_expt_file_path)
    merged_df = pd.merge(pre_expt_df, accuracy_df, on='Participant number:')
    return merged_df

