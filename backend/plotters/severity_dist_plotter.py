import matplotlib.pyplot as plt
import pandas as pd
import io
import base64

def load_pre_experiment_data(pre_experiment_csv):
    """
    Load and preprocess the pre-experiment questionnaire data.

    Parameters:
    - pre_experiment_csv: Path to the pre-experiment questionnaire CSV file.

    Returns:
    - pre_df: Pandas DataFrame with pre-experiment data.
    """
    pre_df = pd.read_csv(pre_experiment_csv)
    filtered_df = pre_df[~pre_df['Participant number:'].isin([2, 5, 23, 24, 35, 36])]
    return filtered_df

def create_pre_experiment_bar_plot(df, column, title):
    """
    Create a bar plot for the given pre-experiment questionnaire column.

    Parameters:
    - df: Pandas DataFrame containing the pre-experiment questionnaire data.
    - column: Column name to plot (e.g., 'Part_A_Score').
    - title: Title of the plot.

    Returns:
    - base64_image: Base64-encoded string of the plot image.
    """
    # Count scores and sort by index
    score_counts = df[column].value_counts().sort_index()

    # Create a bar plot
    plt.figure(figsize=(10, 5))
    plt.bar(score_counts.index, score_counts.values, color='blue')
    plt.title(title)
    plt.xlabel('Score')
    plt.ylabel('Frequency')

    # Save the plot to a Base64-encoded string
    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    base64_image = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()
    plt.close()

    return base64_image

def generate_pre_experiment_plot(pre_experiment_csv, column, title="Pre-Experiment Questionnaire"):
    """
    Generate a bar plot for the pre-experiment questionnaire.

    Parameters:
    - pre_experiment_csv: Path to the pre-experiment questionnaire CSV file.
    - column: Column name to plot (e.g., 'Part_A_Score').
    - title: Title of the plot.

    Returns:
    - base64_image: Base64-encoded string of the plot image.
    """
    # Load pre-experiment data
    pre_df = load_pre_experiment_data(pre_experiment_csv)

    # Create the bar plot
    return create_pre_experiment_bar_plot(pre_df, column, title)
