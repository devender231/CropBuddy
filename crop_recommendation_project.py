# -*- coding: utf-8 -*-
"""Crop_Recommendation_Project.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1zsivbwy7fOVYABw-0gLKwNVLmssC2IlR

# Crop Recommendation

### **Importing Libraries**
"""

# Commented out IPython magic to ensure Python compatibility.
import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
# %matplotlib inline
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

from sklearn.metrics import classification_report
from sklearn import metrics
from sklearn import tree
from sklearn.model_selection import cross_val_score
from sklearn.metrics import confusion_matrix

import warnings
warnings.filterwarnings('ignore')

"""### **Loading Data**"""

crop = pd.read_csv('Augmented_Crop_recommendation.csv')
crop.head(5)

"""### **Exploratory Data Analysis (EDA)**"""

crop.info()

crop.describe()

crop.columns

crop.shape

crop['label'].unique()

crop['label'].nunique()

crop['label'].value_counts()

sns.heatmap(crop.isnull(), cmap="coolwarm")
plt.show()

plt.figure(figsize=(12,5))
plt.subplot(1,2,1)
sns.distplot(crop['temperature'],color="red",bins=15,hist_kws={'alpha':0.5})
plt.subplot(1,2,2)
sns.distplot(crop['ph'],color="green",bins=15,hist_kws={'alpha':0.5})
plt.show()

sns.pairplot(crop,hue='label')
plt.show()

sns.jointplot(x="rainfall",y="humidity",data=crop[(crop['temperature']<40) &
                                                  (crop['rainfall']>40)],height=10,hue="label")
plt.show()

sns.set_theme(style="whitegrid")
fig, ax = plt.subplots(figsize=(30,15))
sns.boxplot(x='label',y='ph',data=crop)
plt.show()

f = list(crop.columns)
f.remove('label')
features=crop[f]

target = crop['label']

for feature in features:
    plt.figure(figsize=(8, 4))
    sns.histplot(crop[feature], kde=True)
    plt.title(f"Distribution of {feature}")
    plt.show()

crop_conditions = crop.describe()
print(crop_conditions)
crop_conditions.to_csv('crop_conditions.csv')
for feature in features:
    plt.figure(figsize=(12, 6))
    sns.boxplot(x='label', y=feature, data=crop)
    plt.title(f"{feature.capitalize()} Distribution for Each Crop")
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.show()

fig, ax = plt.subplots(1, 1, figsize=(15, 9))
sns.heatmap(features.corr(), annot=True,cmap='viridis')
ax.set(xlabel='features')
ax.set(ylabel='features')
plt.title('Correlation between different features', fontsize = 15, c='black')
plt.show()

crop_summary = pd.pivot_table(crop,index=['label'],aggfunc='mean')
crop_summary.head()

fig = go.Figure()
fig.add_trace(go.Bar(
    x=crop_summary.index,
    y=crop_summary['N'],
    name='Nitrogen',
    marker_color='mediumvioletred'
))
fig.add_trace(go.Bar(
    x=crop_summary.index,
    y=crop_summary['P'],
    name='Phosphorous',
    marker_color='springgreen'
))
fig.add_trace(go.Bar(
    x=crop_summary.index,
    y=crop_summary['K'],
    name='Potash',
    marker_color='dodgerblue'
))

fig.update_layout(title="N-P-K values comparision between crops",
                  plot_bgcolor='white',
                  barmode='group',
                  xaxis_tickangle=-45)

fig.show()

"""### **Feature Selection**"""

features.head()

target.head()

acc = []
model = []

from sklearn.model_selection import train_test_split
x_train, x_test, y_train, y_test = train_test_split(features,target,test_size = 0.2,random_state =2)

"""## **Modeling Classification Algorithms**

### **K-Nearest Neighbors**
"""

from sklearn.neighbors import KNeighborsClassifier
knn = KNeighborsClassifier()

knn.fit(x_train,y_train)

predicted_values = knn.predict(x_test)

x = metrics.accuracy_score(y_test, predicted_values)
acc.append(x)
model.append('K Nearest Neighbours')
print("KNN Accuracy is: ", x)

print(classification_report(y_test,predicted_values))

