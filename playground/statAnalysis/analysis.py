from pandas import *
import numpy as np
from scipy import stats

# Getting data
experimentDF = read_csv('parasite_data.csv', na_values=[' '])
print(experimentDF)

# Accessing data
print(experimentDF['Virulence'])
print(experimentDF['ShannonDiversity'][12])
print(experimentDF[experimentDF['ShannonDiversity'] > 2.0])

# Handling NA values
print(experimentDF[np.isnan(experimentDF['Virulence'])])
print('Mean virulance accros all treatments: {}'.format(experimentDF['Virulence'].mean()))
print('Mean virulance accros all treatments: {}'.format(stats.sem(experimentDF['Virulence'])))
# NA issue solution
print(experimentDF['Virulence'].dropna())       #first idea
print ("Mean virulence across all treatments w/ dropped NaN:",
		experimentDF["Virulence"].dropna().mean())
print(experimentDF.fillna(0.0)['Virulence'])    #second one
print ("Mean virulence across all treatments w/ filled NaN:",
		experimentDF.fillna(0.0)["Virulence"].mean())

# Analysis: mean
print ("Mean Shannon Diversity w/ 0.8 Parasite Virulence ={}"
        .format(experimentDF[experimentDF["Virulence"] == 0.8]["ShannonDiversity"].mean()))
# Analysis: variance
# -> getting a metric of data consistency
print ("Variance Shannon Diversity w/ 0.8 Parasite Virulence = {}"
		.format(experimentDF[experimentDF["Virulence"] == 0.8]["ShannonDiversity"].var()))
# Analysis: Standard error of the mean (SEM)
# -> getting a range where most of the future data will fall-in, reliable with 20 replicates
print ("SEM Shannon Diversity w/ 0.8 Parasite Virulence = {}"
		.format(stats.sem(experimentDF[experimentDF["Virulence"] == 0.8]["ShannonDiversity"])))
# Analysis: Mann-Whitney-Wilcoxon (MWW) Ransum test
# -> Getting a correlation indicator [0, 1] between two datasets
dist1 = experimentDF[experimentDF['Virulence'] == 0.5]['ShannonDiversity']
dist2 = experimentDF[experimentDF['Virulence'] == 0.8]['ShannonDiversity']
z_stat, p_val = stats.ranksums(dist1, dist2)
print('MWW Ranksum P for distribution 1 and 2 = {} ({})'.format(p_val, z_stat))

# Analysis: One-way analysis of variance (ANOVA)
# -> Getting a correlation indicator [0, 1] between more than two datasets
dist1 = experimentDF[experimentDF['Virulence'] == 0.7]['ShannonDiversity']
dist2 = experimentDF[experimentDF['Virulence'] == 0.8]['ShannonDiversity']
dist3 = experimentDF[experimentDF['Virulence'] == 0.9]['ShannonDiversity']
f_val, p_val = stats.f_oneway(dist1, dist2, dist3)
print('One-way ANOVA P = {} ({})'.format(p_val, f_val))

# Analysis: Boostraping 95% confidence intervals
# -> Beat SEM
