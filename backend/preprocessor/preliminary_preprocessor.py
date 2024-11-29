import os
import json
import pandas as pd
from utils.constants import EXCLUDED_PARTICIPANTS

def process_pre_expt(filePath):
    """
    Load and preprocess the pre-experiment questionnaire data.
    """
    # Load the CSV file and rename question columns for easy access
    print(filePath)
    df = pd.read_csv(filePath)
    df = df.iloc[:, 2:]  # Drop first two columns if they are non-relevant metadata

    # Rename columns to standard format Q0, Q1, etc.
    new_columns = {df.columns[i + 1]: f'Q{i}' for i in range(18)}
    df = df.rename(columns=new_columns)
    #df = df.drop(df.index[23])  # Drop any specific row as needed

    # Part A Score and ADHD Indication are already present, so no further calculation needed
    return df

def extractParticipant(baseDir, startExptNum, endExptNum, startSession, endSession):
    """
    Extract participant response time data and compute error counts.
    """
    participantAcc = {}
    for e in range(startExptNum, endExptNum + 1):
        currentAcc = {'w': [0, 0], 'wo': [0, 0]}
        if e in EXCLUDED_PARTICIPANTS:
            continue
        
        for s in range(startSession, endSession + 1):
            currentPath = os.path.join(baseDir, f'Accuracy/P{e}/expt_{e}_session_{s}_Response_Time.txt')
            if not os.path.exists(currentPath):
                print(f"File not found: {currentPath}")
                continue
            
            incorrect_click, incorrect_pass = extractErrors(currentPath)
            
            if s in [1, 4, 5, 8]:    
                currentAcc['w'][0] += incorrect_pass
                currentAcc['w'][1] += incorrect_click
            else:
                currentAcc['wo'][0] += incorrect_pass
                currentAcc['wo'][1] += incorrect_click
                 
        participantAcc[e] = currentAcc
        
    return participantAcc

def extractErrors(file_path):
    """
    Parse the response time file to extract error counts.
    """
    with open(file_path, 'r') as file:
        content = file.read()

    data_content, _ = content.split('Distraction Data:')
    data = json.loads(data_content)
  
    incorrect_pass_count = 0
    incorrect_click_count = 0

    for entry in data.values():
        if entry["Evaluation"] == "Incorrect Pass":
            incorrect_pass_count += 1
        elif entry["Evaluation"] == "Incorrect Click":
            incorrect_click_count += 1
    return incorrect_click_count, incorrect_pass_count

def convertToDF(data):
    """
    Convert participant data dictionary to a Pandas DataFrame.
    """
    data_list = []
    for participant, values in data.items():
        w_pass, w_click = values['w']
        wo_pass, wo_click = values['wo']
        data_list.append([participant, w_pass, w_click, wo_pass, wo_click])
    session_accuracy_df = pd.DataFrame(data_list, columns=['Participant number:', 'w_incorrect_pass', 'w_incorrect_click', 'wo_incorrect_pass', 'wo_incorrect_click'])
    return session_accuracy_df

def convertToAccuracy(df):
    """
    Convert total errors to accuracy scores for both 'w' and 'wo' sessions.
    """
    df["total_error_w"] = 1 - (df["w_incorrect_pass"] + df["w_incorrect_click"]) / 120
    df["total_error_wo"] = 1 - (df["wo_incorrect_pass"] + df["wo_incorrect_click"]) / 120
    return df

def preprocess_and_save(baseDir, output_csv="../backend/results/accuracy_data.csv"):
    """
    Preprocess response time and pre-experiment data, then save the merged results to a CSV.
    """
    # Step 1: Ensure the output directory exists
    output_dir = os.path.dirname(output_csv)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
        print(f"Created directory: {output_dir}")

    # Step 2: Process session data to calculate errors and accuracy
    result_data = convertToDF(extractParticipant(baseDir, 1, 59, 1, 8))
    final_data = convertToAccuracy(result_data)

    # Step 3: Load only 'Participant number:' and 'ADHD Indication' columns from pre-experiment data
    pre_expt_df = pd.read_csv(os.path.join(baseDir, "Pre-Experiment Questionnaire.csv"))[
        ['Participant number:', 'ADHD Indication']
    ]

    # Step 4: Merge only 'ADHD Indication' column with session accuracy data
    final_data = pd.merge(
        final_data, 
        pre_expt_df, 
        on='Participant number:', 
        how='inner'
    )

    # Step 5: Save the final merged DataFrame to CSV
    absolute_csv_path = os.path.abspath(output_csv)  # Resolve to absolute path
    print(absolute_csv_path)
    final_data.to_csv(absolute_csv_path, index=False)
    print(f"Data saved to {absolute_csv_path}")

def preprocess_pose(baseDir, output_csv="results/accuracy/accuracy_data.csv"):
    """
    Preprocess response time and pre-experiment data, then save the merged results to a CSV and JSON.
    """
    # Step 1: Ensure the output directory exists
    output_dir = os.path.dirname(output_csv)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
        print(f"Created directory: {output_dir}")

    # Step 2: Process session data to calculate errors and accuracy
    result_data = convertToDF(extractParticipant(baseDir, 1, 59, 1, 8))
    final_data = convertToAccuracy(result_data)

    # Step 3: Load only 'Participant number:' and 'ADHD Indication' columns from pre-experiment data
    pre_expt_file = os.path.join(baseDir, "Pre-Experiment Questionnaire.csv")
    pre_expt_df = pd.read_csv(pre_expt_file)[['Participant number:', 'ADHD Indication']]

    # Step 4: Merge only 'ADHD Indication' column with session accuracy data
    final_data = pd.merge(
        final_data, 
        pre_expt_df, 
        on='Participant number:', 
        how='inner'
    )

    # Step 5: Save the final merged DataFrame to CSV
    absolute_csv_path = os.path.abspath(output_csv)  # Resolve to absolute path
    final_data.to_csv(absolute_csv_path, index=False)
    print(f"Data saved to {absolute_csv_path}")

    # Step 6: Save as JSON
    json_output_path = absolute_csv_path.replace('.csv', '.json')
    final_data.to_json(json_output_path, orient='records', indent=4)
    print(f"Data saved to {json_output_path}")
