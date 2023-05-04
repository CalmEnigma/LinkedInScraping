# Import packages
import os as os
import pandas as pd
import re
import numpy as np
import nltk
from nltk.corpus import stopwords
import string
import sklearn
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.preprocessing import scale

# Set working directory
os.chdir('C:\\Users\\calmp\\OneDrive\\0 - Job Applications\\Job Apps\\Portfolio\\LinkedIn job analysis')

# Import dataframe
df = pd.read_csv('LI_Data.csv')




# Clean job ID
df['ID'] = df['ID'].fillna('N/A')
df['ID'] = df['ID'].apply(lambda l: l.replace('urn:li:jobPosting:', ""))

# Split location date
df[['City', 'Country A', 'Country B']] = df['Location'].str.split(', ', 2, expand=True)

# Clean applicants
df['Applicants'] = df['Applicants'].apply(lambda l:[int(s) for s in l.split() if s.isdigit()][0])

# Clean description
df["Description"] = df["Description"].str.replace("\n", " ")

# Clean other criteria
sep = "@"
df["Other criteria"] = df["Other criteria"].str.replace("\n", sep)



## Define function to separate criteria
def crit_sep(string):
    
    # Empty dataframe with criteria headings
    df_crit = pd.DataFrame(columns=['Seniority level', 'Employment type',
                              'Job function', 'Industries'])
    
    # The various criteria
    criteria = ['Seniority level', f'{sep}Employment type', f'{sep}Job function', f'{sep}Industries']
    index = 0
    
    # Separating the relevant criteria
    for i in criteria:
        
        # Get criteria to remove for this output
        drop = criteria.copy()
        drop.remove(i)
            
        # Drop criteria before the one needed
        if i in string:
            x = string[np.max([string.find(i)+len(i), 0]):]

            # Drop criteria after the one needed
            for j in drop:
                if j in x:
                    x = x[:x.find(j)]
                    
            # Fix separators and add & for multiple results
            x = x[1:]
            x = x.replace(sep, " & ")
                    
        else:
            x = float('nan')
                
        # Populate dataframe
        df_crit.loc[index, i.replace(sep, "")] = x
        
    index = index+1
    return df_crit
        
## Apply function and add to main df
df_crit = []
for i in df['Other criteria']:
    df_crit.append(crit_sep(i))
df_crit = pd.concat(df_crit, ignore_index=True)
df[list(df_crit.columns)] = df_crit

## Replace some entries
df.loc[df['Seniority level']=='Not Applicable', 'Seniority level'] = float('nan')






# Get individual words of the description

## Define description cleaning function
def desc_clean(desc):
    
    # Replace punctuation with a space
    translator = str.maketrans(string.punctuation, ' '*len(string.punctuation))
    desc = desc.translate(translator)
    
    # Remove other symbols
    desc = desc.replace('’', "")

    # Remove stopwords
    desc = [word.strip() for word in desc.split() if word.lower() not in stopwords.words('english')]
    
    # Output
    return desc

## Apply function
df_desc = pd.DataFrame(columns=['Words'])
df_desc['Words'] = df['Description'].apply(lambda l: desc_clean(l))





# Get years of experience

## Define function
def exp_loc(w_list):
    
    ## Setup
    x = []  
    words = []
    years = []
    n = 0
    
    ## Find locations where the word 'experience' is present
    for w in w_list:
        if (w.lower() == 'year') | (w.lower() == 'years') | (w.lower() == 'yrs'):
            x.append(n)
        n = n+1
    
    ## Get the range of words before and after the location
    delta = 4
    for a in x:
        n_range = list(range(np.max([a-delta, 0]),
                        np.min([a+delta, len(w_list)])))
        
        ## Get the words in the range
        b = list(map(w_list.__getitem__, n_range))
        
        ## If some of the words include 'exp' or 'work', add to list, otherwise drop
        if ('work' in " ".join(b).lower()) | ('exp' in " ".join(b).lower()):
            words.extend(b)
        
    
    ## Extract integers
    for i in words:
        try:
            int(i)
            years.append(int(i))
        except:
            next
    
    ## Remove integers larger than 10
    years = [item for item in years if ((item <= 10) & (item >0))]
    
    ## Return maximum value
    if len(years)>0:
        years = np.max(years)
    else:
        years = float('nan')
    
    ## Return output
    return years
    
## Apply function
df_desc['Exp_Yrs'] = df_desc['Words'].apply(lambda l: exp_loc(l))

## Add to main df
df['Exp_Yrs'] = df_desc['Exp_Yrs']




x = df_desc[df['Company']=='Moonpig']




# Extract salary

