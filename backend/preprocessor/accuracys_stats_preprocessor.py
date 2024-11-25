import os
import json
import pandas as pd

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




def extractParticipantAccuracy(baseDir, session, participants, adhd_list, n=120):
    """Extract accuracy data for a given session and list of participants."""
    num_blocks = 120 // n  # Calculate the number of blocks based on 'n'
    session_scores = {'ADHD': [], 'Non-ADHD': []}  # Store individual scores for analysis

    for participant_id in participants:
        if participant_id in [2, 5, 23, 24, 35, 36]:  # Skip specific participants if necessary
            continue
        
        currentPath = os.path.join(baseDir, f'P{participant_id}/expt_{participant_id}_session_{session}_Response_Time.txt')
        incorrect_click, incorrect_pass = extractErrors(currentPath)

        # Calculate accuracy in blocks of 'n' trials
        block_accuracies = []
        for i in range(0, 120, n):
            block_pass = incorrect_pass[i:i + n]
            block_click = incorrect_click[i:i + n]
            total_errors = sum(block_pass) + sum(block_click)
            correct_trials = n - total_errors  # Correct trials in the block

            # Normalize to percentage
            accuracy_percentage = (correct_trials / n) * 100
            block_accuracies.append(accuracy_percentage)
        
        # Determine participant type (ADHD or Non-ADHD) and store scores
        participant_type = 'ADHD' if participant_id in adhd_list else 'Non-ADHD'
        session_scores[participant_type].append(block_accuracies)

    return session_scores

def computeSessionAccuracy(baseDir, adhd_list, non_adhd_list, n=120):
    """Compute individual accuracy lists for ADHD and Non-ADHD participants across all sessions."""
    all_sessions_scores = {f'Session {i}': {'ADHD': [], 'Non-ADHD': []} for i in range(1, 9)}

    for session in range(1, 9):
        session_scores = extractParticipantAccuracy(baseDir, session, adhd_list + non_adhd_list, adhd_list, n)
        all_sessions_scores[f'Session {session}']['ADHD'] = session_scores['ADHD']
        all_sessions_scores[f'Session {session}']['Non-ADHD'] = session_scores['Non-ADHD']

    return all_sessions_scores


def save_stat_accuracy_to_json(baseDir, pre_experiment_file, output_file="../backend/results/stat_accuracy.json", n=120):
    """Compute and save session accuracy data for ADHD and Non-ADHD groups."""
    # Load ADHD and Non-ADHD participant lists
    pre_experiment_df = pd.read_csv(pre_experiment_file)
    adhd_list = pre_experiment_df[pre_experiment_df['ADHD Indication'] == True]['Participant number:'].tolist()
    non_adhd_list = pre_experiment_df[pre_experiment_df['ADHD Indication'] == False]['Participant number:'].tolist()

    # Compute accuracy data for all sessions
    all_sessions_scores = computeSessionAccuracy(baseDir, adhd_list, non_adhd_list, n)

    # Save to JSON
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w") as json_file:
        json.dump(all_sessions_scores, json_file, indent=4)
    print(f"Accuracy data saved to '{output_file}'.")

def preprocess_accuracy_stat(baseDir):
    PRE_EXPERIMENT_FILE = baseDir + "/Pre-Experiment Questionnaire.csv"
    save_stat_accuracy_to_json(baseDir, PRE_EXPERIMENT_FILE)