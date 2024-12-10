import os
import json
import pandas as pd
from preprocessor.accuracys_stats_preprocessor import preprocess_accuracy_stat
from utils.constants import EXCLUDED_PARTICIPANTS

def extractErrors(file_path):
    """Extract errors from response time text files."""
    file_path = os.path.expanduser(file_path)
    with open(file_path, 'r') as file:
        content = file.read()

    data_content, distraction_content = content.split('Distraction Data:')
    data = json.loads(data_content)
    
    incorrect_pass_list = []
    incorrect_click_list = []

    for key, entry in data.items():
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

def extractParticipant(baseDir, startExptNum, endExptNum, session, adhd_list, non_adhd_list, n=12):
    """Extract participant accuracy data in blocks of size 'n'."""
    num_blocks = 120 // n  # Calculate the number of blocks based on 'n'
    session_scores = {
        'ADHD': {'w': [0] * num_blocks, 'wo': [0] * num_blocks},
        'Non-ADHD': {'w': [0] * num_blocks, 'wo': [0] * num_blocks}
    }

    for e in range(startExptNum, endExptNum + 1):
        if e in EXCLUDED_PARTICIPANTS:
            continue
        
        currentPath = os.path.join(baseDir, f'Accuracy/P{e}/expt_{e}_session_{session}_Response_Time.txt')
        incorrect_click, incorrect_pass = extractErrors(currentPath)

        # Calculate accuracy in blocks of 'n' trials
        for i in range(0, 120, n):
            block_pass = incorrect_pass[i:i + n]
            block_click = incorrect_click[i:i + n]
            total_errors = sum(block_pass) + sum(block_click)
            accuracy_score = n - total_errors

            participant_type = 'ADHD' if e in adhd_list else 'Non-ADHD'
            if session in [1, 4, 5, 8]:  # 'w' sessions
                session_scores[participant_type]['w'][i // n] += accuracy_score
            else:  # 'wo' sessions
                session_scores[participant_type]['wo'][i // n] += accuracy_score

    return session_scores

def computeTotalAccuracy(baseDir, startExptNum, endExptNum, adhd_list, non_adhd_list, n=12):
    """Compute total accuracy for all sessions."""
    # Update normalization factors based on the number of participants
    adhd_count = 26
    non_adhd_count = 26

    all_sessions_scores = {
        'ADHD': {},
        'Non-ADHD': {}
    }

    # Initialize dictionaries for each session
    for participant_type in ['ADHD', 'Non-ADHD']:
        for session in range(1, 9):
            num_blocks = 120 // n
            all_sessions_scores[participant_type][f'Session {session}'] = {'w': [0] * num_blocks, 'wo': [0] * num_blocks}

    # Iterate over sessions 1 to 8
    for session in range(1, 9):
        session_scores = extractParticipant(baseDir, startExptNum, endExptNum, session, adhd_list, non_adhd_list, n)
        
        # Accumulate scores for each session and participant type
        for participant_type in ['ADHD', 'Non-ADHD']:
            num_blocks = len(session_scores[participant_type]['w'])
            for i in range(num_blocks):
                all_sessions_scores[participant_type][f'Session {session}']['w'][i] += session_scores[participant_type]['w'][i]
                all_sessions_scores[participant_type][f'Session {session}']['wo'][i] += session_scores[participant_type]['wo'][i]

    # Normalize the scores to percentages
    for participant_type in ['ADHD', 'Non-ADHD']:
        normalization_factor = adhd_count if participant_type == 'ADHD' else non_adhd_count
        print(normalization_factor)
        for session in range(1, 9):
            num_blocks = len(all_sessions_scores[participant_type][f'Session {session}']['w'])
            for i in range(num_blocks):
                all_sessions_scores[participant_type][f'Session {session}']['w'][i] *= (100 / (normalization_factor * n))
                all_sessions_scores[participant_type][f'Session {session}']['wo'][i] *= (100 / (normalization_factor * n))

    return all_sessions_scores

def preprocess_and_save_trendlines(baseDir, pre_experiment_file):
    """Generate trendline accuracy files for n=12 and n=120."""
    # Load ADHD and Non-ADHD participant lists
    pre_experiment_df = pd.read_csv(pre_experiment_file)
    adhd_list = pre_experiment_df[pre_experiment_df['ADHD Indication'] == True]['Participant number:'].tolist()
    non_adhd_list = pre_experiment_df[pre_experiment_df['ADHD Indication'] == False]['Participant number:'].tolist()
      
    # Generate accuracy data for n=12 and n=120
    for n in [12, 120]:
        accuracy_data = computeTotalAccuracy(baseDir, 1, 59, adhd_list, non_adhd_list, n=n)
        # Save to file
        filename = f"../backend/results/accuracy/trendline_accuracy_{n}.json"
        absolute_csv_path = os.path.abspath(filename)
        with open(absolute_csv_path, 'w') as outfile:
            json.dump(accuracy_data, outfile, indent=4)
        print(f"../results/Trendline accuracy data saved to '{filename}'.")
        
def preprocess_accuracy_trend(baseDir):
    PRE_EXPERIMENT_FILE = baseDir + "/Pre-Experiment Questionnaire.csv"
    preprocess_and_save_trendlines(baseDir, PRE_EXPERIMENT_FILE)
    preprocess_accuracy_stat(baseDir=baseDir)
