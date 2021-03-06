# -*- coding: utf-8 -*-
"""NLP_Amazon_Data_Preparation_prediction-deploy.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1yRYpeoDWvhvD9ZXk6xfCAs13sGs5GUwD
"""

## import all the necessary libraries
import warnings

#Ignoring unnecessory warnings
warnings.filterwarnings("ignore")                   

import numpy as np                                  #for large and multi-dimensional arrays
import pandas as pd                                 #for data manipulation and analysis
import nltk

##reading dataset
df = pd.read_csv('F:\Data Science projects\By_me\ML\Amazon\Dataset/Reviews.csv')

print(df.shape)
df.head()

df.columns

"""### Data Preparation"""

### add some columns for upvote metrics
df['Helpful %'] = np.where(df['HelpfulnessDenominator'] > 0, df['HelpfulnessNumerator'] / df['HelpfulnessDenominator'], -1)

df.head()



"""#### assigning different different labels to helpful% according to its value"""

df['Helpful %'].unique()

pd.cut(df['Helpful %'] , bins = [-1, 0, 0.2, 0.4, 0.6, 0.8, 1.0], labels = ['Empty', '0-20%', '20-40%', '40-60%', '60-80%', '80-100%'])

df['%upvote'] = pd.cut( df['Helpful %'] , bins = [-1, 0, 0.2, 0.4, 0.6, 0.8, 1.0], labels = ['Empty', '0-20%', '20-40%', '40-60%', '60-80%', '80-100%'])

df.head()

df.groupby(['Score', '%upvote']).agg('count')

"""#### considering only Id Column, as I have to count Total Upvotes for different different categories"""

df.groupby(['Score', '%upvote']).agg({'Id':'count'})

df_s=df.groupby(['Score', '%upvote']).agg({'Id':'count'}).reset_index()
df_s



"""#### create Pivot Table for better conclusion"""

df_s.pivot(index='%upvote',columns='Score')



"""#### create heatmap of it,for better Visualisations"""

import seaborn as sns
import matplotlib.pyplot as plt
sns.heatmap(df_s.pivot(index='%upvote',columns='Score'),annot=True,cmap = 'YlGnBu')
plt.title('How helpful users find among user scores')

"""Key message from above:

Reviews are skewed towards positive
More than half of the reviews are with zero votes
Many people agree with score 5 reviews
"""

df.shape

df.head()

df['Score'].unique()

df2 = df[df['Score'] != 3]
X = df2['Text']
y_dict = {1:0, 2:0, 4:1, 5:1}
y = df2['Score'].map(y_dict)

"""#### Score prediction"""



"""### convert your text into vectors using NLP"""

from sklearn.feature_extraction.text import CountVectorizer
c = CountVectorizer(stop_words = 'english')

##takes almost 2 mins to execute
X_c = c.fit_transform(X)

print('features: {}'.format(X_c.shape[1]))

from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X_c, y)
print(' train records: {}'.format(X_train.shape[0]))

from sklearn.linear_model import LogisticRegression
log=LogisticRegression()

ml =log.fit(X_train, y_train)
acc = ml.score(X_test, y_test)
print ('Model Accuracy: {}'.format(acc))

"""#### fetch Top 20 Positive & Top 20 negative words"""

w = c.get_feature_names()
w

coef = ml.coef_.tolist()[0]
coef

coeff_df = pd.DataFrame({'Word' : w, 'Coefficient' : coef})
coeff_df

coeff_df = coeff_df.sort_values(['Coefficient', 'Word'],ascending=False)
coeff_df

print('-Top 20 positive-')
print(coeff_df.head(20).to_string(index=False))
print('\n')
print('-Top 20 negative-')        
print(coeff_df.tail(20).to_string(index=False))





"""#### lets try to create a function so that I can apply mutliple NLP Techniques + Multiple Ml algos in such a way that I will acheive my best accuracy"""

### create a function 

