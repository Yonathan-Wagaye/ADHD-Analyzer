import os
import json
import matplotlib.pyplot as plt
import io
import base64
from analyzer.pose_trendline_stat_analyzer import get_pose_pvalues_array


def load_json_as_dict(json_file):
    """Load the JSON file and return it as a dictionary."""
    with open(json_file, 'r') as file:
        return json.load(file)


def generate_pose_trendline_plot(data, n, threshold, p_values):
    """
    Generate a pose trendline plot and return it as a Base64-encoded string.

    Parameters:
    - data: Dictionary containing pose stability data for ADHD and Non-ADHD participants.
    - n: Number of blocks per session.
    - threshold: Pose threshold being analyzed.
    - p_values: List of p-values for each session.

    Returns:
    - Base64-encoded image string.
    """
    adhd_all_points = []
    non_adhd_all_points = []
    time_points = []

    for session_index in range(1, 9):
        session = f'Session {session_index}'

        adhd_points = data['ADHD'][session]
        non_adhd_points = data['Non-ADHD'][session]

        adhd_all_points.extend(adhd_points)
        non_adhd_all_points.extend(non_adhd_points)

        session_time_points = [i + (session_index - 1) * n for i in range(len(adhd_points))]
        time_points.extend(session_time_points)

    fig, ax = plt.subplots(figsize=(15, 8))
    if n == 120:
        ax.step(time_points, adhd_all_points, 'r-', label='ADHD', where='post', linewidth=2)
        ax.step(time_points, non_adhd_all_points, 'b-', label='Non-ADHD', where='post', linewidth=2)
    else:
        ax.plot(time_points, adhd_all_points, 'r-', label='ADHD', linewidth=2)
        ax.plot(time_points, non_adhd_all_points, 'b-', label='Non-ADHD', linewidth=2)

    session_ticks = [n * (i - 1) for i in range(1, 9)]
    session_labels = [f'Session {i}' for i in range(1, 9)]
    plt.xticks(session_ticks, session_labels)

    max_y = max(max(adhd_all_points), max(non_adhd_all_points))

    for i in range(1, 9):
        session_time_start = n * (i - 1)
        session_time_end = n * i
        if i in [1, 4, 5, 8]:  # Sessions with distraction
            ax.axvspan(session_time_start, session_time_end, facecolor='yellow', alpha=0.3)
        else:  # Sessions without distraction
            ax.axvspan(session_time_start, session_time_end, facecolor='white', alpha=0.2)

        # Annotate p-values only if n == 120
        if n == 120 and i - 1 < len(p_values):  # Ensure index is within range
            p_value = p_values[i - 1]
            color = 'red' if p_value < 0.05 else 'black'
            # Position p-values slightly below the top of the plot area
            plt.text((session_time_start + session_time_end) / 2, max_y + 2,
                     f"p={p_value:.3f}", ha='center', fontsize=10, color=color)

    for tick in session_ticks:
        plt.axvline(x=tick, color='gray', linestyle='--', linewidth=0.5)

    plt.title(f'Pose Stability (n={n}, Threshold={threshold})', fontsize=16)
    plt.xlabel('Sessions', fontsize=12)
    plt.ylabel('Pose Stability Score (out of 100)', fontsize=12)
    plt.legend()

    # Save the plot to a BytesIO buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()

    return base64.b64encode(buf.getvalue()).decode('utf-8')



def generate_pose_trendline_plots(base_dir, thresholds=[15]):
    """Generate plots for both n=12 and n=120 and include p-values."""
    p_values = get_pose_pvalues_array()  # Fetch p-values only for n=120
    plots = {}
    for threshold in thresholds:
        for n in [12, 120]:
            json_file = f"../backend/results/pose/pose_trendline_{n}_threshold_{threshold}.json"
            if os.path.exists(json_file):
                data = load_json_as_dict(json_file)
                plot_key = f"Threshold={threshold}, n={n}"
                plots[plot_key] = generate_pose_trendline_plot(data, n, threshold, p_values if n == 120 else [])
            else:
                print(f"JSON file for n={n}, threshold={threshold} not found.")
    return plots
