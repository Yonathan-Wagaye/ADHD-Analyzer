import os
import json
import pandas as pd
import scipy.stats as stats
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64

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

def calculate_adhd_score(row):
    score = 0
    response_mapping_one = {'Never': 0, 'Rarely': 0, 'Sometimes': 1, 'Often': 1, 'Very Often': 1}
    response_mapping_two = {'Never': 0, 'Rarely': 0, 'Sometimes': 0, 'Often': 1, 'Very Often': 1}
    for q in ['Q0', 'Q1', 'Q2']:
        score += response_mapping_one[row[q]]
    for q in ['Q3', 'Q4', 'Q5']:
        score += response_mapping_two[row[q]]
    return score

def process_pre_expt(filePath):
    df = pd.read_csv(filePath)
    df = df.iloc[:, 2:]
    new_columns = {df.columns[i + 1]: f'Q{i}' for i in range(18)}
    df = df.rename(columns=new_columns)
    df = df.drop(df.index[23])
    df['Part_A_Score'] = df.iloc[:, 1:].apply(calculate_adhd_score, axis=1)
    df['ADHD_Indication'] = df['Part_A_Score'] >= 4
    return df

def createTotalError(final_df):
    final_df['total_error_w'] = final_df['w_incorrect_pass'] + final_df['w_incorrect_click']
    final_df['total_error_wo'] = final_df['wo_incorrect_pass'] + final_df['wo_incorrect_click']
    final_df['total_errors'] = final_df['total_error_w'] + final_df['total_error_wo']
    return final_df

def convertToAccuracy(df):
    """
    Converts total error columns to accuracy for both with and without distraction.
    """
    df["total_error_w"] = 1 - df["total_error_w"] / 120
    df["total_error_wo"] = 1 - df["total_error_wo"] / 120
    return df

def sameGroup(final_df):
    adhd_df = final_df[final_df['ADHD_Indication'] == True]
    non_adhd_df = final_df[final_df['ADHD_Indication'] == False]
    
    plt.figure(figsize=(14, 6))
    
    # Plot for ADHD group with and without distraction
    plt.subplot(1, 2, 1)
    sns.boxplot(data=adhd_df[['total_error_w', 'total_error_wo']])
    plt.title('ADHD Group')
    plt.xlabel('Condition')
    plt.ylabel('Accuracy Rate')
    plt.xticks([0, 1], ['With Distraction', 'Without Distraction'])
    plt.ylim([0, 1.05])
    
    # Plot for Non-ADHD group with and without distraction
    plt.subplot(1, 2, 2)
    sns.boxplot(data=non_adhd_df[['total_error_w', 'total_error_wo']])
    plt.title('Non-ADHD Group')
    plt.xlabel('Condition')
    plt.ylabel('Accuracy Rate')
    plt.xticks([0, 1], ['With Distraction', 'Without Distraction'])
    plt.ylim([0, 1.05])
    
    plt.tight_layout()
    
    # Save plot to a bytes buffer and encode to base64
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()
    plot_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    return plot_base64

def diffGroup(final_df):
    adhd_df = final_df[final_df['ADHD_Indication'] == True]
    non_adhd_df = final_df[final_df['ADHD_Indication'] == False]
    
    plt.figure(figsize=(14, 6))
    
    # Combine the ADHD and Non-ADHD data for plotting
    with_distraction = pd.concat([adhd_df[['total_error_w']].assign(Group='ADHD'),
                                  non_adhd_df[['total_error_w']].assign(Group='Non-ADHD')])
    
    without_distraction = pd.concat([adhd_df[['total_error_wo']].assign(Group='ADHD'),
                                     non_adhd_df[['total_error_wo']].assign(Group='Non-ADHD')])
    
    # Plot for ADHD and Non-ADHD group with distraction
    plt.subplot(1, 2, 1)
    sns.boxplot(x='Group', y='total_error_w', data=with_distraction)
    plt.title('With Distraction')
    plt.xlabel('Group')
    plt.ylabel('Accuracy Rate')
    plt.ylim([0, 1.05])
    
    # Plot for ADHD and Non-ADHD group without distraction
    plt.subplot(1, 2, 2)
    sns.boxplot(x='Group', y='total_error_wo', data=without_distraction)
    plt.title('Without Distraction')
    plt.xlabel('Group')
    plt.ylabel('Accuracy Rate')
    plt.ylim([0, 1.05])
    
    plt.tight_layout()
    
    # Save plot to a bytes buffer and encode to base64
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()
    plot_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    return plot_base64