def text_fit(X, y, nlp_model,ml_model,coef_show=1):
    
    X_c = nlp_model.fit_transform(X)
    print('features: {}'.format(X_c.shape[1]))
    X_train, X_test, y_train, y_test = train_test_split(X_c, y)
    print(' train records: {}'.format(X_train.shape[0]))
    print(' test records: {}'.format(X_test.shape[0]))
    ml =ml_model.fit(X_train, y_train)
    acc = ml.score(X_test, y_test)
    print ('Model Accuracy: {}'.format(acc))
    
    if coef_show == 1: 
        w = nlp_model.get_feature_names()
        coef = ml.coef_.tolist()[0]
        coeff_df = pd.DataFrame({'Word' : w, 'Coefficient' : coef})
        coeff_df = coeff_df.sort_values(['Coefficient', 'Word'], ascending=[0, 1])
        print('\n')
        print('-Top 20 positive-')
        print(coeff_df.head(20).to_string(index=False))
        print('\n')
        print('-Top 20 negative-')        
        print(coeff_df.tail(20).to_string(index=False))

from sklearn.feature_extraction.text import CountVectorizer
c = CountVectorizer(stop_words = 'english')
from sklearn.linear_model import LogisticRegression

text_fit(X, y, c, LogisticRegression())



"""### Lets define a predict function"""

from sklearn.metrics import confusion_matrix,accuracy_score
def predict(X, y, nlp_model,ml_model):
    
    X_c = nlp_model.fit_transform(X)
    print('features: {}'.format(X_c.shape[1]))
    X_train, X_test, y_train, y_test = train_test_split(X_c, y)
    print(' train records: {}'.format(X_train.shape[0]))
    print(' test records: {}'.format(X_test.shape[0]))
    ml =ml_model.fit(X_train, y_train)
    predictions=ml.predict(X_test)
    cm=confusion_matrix(predictions,y_test)
    print(cm)
    acc=accuracy_score(predictions,y_test)
    print(acc)

from sklearn.feature_extraction.text import CountVectorizer
c = CountVectorizer(stop_words = 'english')
from sklearn.linear_model import LogisticRegression
lr=LogisticRegression()

predict(X,y,c,lr)



"""#### Accuracy is around 93.9% - not bad. However we notice that some of those significant coefficients are not meaningful, e.g. 280mg."""

from sklearn.dummy import DummyClassifier

### calling function for dummy classifier 
text_fit(X, y, c, DummyClassifier(),0)



"""#### Logistic regression model on TFIDF"""

from sklearn.feature_extraction.text import TfidfVectorizer
tfidf = TfidfVectorizer(stop_words = 'english')
text_fit(X, y, tfidf, LogisticRegression())

from sklearn.feature_extraction.text import TfidfVectorizer
tfidf = TfidfVectorizer(stop_words = 'english')
predict(X, y, tfidf, LogisticRegression())

"""Accurany is roughly the same - 93.5%. However we notice that the significant words make much more sense now, with higher coefficient magnitude as well!"""







"""#### Upvote prediction

We will be focusing on score 5 reviews, and get rid of comments with neutral votes
"""

data = df[df['Score'] == 5]

data.columns

data2 = data[data['%upvote'].isin(['0-20%', '20-40%', '60-80%', '80-100%'])]
data2.shape

X = data2['Text']

y_dict = {'0-20%': 0, '20-40%': 0, '60-80%': 1, '80-100%': 1}
y = data2['%upvote'].map(y_dict)

print(y.value_counts())

"""#### The target class 'y' is highly skewed , we will observe positive upvotes are too much higher than negative ones.
    Let's resample the data to get balanced data:
"""



from sklearn.feature_extraction.text import TfidfVectorizer

tf=TfidfVectorizer()

X_c=tf.fit_transform(X)

from sklearn.model_selection import train_test_split
X_train,X_test,y_train,y_test=train_test_split(X_c,y,train_size=0.7)

y_test.value_counts()

## RandomOverSampler to handle imbalanced data

from imblearn.over_sampling import RandomOverSampler

os =  RandomOverSampler()

X_train_res, y_train_res = os.fit_sample(X_c, y)

X_train_res.shape,y_train_res.shape

from collections import Counter

print('Original dataset shape {}'.format(Counter(y)))
print('Resampled dataset shape {}'.format(Counter(y_train_res)))

from sklearn.linear_model import LogisticRegression

log_class=LogisticRegression()

grid={'C':10.0 **np.arange(-2,3),'penalty':['l1','l2']}

import numpy as np
from sklearn.model_selection import GridSearchCV

clf=GridSearchCV(estimator=log_class,param_grid=grid,cv=5,n_jobs=-1,scoring='f1_macro')
clf.fit(X_train_res,y_train_res)

y_pred=clf.predict(X_test)
print(confusion_matrix(y_test,y_pred))
print(accuracy_score(y_test,y_pred))











