import os
import json
import pandas as pd

def calculate_adhd_score(row):
    score = 0
    # Define response mappings based on the scoring criteria
    response_mapping_one = { 'Never': 0, 'Rarely': 0, 'Sometimes': 1, 'Often': 1, 'Very Often': 1 }
    response_mapping_two = { 'Never': 0, 'Rarely': 0, 'Sometimes': 0, 'Often': 1, 'Very Often': 1 }

    # Apply response mappings for specific questions
    for q in ['Q0', 'Q1', 'Q2']:
        score += response_mapping_one[row[q]]
    for q in ['Q3', 'Q4', 'Q5']:
        score += response_mapping_two[row[q]]  
    
    return score

def process_pre_expt(filePath):
    # Load the CSV file and rename question columns for easy access
    df = pd.read_csv(filePath)
    df = df.iloc[:, 2:]  # Drop first two columns if they are non-relevant metadata
    
    # Rename columns to standard format Q0, Q1, etc.
    new_columns = { df.columns[i + 1]: f'Q{i}' for i in range(18) }
    df = df.rename(columns=new_columns)
    df = df.drop(df.index[23])  # Drop any specific row as needed

    # Calculate Part A scores and add ADHD indication
    df['Part_A_Score'] = df.apply(calculate_adhd_score, axis=1)
    df['ADHD_Indication'] = df['Part_A_Score'] >= 4  # True if score meets ADHD threshold

    return df

def extractParticipant(baseDir, startExptNum, endExptNum, startSession, endSession):
    participantAcc = {} 
    for e in range(startExptNum, endExptNum + 1):
        currentAcc = {'w': [0, 0], 'wo': [0, 0]}
        if e == 24:
            continue
        
        for s in range(startSession, endSession + 1):
            currentPath = os.path.join(baseDir, f'P{e}', f'expt_{e}_session_{s}_Response_Time.txt')
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
    data_list = []
    for participant, values in data.items():
        w_pass, w_click = values['w']
        wo_pass, wo_click = values['wo']
        data_list.append([participant, w_pass, w_click, wo_pass, wo_click])
    session_accuracy_df = pd.DataFrame(data_list, columns=['Participant number:', 'w_incorrect_pass', 'w_incorrect_click', 'wo_incorrect_pass', 'wo_incorrect_click'])
    return session_accuracy_df

def convertToAccuracy(df):
    # Convert total errors to accuracy scores
    df["total_error_w"] = 1 - (df["w_incorrect_pass"] + df["w_incorrect_click"]) / 120
    df["total_error_wo"] = 1 - (df["wo_incorrect_pass"] + df["wo_incorrect_click"]) / 120
    return df

def preprocess_and_save(baseDir,output_csv="accuracy_data.csv"):
    # Process session data
    result_data = convertToDF(extractParticipant(baseDir, 1, 35, 1, 8))
    final_data = convertToAccuracy(result_data)

    # Process pre-experiment data to get ADHD indication
    pre_expt_df = process_pre_expt(baseDir + '/Pre-Experiment Questionnaire-Final.csv')

    # Merge pre-experiment data with session data based on Participant number
    final_data = pd.merge(pre_expt_df[['Participant number:', 'ADHD_Indication', 'Part_A_Score']], 
                          final_data, 
                          on='Participant number:', 
                          how='inner')

    # Save the final DataFrame to CSV
    final_data.to_csv(output_csv, index=False)
    print(f"Data saved to {output_csv}")

