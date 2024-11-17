import matplotlib.pyplot as plt
import matplotlib.patches as patches
import json
import io
import base64

def load_gender_accuracy_from_json(json_file):
    """
    Load the gender-based accuracy data from a JSON file.

    Parameters:
    - json_file: Path to the JSON file containing gender accuracy data.

    Returns:
    - gender_accuracy: Dictionary with gender accuracy data.
    """
    with open(json_file, 'r') as file:
        return json.load(file)

def create_gender_trendline_plot(gender_accuracy, n=120):
    """
    Generate a trendline plot for gender-based accuracy data.

    Parameters:
    - gender_accuracy: Dictionary containing gender accuracy data.
    - n: Number of blocks per session.

    Returns:
    - base64_image: Base64-encoded string of the plot image.
    """
    # Define color mapping for gender groups
    color_map = {
        'M-ADHD': 'red',       # Red for Male-ADHD
        'F-ADHD': 'green',      # Pink for Female-ADHD
        'M-nonADHD': 'blue',   # Blue for Male-nonADHD
        'F-nonADHD': 'black'    # Cyan for Female-nonADHD
    }

    plt.figure(figsize=(14, 8))

    # Add traces for each gender-based group
    for gender_group, session_data in gender_accuracy.items():
        time_points = []
        accuracy_points = []

        # Loop through all sessions to extract accuracy data
        for session_index in range(1, 9):
            session = f"Session {session_index}"
            if session_index in [1, 4, 5, 8]:  # 'w' sessions
                accuracy_points.extend(session_data[session]['w'])
            else:  # 'wo' sessions
                accuracy_points.extend(session_data[session]['wo'])

            # Generate x-axis values for the blocks of this session
            session_time_points = [i + (session_index - 1) * n for i in range(len(session_data[session]['w']))]
            time_points.extend(session_time_points)

        # Append the last time point for staircase continuation
        time_points.append(time_points[-1] + n)
        accuracy_points.append(accuracy_points[-1])

        # Plot the staircase line
        plt.step(
            time_points,
            accuracy_points,
            where='post',
            color=color_map[gender_group],
            linewidth=2,
            label=gender_group
        )

    # Add shaded areas for sessions with distractions (Sessions 1, 4, 5, 8)
    distraction_sessions = [1, 4, 5, 8]
    for session in distraction_sessions:
        start_x = n * (session - 1)
        end_x = start_x + n
        plt.gca().add_patch(
            patches.Rectangle(
                (start_x, 60), n, 41,  # Width=n, Height=41 (from 60 to 101)
                facecolor='orange',
                alpha=0.2,
                edgecolor='none'
            )
        )

    # Customize the plot
    plt.title('Gender-Based Accuracy Trendline', fontsize=16)
    plt.xlabel('Time (Frames)', fontsize=12)
    plt.ylabel('Accuracy Score (out of 100)', fontsize=12)
    plt.ylim(60, 101)  # Set y-axis limits
    plt.xticks([n * i for i in range(8)], [f'Session {i}' for i in range(1, 9)])  # Match 8 ticks with 8 labels
    plt.legend(loc='best', fontsize=12)
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    # Save the plot to a Base64-encoded string
    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    base64_image = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()
    plt.close()

    return base64_image


def generate_gender_trendline_plot(json_file):
    """
    Generate a Base64-encoded gender trendline plot from a JSON file.

    Parameters:
    - json_file: Path to the JSON file containing gender accuracy data.

    Returns:
    - plot_base64: Base64-encoded string of the plot image.
    """
    gender_accuracy = load_gender_accuracy_from_json(json_file)
    return create_gender_trendline_plot(gender_accuracy, n=120)
