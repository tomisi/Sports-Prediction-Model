# -*- coding: utf-8 -*-
"""Sports Prediction.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1uUeCNds_F00vy52ORMzKBh7FCMpX3FJW

TASK 1: Demonstrate the data preparation & feature extraction process
"""

# Import libraries
import pandas as pd
import numpy as np

# Upload dataset
from google.colab import files
uploaded = files.upload()

import io
players_data = pd.read_csv(io.BytesIO(uploaded['players_22.csv']), low_memory= False)

players_data.head()

all_columns = players_data.columns.tolist()
print(all_columns)

# Drop unecessary columns
data = players_data.drop(['potential', 'player_face_url', 'club_logo_url', 'club_flag_url', 'nation_logo_url', 'nation_flag_url', 'real_face', 'nation_jersey_number', 'nation_position', 'nation_team_id', 'nationality_name', 'nationality_id', 'club_contract_valid_until', 'club_joined', 'player_tags', 'player_traits', 'league_name', 'sofifa_id', 'club_loaned_from' , 'club_jersey_number', 'club_position' , 'league_level', 'club_name', 'club_team_id', 'dob', 'player_url', 'short_name', 'long_name'], axis=1)

data.head()

# Calculate percentage of missing values on each column
missing_values_pct = (data.isnull().sum() / len(data)) * 100

missing_values_pct = missing_values_pct.sort_values(ascending=False)
print(missing_values_pct.head(10))

data.info()

# Drop column with highest percentage of null values
data.drop(['goalkeeping_speed'], axis=1, inplace=True)

data.info()

print(data['gk'].head())

print(data['work_rate'].head())

# Split into potential and current 
columns_to_split = ['ls', 'st', 'rs', 'lw', 'lf', 'cf', 'rf', 'rw', 'lam', 'cam', 'ram', 'lm', 'lcm', 'cm', 'rcm', 'rm', 'lwb', 'ldm', 'cdm', 'rdm', 'rwb', 'lb', 'lcb', 'cb', 'rcb', 'rb', 'gk']

for col in columns_to_split:
    data[col] = data[col].str.replace('-', '+-')
    data[[f'{col}_current', f'{col}_potential']] = data[col].str.split('+', expand=True)
    data[f'{col}_current'] = pd.to_numeric(data[f'{col}_current'])
    data[f'{col}_potential'] = pd.to_numeric(data[f'{col}_potential']) + data[f'{col}_current']
    
data.drop(columns_to_split, axis=1, inplace=True)

# Drop potential columns
data.drop(data.filter(regex='_potential$').columns, axis=1, inplace=True)

data

object_cols = data.select_dtypes(include=['object']).columns
print(object_cols)

# Drop NaN values
data.dropna(how="all")

# Pipeline to scale the data and imput missing values
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer

cols_to_scale = [col for col in data.columns if data[col].dtype != 'object']

pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('imputer', IterativeImputer(max_iter=100, random_state=0)),
])

data[cols_to_scale] = pipeline.fit_transform(data[cols_to_scale])

print(data.head())

data['work_rate'].head()

# Handle categorical features
object_cols = data.select_dtypes(include='object').columns
data[object_cols] = data[object_cols].fillna(method='ffill', limit=3)
data[object_cols] = data[object_cols].fillna(method='bfill', limit=3)

# Check for null values
data.isnull().sum()

# Encoding
data['preferred_foot'] = data['preferred_foot'].apply(lambda x: 0 if x == 'Left' else 1)

work_rate_encoding = pd.get_dummies(data['work_rate'], prefix='work_rate')
data = pd.concat([data, work_rate_encoding], axis=1)
data.drop('work_rate', axis=1, inplace=True)

from sklearn.preprocessing import LabelEncoder

label_encoder = LabelEncoder()
data['player_positions'] = label_encoder.fit_transform(data['player_positions'])
data['body_type'] = label_encoder.fit_transform(data['body_type'])

print(data['player_positions'].unique())
print(data['body_type'].unique())

data.info()

# Feature extraction using Principal Component Analysis
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestRegressor

X = data.drop(['overall'], axis=1)
y = data[['overall']]

pca = PCA(n_components=10)
X_pca = pca.fit_transform(X)

rf_model = RandomForestRegressor(random_state=42)
rf_model.fit(X_pca, y.to_numpy().ravel())

importance_scores = rf_model.feature_importances_
k = 10
important_features_indices = importance_scores.argsort()[::-1][:k]
important_features_names = X.columns[important_features_indices]
print(important_features_names)

"""TASK 2: Create  feature subsets which show maximum correlation with the dependent variable. """

# Checking features that show maximum correlation to target feature
corr_coeffs = data.corr()['overall'].abs().sort_values(ascending=False)
top_features = corr_coeffs[1:11].index.tolist()

final_feature_names = set(important_features_names) & set(top_features)
feature_subset = data[final_feature_names]
print(feature_subset)

"""TASK 3: Create and train a suitable machine learning model that can predict a player rating."""

# Training
X = feature_subset
y = data['overall']

from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

from sklearn.ensemble import RandomForestRegressor
rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
rf_model.fit(X_train, y_train)

"""TASK4: Measure the performance of the model and fine tune it as a process of optimization."""

y_pred = rf_model.predict(X_test)

# MSE Performance of the model
from sklearn.metrics import mean_squared_error, r2_score
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print(f"Mean squared error: {mse:.2f}")
print(f"R-squared: {r2:.2f}")

# Optimization of the model
X = feature_subset
y = data['overall']

from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
X = scaler.fit_transform(X)

