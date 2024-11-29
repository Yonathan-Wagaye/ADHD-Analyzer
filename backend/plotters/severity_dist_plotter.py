import matplotlib.pyplot as plt
import pandas as pd
import io
import base64
import os
from utils.constants import EXCLUDED_PARTICIPANTS

def load_pre_experiment_data(pre_experiment_csv):
    """
    Load and preprocess the pre-experiment questionnaire data, excluding specific participants.

    Parameters:
    - pre_experiment_csv: Path to the pre-experiment questionnaire CSV file.

    Returns:
    - pre_df: Pandas DataFrame with pre-experiment data.
    """
    pre_df = pd.read_csv(pre_experiment_csv)
    filtered_df = pre_df[~pre_df['Participant number:'].isin(EXCLUDED_PARTICIPANTS)]
    return filtered_df

def create_stacked_bar_plot(df, column, title):
    """
    Create a stacked bar plot for the given pre-experiment questionnaire column by gender
    and return it as a Base64-encoded string.

    Parameters:
    - df: Pandas DataFrame containing the pre-experiment questionnaire data.
    - column: Column name to plot (e.g., 'ADHD Score').
    - title: Title of the plot.

    Returns:
    - base64_image: Base64-encoded string of the plot image.
    """
    # Group data by Gender and the specified column, then calculate counts
    grouped_data = df.groupby(['Gender', column]).size().unstack(fill_value=0)

    # Create the stacked bar plot
    plt.figure(figsize=(10, 6))
    grouped_data.T.plot(kind='bar', stacked=True, color=['blue', 'red'], alpha=0.8)
    
    plt.xticks(rotation=0)

    plt.title(title)
    plt.xlabel('ADHD Severity Level')
    plt.ylabel('Frequency')
    plt.legend(title='Gender', loc='upper right')

    # Save the plot to a Base64-encoded string
    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    base64_image = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()
    plt.close()
    return base64_image

def generate_gender_severity_plot(baseDir):
    """
    Generate a stacked bar plot for severity levels by gender and return it as a Base64-encoded string.

    Parameters:
    - baseDir: Base directory where the pre-experiment questionnaire file is located.

    Returns:
    - base64_image: Base64-encoded string of the stacked bar plot image.
    """
    pre_experiment_file = os.path.join(baseDir, "Pre-Experiment Questionnaire.csv")
    column = "ADHD Score"  # Adjust the column name if needed

    # Load pre-experiment data, excluding specified participants
    pre_df = load_pre_experiment_data(pre_experiment_file)

    # Generate and return the stacked bar plot
    base64_image = create_stacked_bar_plot(pre_df, column, title="Severity Levels by Gender")
    return base64_image
