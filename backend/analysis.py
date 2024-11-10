import os
import json
import pandas as pd
import scipy.stats as stats

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

def getErrors(final_df):
    errors_adhd_w = final_df[final_df['ADHD_Indication'] == True]['total_error_w']
    errors_non_adhd_w = final_df[final_df['ADHD_Indication'] == False]['total_error_w']
    errors_adhd_wo = final_df[final_df['ADHD_Indication'] == True]['total_error_wo']
    errors_non_adhd_wo = final_df[final_df['ADHD_Indication'] == False]['total_error_wo']
    total_errors_adhd = final_df[final_df['ADHD_Indication'] == True]['total_errors']
    total_errors_non_adhd = final_df[final_df['ADHD_Indication'] == False]['total_errors']
    
    return {
        'errors_adhd_w': errors_adhd_w,
        'errors_non_adhd_w': errors_non_adhd_w,
        'errors_adhd_wo': errors_adhd_wo,
        'errors_non_adhd_wo': errors_non_adhd_wo,
        'total_errors_adhd': total_errors_adhd,
        'total_errors_non_adhd': total_errors_non_adhd
    }

def stat_test(x, y, alt='two-sided', option='indep'):
    wx, px = stats.shapiro(x)
    wy, py = stats.shapiro(y)
    t_stat, p_val = 0, 0
    if px > 0.05 and py > 0.05:
        if option == 'indep':
            levene_stat, levene_p_val = stats.levene(x, y)
            if levene_p_val > 0.05:
                t_stat, p_val = stats.ttest_ind(x, y, alternative=alt)
            else:
                t_stat, p_val = stats.ttest_ind(x, y, alternative=alt, equal_var=False)
        else:
            t_stat, p_val = stats.ttest_rel(x, y, alternative=alt)
    else:
        if option == 'indep':
            t_stat, p_val = stats.ranksums(x, y, alternative=alt)
        else:
            t_stat, p_val = stats.wilcoxon(x, y, alternative=alt)
    return t_stat, p_val
