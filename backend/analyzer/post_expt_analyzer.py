# post_experiment_analyzer.py

import pandas as pd
import os
from utils.constants import EXCLUDED_PARTICIPANTS
from utils.stat_tests import stat_test

columns_mapping = {
    "I felt that the robot yawning distracted me from the task": "Yawn",
    "I felt that the robot sneezing distracted me from the task": "Sneeze",
    "I felt that the silent presence of the robot distracted me from the task": "Silent Presence",
    "I felt that the robot singing distracted me from the task": "Sing"
}

response_mapping = {
    'Strongly Disagree': 1,
    'Disagree': 2,
    'Neutral': 3,
    'Natural': 3,
    'Agree': 4,
    'Strongly Agree': 5,
    'Strong Agree': 5
}

def load_data(pre_experiment_csv, post_experiment_csv):
    """
    Load and join pre-experiment and post-experiment questionnaire data,
    excluding participants in EXCLUDED_PARTICIPANTS.

    Parameters:
    - pre_experiment_csv: Path to the pre-experiment questionnaire CSV file.
    - post_experiment_csv: Path to the post-experiment questionnaire CSV file.

    Returns:
    - df: Pandas DataFrame with joined data, including the ADHD Indication field.
    """
    # Load pre and post data
    pre_df = pd.read_csv(pre_experiment_csv)
    post_df = pd.read_csv(post_experiment_csv)

    # Exclude participants from the pre-experiment data
    pre_df = pre_df[~pre_df['Participant number:'].isin(EXCLUDED_PARTICIPANTS)]
    post_df = post_df[~post_df['Participant number:'].isin(EXCLUDED_PARTICIPANTS)]

    # Merge data on 'Participant number:'
    merged_df = post_df.merge(pre_df[['Participant number:', 'ADHD Indication']], 
                              on='Participant number:')

    # Preprocess post-experiment data
    merged_df = preprocess_post_data(merged_df)

    return merged_df


def preprocess_post_data(post_df):
    """
    Preprocess the post-experiment data by renaming columns and mapping responses.

    Parameters:
    - post_df: Pandas DataFrame containing post-experiment questionnaire data.

    Returns:
    - post_df: Preprocessed DataFrame with renamed columns and numerical responses.
    """
    # Rename columns
    post_df.rename(columns=columns_mapping, inplace=True)

    # Map responses to numerical values
    for column in columns_mapping.values():
        if column in post_df.columns:
            post_df[column] = post_df[column].str.strip()  # Remove extra whitespace
            post_df[column] = post_df[column].map(response_mapping)
        else:
            print(f"Warning: Column '{column}' not found in post_df.")

    return post_df

def perform_p_value_analysis(baseDir):
    """
    Perform p-value analysis comparing ADHD and Non-ADHD groups for each distraction type.

    Parameters:
    - baseDir: Base directory where the pre- and post-experiment CSV files are located.

    Returns:
    - p_values: Dictionary containing p-values for each distraction type.
    """
    pre_experiment_csv = os.path.join(baseDir, "Pre-Experiment Questionnaire.csv")
    post_experiment_csv = os.path.join(baseDir, "Post-Experiment Question.csv")

    df = load_data(pre_experiment_csv, post_experiment_csv)

    # Split the dataframe into ADHD and Non-ADHD groups
    groups = {
        "ADHD": df[df["ADHD Indication"] == True],
        "Non-ADHD": df[df["ADHD Indication"] == False]
    }

    p_values = {}
    for d in ["Yawn", "Sneeze", "Silent Presence", "Sing"]:
        adhd_scores = groups['ADHD'][d].dropna()
        non_adhd_scores = groups['Non-ADHD'][d].dropna()
        stat, p_value = stat_test(adhd_scores, non_adhd_scores)
        p_values[d] = p_value

    return p_values

def get_participant_counts(baseDir):
    """
    Get the counts of participants in each group.

    Parameters:
    - baseDir: Base directory where the pre-experiment CSV file is located.

    Returns:
    - counts: Dictionary containing counts of participants in each group.
    """
    pre_experiment_csv = os.path.join(baseDir, "Pre-Experiment Questionnaire.csv")
    pre_df = pd.read_csv(pre_experiment_csv)

    # Exclude specified participants
    pre_df = pre_df[~pre_df['Participant number:'].isin(EXCLUDED_PARTICIPANTS)]

    counts = {}

    counts['Total Participants'] = len(pre_df)

    counts['Male ADHD'] = len(pre_df[(pre_df['Gender'] == 'Male') & (pre_df['ADHD Indication'] == True)])
    counts['Female ADHD'] = len(pre_df[(pre_df['Gender'] == 'Female') & (pre_df['ADHD Indication'] == True)])
    counts['Male Non-ADHD'] = len(pre_df[(pre_df['Gender'] == 'Male') & (pre_df['ADHD Indication'] == False)])
    counts['Female Non-ADHD'] = len(pre_df[(pre_df['Gender'] == 'Female') & (pre_df['ADHD Indication'] == False)])

    return counts
