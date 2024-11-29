import os
import json
import matplotlib.pyplot as plt
import numpy as np
import io
import base64

def load_json_as_dict(json_file):
    """Load the JSON file and return it as a dictionary."""
    with open(json_file, 'r') as file:
        return json.load(file)

def apply_running_average(data, window_size=3):
    """Apply a running average filter to smooth the data."""
    return np.convolve(data, np.ones(window_size) / window_size, mode='same')

def create_pose_trendline_plot_by_gender(data, n, threshold):
    """Generate a gender-based pose trendline plot as a Base64-encoded string."""
    gender_colors = {
        'M-ADHD': 'red',
        'F-ADHD': 'green',
        'M-nonADHD': 'blue',
        'F-nonADHD': 'black'
    }

    plt.figure(figsize=(15, 8))
    for gender_group, session_data in data.items():
        all_points, time_points = [], []

        for session_index in range(1, 9):
            session = f'Session {session_index}'
            points = session_data[session]
            all_points.extend(points)
            time_points.extend([i + (session_index - 1) * n for i in range(len(points))])

        if n == 120:
            time_points.append(time_points[-1] + n)
            all_points.append(all_points[-1])

            plt.step(
                time_points, all_points, where='post',
                color=gender_colors.get(gender_group, 'gray'), linewidth=2, label=gender_group
            )
        else:
            # Apply running average filter for n = 12
            all_points = apply_running_average(all_points, window_size=3)
            plt.plot(
                time_points, all_points,
                color=gender_colors.get(gender_group, 'gray'), linewidth=2, label=gender_group
            )

    session_ticks = [n * (i - 1) for i in range(1, 9)]
    plt.xticks(session_ticks, [f'Session {i}' for i in range(1, 9)])

    for i in range(1, 9):
        start_x, end_x = n * (i - 1), n * i
        plt.axvspan(start_x, end_x, facecolor='orange' if i in [1, 4, 5, 8] else 'white', alpha=0.2)

    plt.title(f'Pose Stability by Gender (Threshold={threshold}, n={n})', fontsize=16)
    plt.xlabel('Sessions')
    plt.ylabel('Pose Stability Score (out of 100)')
    plt.legend()
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()

    return base64.b64encode(buf.getvalue()).decode('utf-8')

def generate_pose_trendline_plots_by_gender(base_dir, thresholds):
    """Generate gender-based pose trendline plots for n=12 and n=120."""
    plots = {}
    for threshold in thresholds:
        for n in [12, 120]:
            json_file =  f"../backend/results/pose/pose_trendline_gender_{n}_threshold_{threshold}.json"
            if os.path.exists(json_file):
                data = load_json_as_dict(json_file)
                plots[f"Threshold={threshold}, n={n}"] = create_pose_trendline_plot_by_gender(data, n, threshold)
    return plots
