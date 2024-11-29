import pandas as pd
import numpy as np
import os
from utils.stat_tests import stat_test


def load_accuracy_data(csv_file="../backend/results/accuracy/accuracy_data.csv"):
    """
    Loads the accuracy data from a specified CSV file.
    """
    absolute_csv_path = os.path.abspath(csv_file) 
    try:
        data = pd.read_csv(absolute_csv_path)
        print("Accuracy data loaded successfully.")
        return data
    except FileNotFoundError:
        print(f"File {csv_file} not found. Ensure the file path is correct.")
        return None

def basic_within_test(data):
    # Separate ADHD and Non-ADHD groups
    adhd = data[data['ADHD Indication'] == True]
    non_adhd = data[data['ADHD Indication'] == False]

    # Calculate mean and standard deviation for ADHD with and without distraction
    adhd_mean_w, adhd_std_w = np.mean(adhd['total_error_w']), np.std(adhd['total_error_w'])
    adhd_mean_wo, adhd_std_wo = np.mean(adhd['total_error_wo']), np.std(adhd['total_error_wo'])

    # Calculate mean and standard deviation for Non-ADHD with and without distraction
    non_adhd_mean_w, non_adhd_std_w = np.mean(non_adhd['total_error_w']), np.std(non_adhd['total_error_w'])
    non_adhd_mean_wo, non_adhd_std_wo = np.mean(non_adhd['total_error_wo']), np.std(non_adhd['total_error_wo'])

    # Perform statistical tests within each group (with vs without distraction)
    t_stat_adhd, p_val_adhd = stat_test(adhd['total_error_w'], adhd['total_error_wo'], option='dep')
    t_stat_non_adhd, p_val_non_adhd = stat_test(non_adhd['total_error_w'], non_adhd['total_error_wo'], option='dep')

    return {
        'ADHD': {
            'Mean ± SD With Distraction': f"{adhd_mean_w:.2f} ± {adhd_std_w:.2f}",
            'Mean ± SD Without Distraction': f"{adhd_mean_wo:.2f} ± {adhd_std_wo:.2f}",
            'p_value_within': p_val_adhd
        },
        'Non-ADHD': {
            'Mean ± SD With Distraction': f"{non_adhd_mean_w:.2f} ± {non_adhd_std_w:.2f}",
            'Mean ± SD Without Distraction': f"{non_adhd_mean_wo:.2f} ± {non_adhd_std_wo:.2f}",
            'p_value_within': p_val_non_adhd
        }
    }

def basic_between_test(data):
    # Separate ADHD and Non-ADHD groups
    adhd = data[data['ADHD Indication'] == True]
    non_adhd = data[data['ADHD Indication'] == False]

    # Calculate mean and standard deviation for ADHD and Non-ADHD with distraction
    adhd_mean_w, adhd_std_w = np.mean(adhd['total_error_w']), np.std(adhd['total_error_w'])
    non_adhd_mean_w, non_adhd_std_w = np.mean(non_adhd['total_error_w']), np.std(non_adhd['total_error_w'])

    # Calculate mean and standard deviation for ADHD and Non-ADHD without distraction
    adhd_mean_wo, adhd_std_wo = np.mean(adhd['total_error_wo']), np.std(adhd['total_error_wo'])
    non_adhd_mean_wo, non_adhd_std_wo = np.mean(non_adhd['total_error_wo']), np.std(non_adhd['total_error_wo'])

    # Perform statistical tests between groups for each condition (with and without distraction)
    t_stat_w, p_val_w = stat_test(adhd['total_error_w'], non_adhd['total_error_w'], option='indep')
    t_stat_wo, p_val_wo = stat_test(adhd['total_error_wo'], non_adhd['total_error_wo'], option='indep')

    return {
        'With Distraction': {
            'ADHD Mean ± SD': f"{adhd_mean_w:.2f} ± {adhd_std_w:.2f}",
            'Non-ADHD Mean ± SD': f"{non_adhd_mean_w:.2f} ± {non_adhd_std_w:.2f}",
            'p_value_between': p_val_w
        },
        'Without Distraction': {
            'ADHD Mean ± SD': f"{adhd_mean_wo:.2f} ± {adhd_std_wo:.2f}",
            'Non-ADHD Mean ± SD': f"{non_adhd_mean_wo:.2f} ± {non_adhd_std_wo:.2f}",
            'p_value_between': p_val_wo
        }
    }
