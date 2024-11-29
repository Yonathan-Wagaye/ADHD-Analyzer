# analyzer/accuracy_within_session_analyzer.py

import scipy.stats as stats

def stat_test(x, y, alt='two-sided', option='indep'):
    wx, px = stats.shapiro(x)
    wy, py = stats.shapiro(y)
    if px > 0.05 and py > 0.05:
        # Perform t-test
        if option == 'indep':
            levene_stat, levene_p_val = stats.levene(x, y)
            if levene_p_val > 0.05:
                t_stat, p_val = stats.ttest_ind(x, y, alternative=alt)
            else:
                t_stat, p_val = stats.ttest_ind(x, y, alternative=alt, equal_var=False)
        else:
            t_stat, p_val = stats.ttest_rel(x, y, alternative=alt)
    else:
        # Perform non-parametric test
        if option == 'indep':
            t_stat, p_val = stats.mannwhitneyu(x, y, alternative=alt)
        else:
            t_stat, p_val = stats.wilcoxon(x - y)
    return t_stat, p_val

def analyze_within_session_accuracy(merged_df):
    # Separate data into groups
    adhd_group = merged_df[merged_df['ADHD_Indication'] == True]
    non_adhd_group = merged_df[merged_df['ADHD_Indication'] == False]

    # Extract accuracies
    adhd_accuracy_w = adhd_group['w_accuracy']
    adhd_accuracy_wo = adhd_group['wo_accuracy']
    non_adhd_accuracy_w = non_adhd_group['w_accuracy']
    non_adhd_accuracy_wo = non_adhd_group['wo_accuracy']

    results = {}

    # Between-group comparisons
    t_stat, p_val = stat_test(adhd_accuracy_w, non_adhd_accuracy_w, option='indep')
    results['ADHD vs Non-ADHD (With Distraction)'] = {'t_statistic': t_stat, 'p_value': p_val}

    t_stat, p_val = stat_test(adhd_accuracy_wo, non_adhd_accuracy_wo, option='indep')
    results['ADHD vs Non-ADHD (Without Distraction)'] = {'t_statistic': t_stat, 'p_value': p_val}

    # Within-group comparisons
    t_stat, p_val = stat_test(adhd_accuracy_w, adhd_accuracy_wo, option='dep')
    results['ADHD (With vs Without Distraction)'] = {'t_statistic': t_stat, 'p_value': p_val}

    t_stat, p_val = stat_test(non_adhd_accuracy_w, non_adhd_accuracy_wo, option='dep')
    results['Non-ADHD (With vs Without Distraction)'] = {'t_statistic': t_stat, 'p_value': p_val}

    return results

