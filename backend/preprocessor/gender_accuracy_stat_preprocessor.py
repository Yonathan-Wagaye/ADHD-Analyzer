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

def extractParticipant(baseDir, session, participants, n=120):
    """
    Extract participant accuracy data for a given session and list of participants.

    Parameters:
    - baseDir: Base directory containing the participant data files.
    - session: Session number to extract data for (1 to 8).
    - participants: List of participant IDs to process.
    - n: Number of frames to group for accuracy calculation in each block (default 12).

    Returns:
    - session_scores: Dictionary with 'w' and 'wo' accuracy percentages for the given participants.
    """
    num_blocks = 120 // n  # Calculate the number of blocks based on 'n'
    session_scores = {'w': [[] for _ in range(num_blocks)], 'wo': [[] for _ in range(num_blocks)]}

    for participant_id in participants:
        currentPath = os.path.join(baseDir, f'Accuracy/P{participant_id}/expt_{participant_id}_session_{session}_Response_Time.txt')

        # Extract errors for the current participant and session
        incorrect_click, incorrect_pass = extractErrors(currentPath)

        # Calculate accuracy percentages in blocks of 'n' trials
        for i in range(0, 120, n):
            block_pass = incorrect_pass[i:i + n]
            block_click = incorrect_click[i:i + n]
            total_errors = sum(block_pass) + sum(block_click)
            correct_trials = n - total_errors  # Correct trials in the block
            
            # Normalize to percentage
            accuracy_percentage = (correct_trials / n) * 100

            # Determine the session type ('w' or 'wo') and append the scores
            if session in [1, 4, 5, 8]:  # 'w' sessions (with distraction)
                session_scores['w'][i // n].append(accuracy_percentage)
            else:  # 'wo' sessions (without distraction)
                session_scores['wo'][i // n].append(accuracy_percentage)

    return session_scores


def compute_gender_accuracy(baseDir, gender_groups, n=120):
    """
    Compute accuracy percentages per gender group for all sessions.

    Parameters:
    - baseDir: Base directory containing session data.
    - gender_groups: Dictionary of gender-based groups (e.g., {"M-ADHD": [1, 2], "F-ADHD": [3, 4]}).
    - n: Number of trials per block.

    Returns:
    - gender_accuracy: Dictionary of accuracy percentages for each gender group.
    """
    # Initialize gender_accuracy with lists of lists for each block
    gender_accuracy = {group: {f'Session {i}': {'w': [[] for _ in range(120 // n)], 'wo': [[] for _ in range(120 // n)]}
                                for i in range(1, 9)} for group in gender_groups}

    for group, participants in gender_groups.items():
        for session in range(1, 9):
            session_scores = extractParticipant(baseDir, session, participants, n)
            for block_index in range(len(session_scores['w'])):
                # Add individual values to the nested lists without using extend
                for score in session_scores['w'][block_index]:
                    gender_accuracy[group][f'Session {session}']['w'][block_index].append(score)
                for score in session_scores['wo'][block_index]:
                    gender_accuracy[group][f'Session {session}']['wo'][block_index].append(score)

    return gender_accuracy





def save_gender_accuracy_to_json(baseDir, pre_experiment_csv, output_file="../backend/results/accuracy/gender_stat_accuracy.json", n=120):
    """
    Save the computed gender accuracy to a JSON file.

    Parameters:
    - baseDir: Base directory containing session data.
    - pre_experiment_csv: Path to the pre-experiment CSV file containing participant data.
    - output_file: Path to save the JSON output.
    - n: Number of blocks per session.
    """
    # Load participant data from pre-experiment CSV
    pre_experiment_df = pd.read_csv(pre_experiment_csv)
    
    # Extract gender and ADHD groups
    gender_groups = {
        "M-ADHD": pre_experiment_df[(pre_experiment_df['Gender'] == 'Male') & (pre_experiment_df['ADHD Indication'] == True)]['Participant number:'].tolist(),
        "F-ADHD": pre_experiment_df[(pre_experiment_df['Gender'] == 'Female') & (pre_experiment_df['ADHD Indication'] == True)]['Participant number:'].tolist(),
        "M-nonADHD": pre_experiment_df[(pre_experiment_df['Gender'] == 'Male') & (pre_experiment_df['ADHD Indication'] == False)]['Participant number:'].tolist(),
        "F-nonADHD": pre_experiment_df[(pre_experiment_df['Gender'] == 'Female') & (pre_experiment_df['ADHD Indication'] == False)]['Participant number:'].tolist()
    }
    for g in ["M-ADHD", "F-ADHD", "M-nonADHD", "F-nonADHD"]:
        for e in gender_groups[g]:
            if e in EXCLUDED_PARTICIPANTS:
                gender_groups[g].remove(e)
    print('M-ADHD: ', len(gender_groups['M-ADHD']))
    print('F-ADHD: ', len(gender_groups['F-ADHD']))
    print('M-non-ADHD: ', len(gender_groups['M-nonADHD']))
    print('F-non-ADHD: ', len(gender_groups['F-nonADHD']))
    # Compute gender-based accuracy
    gender_accuracy = compute_gender_accuracy(baseDir, gender_groups, n)

    # Save to JSON
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w") as json_file:
        json.dump(gender_accuracy, json_file, indent=4)
    print(f"Gender accuracy saved to {output_file}.")

def preprocess_gender_stat(baseDir):
    PRE_EXPERIMENT_FILE = baseDir + "/Pre-Experiment Questionnaire.csv"
    save_gender_accuracy_to_json(baseDir, PRE_EXPERIMENT_FILE)


