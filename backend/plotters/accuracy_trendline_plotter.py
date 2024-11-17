import matplotlib
matplotlib.use('Agg')  # Use 'Agg' backend for server-side rendering
import matplotlib.pyplot as plt
import json
import numpy as np
import io
import base64
import os

def load_json_as_dict(json_file):
    """
    Load the JSON file and return it as a dictionary.
    """
    with open(json_file, 'r') as file:
        return json.load(file)

def apply_running_average(data, window_size=3):
    """
    Apply a running average filter to smooth the data.
    """
    return np.convolve(data, np.ones(window_size) / window_size, mode='same')

def generate_trendline_plot(all_sessions_scores, n):
    """
    Generate an accuracy trendline plot and return it as a Base64-encoded string.

    Parameters:
    - all_sessions_scores: Dictionary containing accuracy data for ADHD and Non-ADHD participants.
    - n: Number of blocks per session.
    
    Returns:
    - Base64-encoded image string.
    """
    adhd_all_points = []
    non_adhd_all_points = []
    time_points = []

    for session_index in range(1, 9):
        session = f'Session {session_index}'

        # ADHD and Non-ADHD data points
        if session_index in [1, 4, 5, 8]:  # 'w' sessions with distraction
            adhd_points = all_sessions_scores['ADHD'][session]['w']
            non_adhd_points = all_sessions_scores['Non-ADHD'][session]['w']
        else:  # 'wo' sessions without distraction
            adhd_points = all_sessions_scores['ADHD'][session]['wo']
            non_adhd_points = all_sessions_scores['Non-ADHD'][session]['wo']

        adhd_all_points.extend(adhd_points)
        non_adhd_all_points.extend(non_adhd_points)

        session_time_points = [i + (session_index - 1) * n for i in range(len(adhd_points))]
        time_points.extend(session_time_points)

    #if n < 100:
     #   adhd_all_points = apply_running_average(adhd_all_points)
      #  non_adhd_all_points = apply_running_average(non_adhd_all_points)

    if n == 120:
        time_points.append(time_points[-1] + n)
        adhd_all_points.append(adhd_all_points[-1])
        non_adhd_all_points.append(non_adhd_all_points[-1])

    # Plotting
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

    for i in range(1, 9):
        session_time_start = n * (i - 1)
        session_time_end = n * i
        if i in [1, 4, 5, 8]:  # Sessions with distraction
            ax.axvspan(session_time_start, session_time_end, facecolor='yellow', alpha=0.3)
        else:  # Sessions without distraction
            ax.axvspan(session_time_start, session_time_end, facecolor='white', alpha=0.2)

    for tick in session_ticks:
        plt.axvline(x=tick, color='gray', linestyle='--', linewidth=0.5)

    plt.title(f'Accuracy Over Time Across All Sessions (n={n} Blocks Per Session)', fontsize=16)
    plt.xlabel('Sessions', fontsize=12)
    plt.ylabel('Accuracy Score (out of 100)', fontsize=12)
    plt.legend()

    # Save the plot to a BytesIO buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()

    # Convert the buffer to a Base64 string
    return base64.b64encode(buf.getvalue()).decode('utf-8')

def generate_plots():
    """
    Generate trendline plots for n=12 and n=120 and return them as Base64-encoded strings.

    Returns:
    - A dictionary containing Base64-encoded strings of the plots.
    """
    plots = {}
    for n in [12, 120]:
        filename = f"../backend/results/trendline_accuracy_{n}.json"
        json_file = os.path.abspath(filename)
        if os.path.exists(json_file):
            data = load_json_as_dict(json_file)
            plots[f"n={n}"] = generate_trendline_plot(data, n)
        else:
            print(f"JSON file for n={n} not found.")
    return plots