from sklearn.model_selection import cross_val_score
from sklearn.metrics import mean_squared_error
rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
scores = -1 * cross_val_score(rf_model, X, y, cv=5, scoring='neg_mean_squared_error')
print("Cross-validation MSE scores:", scores)
print("Average MSE:", scores.mean())

from sklearn.model_selection import GridSearchCV
param_grid = {
    'n_estimators': [50, 100, 200],
    'max_depth': [None, 5, 10]
}
grid_search = GridSearchCV(rf_model, param_grid=param_grid, cv=5, scoring='neg_mean_squared_error')
grid_search.fit(X, y)
print("Best parameters:", grid_search.best_params_)
print("Best MSE:", -1 * grid_search.best_score_)

"""TASK 5: Use the data from another season which was not used during the training to test how good the model is. """

def preproccess(data):
  from sklearn.pipeline import Pipeline
  from sklearn.preprocessing import StandardScaler
  from sklearn.experimental import enable_iterative_imputer
  from sklearn.impute import IterativeImputer
  from sklearn.preprocessing import LabelEncoder
  from sklearn.decomposition import PCA
  from sklearn.ensemble import RandomForestRegressor

  data = players_data.drop(['potential', 'player_face_url', 'club_logo_url', 'club_flag_url', 'nation_logo_url', 'nation_flag_url', 'real_face', 'nation_jersey_number', 'nation_position', 'nation_team_id', 'nationality_name', 'nationality_id', 'club_contract_valid_until', 'club_joined', 'player_tags', 'player_traits', 'league_name', 'sofifa_id', 'club_loaned_from' , 'club_jersey_number', 'club_position' , 'league_level', 'club_name', 'club_team_id', 'dob', 'player_url', 'short_name', 'long_name'], axis=1)
  missing_values_pct = (data.isnull().sum() / len(data)) * 100
  highest_null_percentage_col = missing_values_pct.idxmax()
  data.drop(highest_null_percentage_col, axis=1, inplace=True)
  
  columns_to_split = ['ls', 'st', 'rs', 'lw', 'lf', 'cf', 'rf', 'rw', 'lam', 'cam', 'ram', 'lm', 'lcm', 'cm', 'rcm', 'rm', 'lwb', 'ldm', 'cdm', 'rdm', 'rwb', 'lb', 'lcb', 'cb', 'rcb', 'rb', 'gk']
  for col in columns_to_split:
    data[col] = data[col].str.replace('-', '+-')
    data[[f'{col}_current', f'{col}_potential']] = data[col].str.split('+', expand=True)
    data[f'{col}_current'] = pd.to_numeric(data[f'{col}_current'])
    data[f'{col}_potential'] = pd.to_numeric(data[f'{col}_potential']) + data[f'{col}_current']  
  data.drop(columns_to_split, axis=1, inplace=True)
  
  data.drop(data.filter(regex='_potential$').columns, axis=1, inplace=True)
  data.dropna(how="all")

  cols_to_scale = [col for col in data.columns if data[col].dtype != 'object']

  pipeline = Pipeline([
      ('scaler', StandardScaler()),
      ('imputer', IterativeImputer(max_iter=100, random_state=0)),
  ])

  data[cols_to_scale] = pipeline.fit_transform(data[cols_to_scale])

  object_cols = data.select_dtypes(include='object').columns
  data[object_cols] = data[object_cols].fillna(method='ffill', limit=3)
  data[object_cols] = data[object_cols].fillna(method='bfill', limit=3)

  data['preferred_foot'] = data['preferred_foot'].apply(lambda x: 0 if x == 'Left' else 1)
  work_rate_encoding = pd.get_dummies(data['work_rate'], prefix='work_rate')
  data = pd.concat([data, work_rate_encoding], axis=1)
  data.drop('work_rate', axis=1, inplace=True)

  label_encoder = LabelEncoder()
  data['player_positions'] = label_encoder.fit_transform(data['player_positions'])
  data['body_type'] = label_encoder.fit_transform(data['body_type'])

  X = data.drop(['overall'], axis=1)
  y = data[['overall']]
  pca = PCA(n_components=10)
  X_pca = pca.fit_transform(X)
  rf_model = RandomForestRegressor(random_state=42)
  rf_model.fit(X_pca, y.to_numpy().ravel())
  importance_scores = rf_model.feature_importances_
  k = 10
  important_features_indices = importance_scores.argsort()[::-1][:k]
  important_features_names = X.columns[important_features_indices]
  corr_coeffs = data.corr()['overall'].abs().sort_values(ascending=False)
  top_features = corr_coeffs[1:11].index.tolist()
  final_feature_names = set(important_features_names) & set(top_features)
  feature_subset = data[final_feature_names]

  return data

new_upload = files.upload()

import io
new_players_data = pd.read_csv(io.BytesIO(new_upload['players_21.csv']), low_memory= False)

new_data = preproccess(new_players_data)

X = new_data[final_feature_names]
y = new_data['overall']

from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

from sklearn.ensemble import RandomForestRegressor
best_params = grid_search.best_params_
rf_model = RandomForestRegressor(n_estimators=best_params['n_estimators'], 
                                  max_depth=best_params['max_depth'], 
                                  random_state=42)
rf_model.fit(X_train, y_train)

mse = ((rf_model.predict(X_test) - y_test) ** 2).mean()
print(f"Mean squared error on the testing set: {mse:.2f}")

X_new = new_data[final_feature_names]
y_new = new_data['overall']

best_params = grid_search.best_params_
rf_model = RandomForestRegressor(n_estimators=best_params['n_estimators'], 
                                  max_depth=best_params['max_depth'], 
                                  random_state=42)

rf_model.fit(X_train, y_train)
y_pred = rf_model.predict(X_new)

mse = mean_squared_error(y_new, y_pred)
print('Mean squared error:', mse)