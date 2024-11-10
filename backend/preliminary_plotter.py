import matplotlib
matplotlib.use('Agg')
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64

def load_accuracy_data(csv_file="accuracy_data.csv"):
    return pd.read_csv(csv_file)

def within_group_plot(data):
    adhd_df = data[data['ADHD_Indication'] == True]
    non_adhd_df = data[data['ADHD_Indication'] == False]
    
    plt.figure(figsize=(14, 6))

    plt.subplot(1, 2, 1)
    sns.boxplot(data=adhd_df[['total_error_w', 'total_error_wo']])
    plt.title('ADHD Group')
    plt.xlabel('Condition')
    plt.ylabel('Accuracy Rate')
    plt.xticks([0, 1], ['With Distraction', 'Without Distraction'])
    plt.ylim([0, 1.05])

    plt.subplot(1, 2, 2)
    sns.boxplot(data=non_adhd_df[['total_error_w', 'total_error_wo']])
    plt.title('Non-ADHD Group')
    plt.xlabel('Condition')
    plt.ylabel('Accuracy Rate')
    plt.xticks([0, 1], ['With Distraction', 'Without Distraction'])
    plt.ylim([0, 1.05])

    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()
    return base64.b64encode(buf.getvalue()).decode('utf-8')

# Function to generate the between-group box plots (comparison of ADHD vs Non-ADHD under both conditions)
def between_group_plot(data):
    adhd_df = data[data['ADHD_Indication'] == True]
    non_adhd_df = data[data['ADHD_Indication'] == False]
    
    plt.figure(figsize=(14, 6))
    
    # Combine the ADHD and Non-ADHD data for plotting
    with_distraction = pd.concat([adhd_df[['total_error_w']].assign(Group='ADHD'),
                                  non_adhd_df[['total_error_w']].assign(Group='Non-ADHD')])
    
    without_distraction = pd.concat([adhd_df[['total_error_wo']].assign(Group='ADHD'),
                                     non_adhd_df[['total_error_wo']].assign(Group='Non-ADHD')])
    
    # Plot for ADHD and Non-ADHD group with distraction
    plt.subplot(1, 2, 1)
    sns.boxplot(x='Group', y='total_error_w', data=with_distraction)
    plt.title('With Distraction')
    plt.xlabel('Group')
    plt.ylabel('Accuracy Rate')
    plt.ylim([0, 1.05])
    
    # Plot for ADHD and Non-ADHD group without distraction
    plt.subplot(1, 2, 2)
    sns.boxplot(x='Group', y='total_error_wo', data=without_distraction)
    plt.title('Without Distraction')
    plt.xlabel('Group')
    plt.ylabel('Accuracy Rate')
    plt.ylim([0, 1.05])

    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()
    return base64.b64encode(buf.getvalue()).decode('utf-8')