## Define function
def get_sal(desc, minmax):
    
    ## Make lowercase
    desc = desc.lower()
    
    ### Remove commas with nothing, and dashes with spaces
    desc = desc.replace(',', "")
    desc = desc.replace('-', " ")
    
    ### Replace punctuation with a space
    translator = str.maketrans(string.punctuation, ' '*len(string.punctuation))
    desc = desc.translate(translator)
    
    ### Remove words that don't have £
    desc = [word for word in desc.split() if '£' in word]
    
    ### Clean extracts 
    n = 0
    k = -1
    for word in desc:
        
        # Replace thousands sign in current word and add to previous word if k exists
        # Replace previous word because often you get £50-60k or similar
        if 'k' in word:
            word = word.replace('000k', 'k')
            word = word.replace('k', '000')
            
            # Replace previous word if previous did not include k
            if k != n-1:
                try:
                    desc[n-1] = str(desc[n-1])+'000'
                except(ValueError):
                    next
                
            # Set k = n to avoid multiply by 1000 when both values are given in k
            k = n
        
        # Remove currency
        word = word.replace('£', '')
        
        # Remove if millions or billions
        if ('m' in word) | ('b' in word):
            word = ""
        
        # Only keep numbers
        word = ''.join(c for c in word if c.isdigit())
        
        # Replace old string with new
        desc[n] = word
        n = n+1


    ### Drop empty values and numbers smaller than 15k and larger than 150k
    desc = [word for word in desc if word != ""]
    desc = [word for word in desc if int(word) > 15000]
    desc = [word for word in desc if int(word) < 150000]
    
    ### Get min and max and return
    if len(desc) > 0:
        desc = np.array(desc).astype(float)
        
        if minmax == 'min':
            sal = np.min(desc)
            
        else: 
            sal = np.max(desc)
    
    ### Output
        return sal
    
    else:
        return float('nan')


## Apply function
df['Min_Salary'] = df['Description'].apply(lambda l: get_sal(l, 'min'))
df['Max_Salary'] = df['Description'].apply(lambda l: get_sal(l, 'max'))








# Clean job title

## Combine all titles and display frequency of each word

### Combine all titles
x = " ". join(list(df['Title']))

### Replace all punctuation with a space
translator = str.maketrans(string.punctuation, ' '*len(string.punctuation))
x = x.translate(translator)
x = x.replace('-', '')
x = x.lower()

### Only keep nouns
#### Use ntlk to tag each word
x = nltk.word_tokenize(x)
x = pd.DataFrame(nltk.pos_tag(x), columns = ['Word', 'Tag'])

#### Remove locations
x = x[x['Tag'] == 'NN']

### Count each word
x = pd.DataFrame(x, columns = ['Word'])
title_count = x.groupby('Word').size().reset_index().sort_values(by = 0, ascending = False)
title_count.columns = ['Word', 'Count']



## Find most relevant groups
### Normalise frequency of each word and drop anything lower than 0.1
title_count['Scaled'] = sklearn.preprocessing.minmax_scale(title_count['Count'])
title_count = title_count[title_count['Scaled']>=0.1]

### Drop title names and add 'Other' category
title_names = ['analyst', 'associate', 'manager', 'director']
title_groups = list(title_count['Word'][-(title_count['Word'].isin(title_names))])
title_groups.append('other')



## Assign titles to main groups

### Define assigning function
def ass_group(title, output = 'role'):
    
    # Make lower
    title = title.lower()
    
    # Get title name, or assign Other if unavailable
    role = []
    for name in title_names:
        if name in title:
            role = name
            next
    
    if len(role) < 1:
        role = 'Other'

    
    # Get relevant groups
    grp = []
    for group in title_groups:
        if group in title:
            grp.append(group)
    
    if len(grp) < 1:
        grp.append('Other')    
    
    # Output
    if output == 'role':
        return role
    else:
        return grp

### Apply function
df['Role Suffix'] = df.apply(lambda l: ass_group(l['Title']), axis=1)   
df['Role Group'] = df.apply(lambda l: ass_group(l['Title'], 'group'), axis=1)

### Create df columns for each group
for grp in title_groups:
    df[grp] = df['Role Group'].apply(lambda l: True if grp in l else False)    








# Clean industries





# Clean job function





# NLP on job description
##nltk.download_shell()
##nltk.download() downloaded the popular ones

## Run bag of words -> produce a matrix of all the words
#bow_mod = CountVectorizer(analyzer=desc_clean).fit(df['Description'])

## Total number of vocab words
#print(bow_mod.vocabulary_)



### https://www.kaggle.com/code/sanabdriss/nlp-extract-skills-from-job-descriptions







# Export dataframe
path = 'C:\\Users\\calmp\\OneDrive\\0 - Job Applications\\Job Apps\\Portfolio\\LinkedIn job analysis\\LI_Data_Clean.csv'
df.to_csv(path, index = False)


