import matplotlib.pyplot as plt
import io
import base64
import pandas as pd

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
    Load and join pre-experiment and post-experiment questionnaire data.

    Parameters:
    - pre_experiment_csv: Path to the pre-experiment questionnaire CSV file.
    - post_experiment_csv: Path to the post-experiment questionnaire CSV file.

    Returns:
    - post_df: Pandas DataFrame with joined data, including the ADHD_Indication field.
    """
    # Load pre and post data
    pre_df = pd.read_csv(pre_experiment_csv)
    post_df = pd.read_csv(post_experiment_csv)

    # Merge data on 'Participant number:'
    merged_df = post_df.merge(pre_df[['Participant number:', 'ADHD Indication', 'Gender']], 
                              on='Participant number:')

    # Preprocess post-experiment data
    merged_df = preprocess_post_data(merged_df)

    # Keep only necessary columns
    necessary_columns = ['Participant number:', 'Gender_x', 'ADHD Indication'] + list(columns_mapping.values())
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


def create_box_plot(dataframe, title, y_ticks):
    """
    Create a box plot for the given dataframe.

    Parameters:
    - dataframe: DataFrame containing the data to plot.
    - title: Title of the plot.
    - y_ticks: Y-axis tick labels.

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
    plt.yticks(y_ticks)

    # Save the plot to a Base64-encoded string
    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    base64_image = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()
    plt.close()

    return base64_image


def generate_gender_based_box_plots(pre_experiment_csv, post_experiment_csv):
    """
    Generate box plots for each gender-based group and return them as Base64-encoded strings.

    Parameters:
    - pre_experiment_csv: Path to the pre-experiment questionnaire CSV file.
    - post_experiment_csv: Path to the post-experiment questionnaire CSV file.

    Returns:
    - box_plots: Dictionary with Base64-encoded box plot images for each group.
    """
    # Load and merge data
    post_df = load_data(pre_experiment_csv, post_experiment_csv)

    # Split the dataframe into gender-based groups
    groups = {
        "ADHD_Male": post_df[(post_df["ADHD Indication"] == True) & (post_df["Gender_x"] == "Male")],
        "ADHD_Female": post_df[(post_df["ADHD Indication"] == True) & (post_df["Gender_x"] == "Female")],
        "NonADHD_Male": post_df[(post_df["ADHD Indication"] == False) & (post_df["Gender_x"] == "Male")],
        "NonADHD_Female": post_df[(post_df["ADHD Indication"] == False) & (post_df["Gender_x"] == "Female")],
    }

    # Generate and store box plots
    box_plots = {}
    yint = [0, 1, 2, 3, 4, 5]  # Y-axis ticks
    for group_name, group_data in groups.items():
        box_plots[group_name] = create_box_plot(
            dataframe=group_data,  # Pass filtered DataFrame
            title=f"Level of distraction - {group_name}",
            y_ticks=yint
        )

    return box_plots