score = cross_val_score(knn,features,target,cv=5)
print('Cross validation score: ',score)

knn_train_accuracy = knn.score(x_train,y_train)
print("knn_train_accuracy = ",knn.score(x_train,y_train))

knn_test_accuracy = knn.score(x_test,y_test)
print("knn_test_accuracy = ",knn.score(x_test,y_test))

y_pred = knn.predict(x_test)
y_true = y_test

cm_knn = confusion_matrix(y_true,y_pred)

f, ax = plt.subplots(figsize=(15,10))
sns.heatmap(cm_knn, annot=True, linewidth=0.5, fmt=".0f",cmap='viridis', ax = ax)
plt.xlabel('Predicted')
plt.ylabel('Actual')
plt.title('Predicted vs actual')
plt.show()

"""**Hyperparameter Tuning**"""

mean_acc = np.zeros(20)
for i in range(1,21):
    knn = KNeighborsClassifier(n_neighbors = i).fit(x_train,y_train)
    yhat= knn.predict(x_test)
    mean_acc[i-1] = metrics.accuracy_score(y_test, yhat)
mean_acc

loc = np.arange(1,21,step=1.0)
plt.figure(figsize = (10, 6))
plt.plot(range(1,21), mean_acc)
plt.xticks(loc)
plt.xlabel('Number of Neighbors ')
plt.ylabel('Accuracy')
plt.show()

from sklearn.model_selection import GridSearchCV
grid_params = { 'n_neighbors' : [12,13,14,15,16,17,18],
               'weights' : ['uniform','distance'],
               'metric' : ['minkowski','euclidean','manhattan']}

gs = GridSearchCV(KNeighborsClassifier(), grid_params, verbose = 1, cv=3, n_jobs = -1)
g_res = gs.fit(x_train, y_train)

g_res.best_score_

g_res.best_params_

knn_1 = KNeighborsClassifier(n_neighbors = 12, weights = 'distance',algorithm = 'brute',metric = 'manhattan')
knn_1.fit(x_train, y_train)

knn_train_accuracy = knn_1.score(x_train,y_train)
print("knn_train_accuracy = ",knn_1.score(x_train,y_train))

knn_test_accuracy = knn_1.score(x_test,y_test)
print("knn_test_accuracy = ",knn_1.score(x_test,y_test))

"""### **Decision Tree**"""

from sklearn.tree import DecisionTreeClassifier
DT = DecisionTreeClassifier(criterion="entropy",random_state=2,max_depth=5)

DT.fit(x_train,y_train)

predicted_values = DT.predict(x_test)
x = metrics.accuracy_score(y_test, predicted_values)
acc.append(x)
model.append('Decision Tree')
print("Decision Tree's Accuracy is: ", x*100)

print(classification_report(y_test,predicted_values))

score = cross_val_score(DT, features, target,cv=5)
print('Cross validation score: ',score)

dt_train_accuracy = DT.score(x_train,y_train)
print("Training accuracy = ",DT.score(x_train,y_train))

dt_test_accuracy = DT.score(x_test,y_test)
print("Testing accuracy = ",DT.score(x_test,y_test))

y_pred = DT.predict(x_test)
y_true = y_test

cm_dt = confusion_matrix(y_true,y_pred)

f, ax = plt.subplots(figsize=(15,10))
sns.heatmap(cm_dt, annot=True, linewidth=0.5, fmt=".0f",  cmap='viridis', ax = ax)
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.title('Predicted vs actual')
plt.show()

"""### **Random Forest**"""

from sklearn.ensemble import RandomForestClassifier

RF = RandomForestClassifier(n_estimators=20, random_state=0)
RF.fit(x_train,y_train)

predicted_values = RF.predict(x_test)

x = metrics.accuracy_score(y_test, predicted_values)
acc.append(x)
model.append('RF')
print("Random Forest Accuracy is: ", x)

print(classification_report(y_test,predicted_values))

score = cross_val_score(RF,features,target,cv=5)
print('Cross validation score: ',score)

rf_train_accuracy = RF.score(x_train,y_train)
print("Training accuracy = ",RF.score(x_train,y_train))

rf_test_accuracy = RF.score(x_test,y_test)
print("Testing accuracy = ",RF.score(x_test,y_test))

