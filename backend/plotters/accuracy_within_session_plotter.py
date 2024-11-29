# plotters/accuracy_within_session_plotter.py

import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64

def generate_within_session_box_plots(merged_df):
    plots = {}

    # ADHD group
    adhd_df = merged_df[merged_df['ADHD_Indication'] == True]
    plt.figure(figsize=(8, 6))
    sns.boxplot(data=adhd_df[['w_accuracy', 'wo_accuracy']])
    plt.title('ADHD Group: Accuracy with and without Distraction')
    plt.xlabel('Condition')
    plt.ylabel('Accuracy')
    plt.ylim(0.5, 1.05)
    plt.xticks([0, 1], ['With Distraction', 'Without Distraction'])
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    plots['ADHD'] = base64.b64encode(buf.getvalue()).decode('utf-8')

    # Non-ADHD group
    non_adhd_df = merged_df[merged_df['ADHD_Indication'] == False]
    plt.figure(figsize=(8, 6))
    sns.boxplot(data=non_adhd_df[['w_accuracy', 'wo_accuracy']])
    plt.title('Non-ADHD Group: Accuracy with and without Distraction')
    plt.xlabel('Condition')
    plt.ylabel('Accuracy')
    plt.ylim(0.5, 1.05)
    plt.xticks([0, 1], ['With Distraction', 'Without Distraction'])
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    plots['Non-ADHD'] = base64.b64encode(buf.getvalue()).decode('utf-8')

    return plots

