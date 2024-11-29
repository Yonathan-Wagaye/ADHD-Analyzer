import matplotlib.pyplot as plt
import io
import base64
import pandas as pd
import os
from utils.constants import EXCLUDED_PARTICIPANTS

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
    - post_df: Pandas DataFrame with joined data, including the ADHD Indication field.
    """
    # Load pre and post data
    pre_df = pd.read_csv(pre_experiment_csv)
    post_df = pd.read_csv(post_experiment_csv)

    # Exclude participants from both datasets
    pre_df = pre_df[~pre_df['Participant number:'].isin(EXCLUDED_PARTICIPANTS)]
    post_df = post_df[~post_df['Participant number:'].isin(EXCLUDED_PARTICIPANTS)]

    # Merge data on 'Participant number:'
    merged_df = post_df.merge(pre_df[['Participant number:', 'ADHD Indication']], 
                              on='Participant number:')

    # Preprocess post-experiment data
    merged_df = preprocess_post_data(merged_df)

    # Keep only necessary columns
    necessary_columns = ['Participant number:', 'ADHD Indication'] + list(columns_mapping.values())
    filtered_df = merged_df.filter(items=necessary_columns)

    return filtered_df

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

def create_box_plot(dataframe, title):
    """
    Create a box plot for the given dataframe and return it as a Base64-encoded string.

    Parameters:
    - dataframe: DataFrame containing the data to plot.
    - title: Title of the plot.

    Returns:
    - base64_image: Base64-encoded string of the plot image.
    """
    # Use only columns corresponding to the responses
    columns_to_plot = ["Yawn", "Sneeze", "Silent Presence", "Sing"]

    # Filter the DataFrame to include only these columns
    dataframe = dataframe[columns_to_plot]

    plt.figure(figsize=(10, 6))  # Adjust plot size
    boxplot = dataframe.boxplot(patch_artist=True, column=columns_to_plot)
    colors = ['lightblue', 'lightgreen', 'lightyellow', 'lightpink']

    # Set box colors
    for patch, color in zip(boxplot.artists, colors):
        patch.set_facecolor(color)

    plt.title(title)
    plt.ylabel('Response (1-5)')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.grid(visible=None)
    plt.yticks([1, 2, 3, 4, 5])

    # Save the plot to a Base64-encoded string
    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    base64_image = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()
    plt.close()
    return base64_image

def generate_adhd_based_box_plots(baseDir):
    """
    Generate box plots for ADHD and Non-ADHD participants and return them as Base64-encoded strings.

    Parameters:
    - baseDir: Base directory where the pre- and post-experiment CSV files are located.

    Returns:
    - box_plots: Dictionary with Base64-encoded box plot images for each group.
    """
    pre_experiment_csv = os.path.join(baseDir, "Pre-Experiment Questionnaire.csv")
    post_experiment_csv = os.path.join(baseDir, "Post-Experiment Question.csv")

    # Load and merge data
    post_df = load_data(pre_experiment_csv, post_experiment_csv)

    # Split the dataframe into ADHD and Non-ADHD groups
    groups = {
        "ADHD": post_df[post_df["ADHD Indication"] == True],
        "Non-ADHD": post_df[post_df["ADHD Indication"] == False]
    }

    # Generate and return box plots
    box_plots = {}
    for group_name, group_data in groups.items():
        base64_image = create_box_plot(
            dataframe=group_data,
            title=f"Level of distraction - {group_name}"
        )
        box_plots[group_name] = base64_image
    return box_plots