y_pred = RF.predict(x_test)
y_true = y_test

cm_rf = confusion_matrix(y_true,y_pred)

f, ax = plt.subplots(figsize=(15,10))
sns.heatmap(cm_rf, annot=True, linewidth=0.5, fmt=".0f",  cmap='viridis', ax = ax)
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.title('Predicted vs actual')
plt.show()

"""### **Naive Bayes Classifier**"""

from sklearn.naive_bayes import GaussianNB
NaiveBayes = GaussianNB()

NaiveBayes.fit(x_train,y_train)

predicted_values = NaiveBayes.predict(x_test)
x = metrics.accuracy_score(y_test, predicted_values)
acc.append(x)
model.append('Naive Bayes')
print("Naive Bayes Accuracy is: ", x)

print(classification_report(y_test,predicted_values))

score = cross_val_score(NaiveBayes,features,target,cv=5)
print('Cross validation score: ',score)

nb_train_accuracy = NaiveBayes.score(x_train,y_train)
print("Training accuracy = ",NaiveBayes.score(x_train,y_train))

nb_test_accuracy = NaiveBayes.score(x_test,y_test)
print("Testing accuracy = ",NaiveBayes.score(x_test,y_test))

y_pred = NaiveBayes.predict(x_test)
y_true = y_test

cm_nb = confusion_matrix(y_true,y_pred)

f, ax = plt.subplots(figsize=(15,10))
sns.heatmap(cm_nb, annot=True, linewidth=0.5, fmt=".0f",  cmap='viridis', ax = ax)
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.title('Predicted vs actual')
plt.show()

"""### **Accuracy Comparision**"""

plt.figure(figsize=[14,7],dpi = 100, facecolor='white')
plt.title('Accuracy Comparison')
plt.xlabel('Accuracy')
plt.ylabel('ML Algorithms')
sns.barplot(x = acc,y = model,palette='viridis')
plt.savefig('plot.png', dpi=300, bbox_inches='tight')

label = ['KNN', 'Decision Tree','Random Forest','Naive Bayes']
Test = [knn_test_accuracy, dt_test_accuracy,rf_test_accuracy,
        nb_test_accuracy]
Train = [knn_train_accuracy,  dt_train_accuracy, rf_train_accuracy,
         nb_train_accuracy]

f, ax = plt.subplots(figsize=(20,7))
X_axis = np.arange(len(label))
plt.bar(X_axis - 0.2,Test, 0.4, label = 'Test', color=('midnightblue'))
plt.bar(X_axis + 0.2,Train, 0.4, label = 'Train', color=('mediumaquamarine'))

plt.xticks(X_axis, label)
plt.xlabel("ML algorithms")
plt.ylabel("Accuracy")
plt.title("Testing vs Training Accuracy")
plt.legend()
plt.show()

def predict_crop_with_rf(nitrogen, phosphorus, potassium, temperature, humidity, ph, rainfall, model):

    input_data = np.array([[nitrogen, phosphorus, potassium, temperature, humidity, ph, rainfall]])
    prediction = model.predict(input_data)
    return prediction[0]

# Example usage with Random Forest model
crop_prediction_rf = predict_crop_with_rf(
    nitrogen=38,
    phosphorus=58,
    potassium=84,
    temperature=17.87,
    humidity=15.59,
    ph=5.86,
    rainfall=68.58,
    model=RF  # Use the trained Random Forest model
)

print(f"The recommended crop is: {crop_prediction_rf}")

def predict_crop(nitrogen, phosphorus, potassium, temperature, humidity, ph, rainfall, model):

    input_data = np.array([[nitrogen, phosphorus, potassium, temperature, humidity, ph, rainfall]])
    prediction = model.predict(input_data)
    return prediction[0]

# Example usage with KNN model
crop_prediction = predict_crop(
    nitrogen=38,
    phosphorus=58,
    potassium=84,
    temperature=17.87,
    humidity=15.59,
    ph=5.86,
    rainfall=68.58,
    model=knn_1  # Use the trained model (knn_1)
)

print(f"The recommended crop is: {crop_prediction}")

import pickle

# Save the Random Forest model
pickle.dump(RF, open('model.pkl', 'wb'))
print("Model saved successfully.")