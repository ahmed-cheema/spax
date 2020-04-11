import pandas as pd
import numpy as np

## using the ridge regression (like regularized adjusted plus minus, or RAPM) to quantify individual performance of nba officials based on l2m reports

refs = list(set((tuple(df.ref_1.unique()) + tuple(df.ref_2.unique()) + tuple(df.ref_3.unique()))))

refs.sort()

for i in range(1,len(refs)+1):
    
    df2['r'+str(i)] = 0

labels = []
    
for i in range(1,len(refs)+1):
    item = 'r'+str(i)
    labels.append(item)

db = pd.DataFrame({'label': labels, 'ref': refs})

def stint(ref_1,ref_2,ref_3):
    local_refs = [ref_1,ref_2,ref_3]
    
    if refs[i-1] in local_refs:
        return 1
    else:
        return 0
        
for i in range(1,len(refs)+1):
    df2['r'+str(i)] = np.vectorize(stint)(df2.ref_1,df2.ref_2,df2.ref_3)
    
matrix = df2[df2.columns[38:128]]
            
matrix['events'] = 1

group_cols = [o for o in matrix.columns if (o != 'correct_decision') & (o != 'events')]
aug = matrix.groupby(group_cols).sum().reset_index()

aug['accuracy'] = (aug.correct_decision / aug.events)
aug['accuracy'] = (aug.accuracy - aug.accuracy.mean())/aug.accuracy.std(ddof=0)

A = aug[aug.columns[0:89]].to_numpy()
B = aug.accuracy.to_numpy()
A_M = np.transpose(A).dot(A)
B_M = np.transpose(A).dot(B)
lam = 35
beta = (np.linalg.inv(A_M + lam*np.identity(len(A_M))).dot(B_M))

final = pd.DataFrame(labels,beta).reset_index(drop=False)
final.columns = ['val','label']
final = pd.merge(final,db[['label','ref']],on='label')

final['events'] = 0
for n in range(0,89):
    final['events'][n] = matrix[final[final.ref == final.ref[n]].label.values[0]].sum()
    
final = final[['ref','events','val']]
