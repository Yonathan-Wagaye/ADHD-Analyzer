from scipy import stats
import numpy as np

def stat_test(x, y, alt='two-sided', option='indep'):
    wx, px = stats.shapiro(x)
    wy, py = stats.shapiro(y)
    t_stat, p_val = [0, 0]
    if px > 0.05 and py > 0.05:
        if option == 'indep':
            levene_stat, levene_p_val = stats.levene(x, y)
            if levene_p_val > 0.05:
                t_stat, p_val = stats.ttest_ind(x, y, alternative=alt)
            else:
                t_stat, p_val = stats.ttest_ind(x, y, alternative=alt, equal_var=False)
        else:
            t_stat, p_val = stats.ttest_rel(x, y, alternative=alt)
    else:
        if option == 'indep':
            t_stat, p_val = stats.ranksums(x, y, alternative=alt)
        else:
            t_stat, p_val = stats.wilcoxon(x, y, alternative=alt)
    return t_stat, p_val

def calculate_correlation(x, y):
    correlation, p_value = stats.pearsonr(x, y)
    return correlation, p_value

def chi_square_test(observed, expected):
    chi2, p_val = stats.chisquare(f_obs=observed, f_exp=expected)
    return chi2, p_val
