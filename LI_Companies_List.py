# Import packages
import os as os
import pandas as pd
import re
import numpy as np
import nltk
from nltk.corpus import stopwords
import string

# Set working directory
os.chdir('C:\\Users\\calmp\\OneDrive\\0 - Job Applications\\Job Apps\\Portfolio\\LinkedIn job analysis')

# Import dataframe
df = pd.read_csv('LI_Companies.csv')
df.columns = ['Description']



# Keep entries that contain Product Analyst
df['Keep'] = df['Description'].apply(lambda l: 1 if 'product analyst' in l.lower() else 0)
df = df[df['Keep']==1]

# Keep entries with a company
df['Keep'] = df['Description'].apply(lambda l: 1 if ' at ' in l.lower() else 0)
df = df[df['Keep']==1]

# Keep text after 'at'
df['Company'] = df['Description'].apply(lambda l: l.split(" at ", 1)[1])

# Keep text before '-'
df['Company'] = df['Company'].apply(lambda l: l.split(" - ", 1)[0])



# Summarise counts
companies= df.groupby('Company').count()
companies = companies.sort_values('Description', ascending = False)

# Export dataframe
path = 'C:\\Users\\calmp\\OneDrive\\0 - Job Applications\\Job Apps\\Portfolio\\LinkedIn job analysis\\LI_Companies_List.csv'
companies.to_csv(path, index = True)
