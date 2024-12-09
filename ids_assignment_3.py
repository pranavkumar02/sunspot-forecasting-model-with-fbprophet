# -*- coding: utf-8 -*-
"""IDS_Assignment_3.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1frSg8QSakp44-PnFY_mshzxZ839PMA0v
"""

!pip install prophet  #Installing prophet package

import pandas as pd
import numpy as np
from prophet import Prophet
from sklearn.metrics import mean_absolute_error, mean_absolute_percentage_error
from sklearn.metrics import r2_score
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import seaborn as sns

"""**Loading and understanding the data**"""

def dataset(file_path,time_period):
  if time_period=='daily':
    df = pd.read_csv(file_path,sep=';',header=None) #
    df.columns= ["Year", "Month", "Day", "Decimal_date", "Daily_Sunspot_Number",
              "Daily_mean_Std_Deviation", "Observations_Daily", "Indicator"]
  elif time_period=='monthly':
    df = pd.read_csv(file_path,sep=';',header=None)
    df.columns= ["Year", "Month", "Decimal_date", "Monthly_Sunspot_Number",
              "Monthly_mean_Std_Deviation", "Observations_Yearly", "Indicator"]
  elif time_period=='yearly':
    df = pd.read_csv(file_path,delimiter=";", header=None)
    df.columns= ["Year", "Yearly_Sunspot_Number", "Yearly_mean_Std_Deviation",
              "Observations_Yearly", "Indicator"]
  return df

df1=dataset('/content/SN_d_tot_V2.0.csv','daily')

#understanding the data
print(df1.head())
print(df1.info())
print(df1.shape)
print(df1.describe())

df2=dataset('/content/SN_m_tot_V2.0.csv','monthly')

#understanding the data
print(df2.head())
print(df2.info())
print(df2.shape)
print(df2.describe())

df3=dataset('/content/SN_y_tot_V2.0.csv','yearly')

#understanding the data
print(df3.head())
print(df3.info())
print(df3.shape)
print(df3.describe())

print(df1.duplicated().sum())
print(df2.duplicated().sum())
print(df3.duplicated().sum())

print(df1.isnull().sum())
print(df2.isnull().sum())
print(df3.isnull().sum())

"""**Preprocessing and Cleaning the data**"""

def processing_cleaning(df):
  unit_time=None
  if df.shape[1]==8:
    df['ds'] = pd.to_datetime(df[['Year','Month','Day']])
    df = df.rename(columns={'Daily_Sunspot_Number':'y'})
    df=df[['ds','y']]
    df=df[df['y']>=0]#A value of -1 indicates that no number is available for that day (missing value).
    df['y'] = df['y'].replace(0, 1e-5)
    unit_time='days'
  elif df.shape[1]==7:
    df['ds'] = pd.to_datetime(df[['Year','Month']].assign(Day=1))
    df = df.rename(columns={'Monthly_Sunspot_Number':'y'})
    df=df[['ds','y']]
    df=df[df['y']>=0]#A value of -1 indicates that no number is available for that day (missing value).
    df['y'] = df['y'].replace(0, 1e-5)
    unit_time='months'
  elif df.shape[1]==5:
     df['Year']=df['Year'].astype(int)
     df['ds']=pd.to_datetime(df[['Year']].assign(Day=1,month=1))
     df = df.rename(columns={'Yearly_Sunspot_Number':'y'})
     df=df[['ds','y']]
     df=df[df['y']>=0]#A value of -1 indicates that no number is available for that day (missing value).
     df['y'] = df['y'].replace(0, 1e-5)
     unit_time='years'
  return df,unit_time

df1,unit_daily=processing_cleaning(df1)
df2,unit_monthly=processing_cleaning(df2)
df3,unit_yearly=processing_cleaning(df3)

def outlier_detection(df):
# Calculate IQR
 Q1 = df['y'].quantile(0.25)  # First quartile (25th percentile)
 Q3 = df['y'].quantile(0.75)  # Third quartile (75th percentile)
 IQR = Q3 - Q1  # Interquartile Range

 upper_bound = Q3 + 1.5 * IQR
 lower_bound = Q1 - 1.5 * IQR

# Find outliers
 outliers = df[(df['y']<lower_bound)|(df['y']>upper_bound)]
 df['y'] = np.clip(df['y'], lower_bound, upper_bound)
 return df

df1=outlier_detection(df1)

#understanding the data
print(df1.head())
print(df1.info())
print(df1.shape)
print(df1.describe())

#understanding the data
print(df2.head())
print(df2.info())
print(df2.shape)
print(df2.describe())

#understanding the data
print(df3.head())
print(df3.info())
print(df3.shape)
print(df3.describe())

"""**EDA and Modeling for daily sunspot data**"""

plt.figure(figsize=(12, 8))
plt.plot(df1['ds'], df1['y'])
plt.title('Daily Sunspots Over Time')
plt.xlabel('Date')
plt.ylabel('Sunspots')
plt.show()

plt.figure(figsize=(8, 6))
sns.histplot(df1['y'], bins=50, kde=True, color='blue')
plt.title('Distribution of Daily Sunspots')
plt.xlabel('Sunspots')
plt.ylabel('Frequency')
plt.show()

df1['Rolling_Mean'] = df1['y'].rolling(window=365).mean()  # 1-year rolling mean

plt.figure(figsize=(12, 6))
plt.plot(df1['ds'],df1['y'], label='Daily Sunspot Counts', alpha=0.5)
plt.plot(df1['ds'], df1['Rolling_Mean'], label='1-Year Rolling Mean', color='red', linewidth=2)
plt.title('Daily Sunspots with 1-Year Rolling Mean', fontsize=16)
plt.xlabel('Date', fontsize=14)
plt.ylabel('Sunspot Counts', fontsize=14)
plt.grid(True)
plt.legend()
plt.show()

from statsmodels.tsa.seasonal import seasonal_decompose

# Set the datetime column as the index for decomposition
df1.set_index('ds', inplace=True)

result = seasonal_decompose(df1['y'], model='additive', period=365)

# Plot decomposition
result.plot()
plt.suptitle('Seasonal Decomposition of Sunspot Counts', fontsize=16)
plt.show()

# Reset index if needed later
df1.reset_index(inplace=True)

#For Daily dataset
growth='linear'
changepoint_prior_scale=0.01
n_changepoints=50
model= Prophet(growth=growth,changepoint_prior_scale=changepoint_prior_scale,n_changepoints=n_changepoints)
model.add_seasonality(name='yearly', period=365, fourier_order=10)
model.add_seasonality(name='weekly', period=7, fourier_order=3)
forcast_periods = [100,200,365]
if growth == 'logistic':
     df1['cap'] = df1['y'].max() + 10

# Fit the model
model.fit(df1)


for periods in forcast_periods:
# Generate future dates
 print(f"\n-----------Forecasting for {periods} days into the future-----------")
 future = model.make_future_dataframe(periods=periods, freq='D')
 if growth == 'logistic':
   future['cap'] = df1['cap'].max()

 # Make predictions
 forecast = model.predict(future)

 # Print the last few forecasted values
 print(f"\n\n\nForecasted values for the last few days of {periods} days:")
 print(forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail())

 # Plot the forecast
 plt.figure(figsize=(12, 6))
 plt.plot(df1['ds'],df1['y'], label='Actual',color='black')
 plt.plot(forecast['ds'], forecast['yhat'], label='Forecast', linestyle='dashed',color='red')
 plt.fill_between(forecast['ds'], forecast['yhat_lower'], forecast['yhat_upper'], color='green', alpha=0.2, label='Confidence Interval')
 plt.title(f"Sunspot Forecast ({periods} {unit_daily}(s)")
 plt.xlabel('Date')
 plt.ylabel('Sunspots')
 plt.legend()
 plt.show()


#Evalution matrix
actual = df1['y']
predicted = forecast['yhat'][:len(df1)]

# Plot the components (trend, yearly seasonality, weekly seasonality, etc.)
model.plot_components(forecast)
plt.show()

def evaluation_matrix(actual,predicted):
  mae = mean_absolute_error(actual, predicted)
  mape = mean_absolute_percentage_error(actual, predicted)
  r2 = r2_score(actual, predicted)
  evalution_matrix=pd.DataFrame({'MAE':[mae],'MAPE':[mape],'R2':[r2]})
  return evalution_matrix

evalution_matrix=evaluation_matrix(actual,predicted)
print(evalution_matrix)

"""**EDA and Modeling for monthly sunspot data**"""

plt.figure(figsize=(12, 8))
plt.plot(df2['ds'], df2['y'])
plt.title('Monthly Sunspots Over Time')
plt.xlabel('Date')
plt.ylabel('Sunspots')
plt.show()

plt.figure(figsize=(8, 6))
sns.histplot(df2['y'], bins=50, kde=True, color='blue')
plt.title('Distribution of Monthly Sunspots')
plt.xlabel('Sunspots')
plt.ylabel('Frequency')
plt.show()

df2['Rolling_Mean'] = df2['y'].rolling(window=365).mean()  # 12-Month rolling mean

plt.figure(figsize=(12, 6))
plt.plot(df2['ds'],df2['y'], label='Montly Sunspot Counts', alpha=0.5)
plt.plot(df2['ds'], df2['Rolling_Mean'], label='12-Month Rolling Mean', color='red', linewidth=2)
plt.title('Monthly Sunspots with 12-Month Rolling Mean', fontsize=16)
plt.xlabel('Date', fontsize=14)
plt.ylabel('Sunspot Counts', fontsize=14)
plt.grid(True)
plt.legend()
plt.show()

# Decompose the time series
decomposition = seasonal_decompose(df2['y'], model='additive', period=12)

# Plot the components
decomposition.plot()
plt.show()

#for Monthly dataset
growth='linear'
changepoint_prior_scale=0.1
n_changepoints=10
fourier_orders =5

model= Prophet(growth=growth, changepoint_prior_scale=changepoint_prior_scale, n_changepoints=n_changepoints)
model.add_seasonality(name='monthly', period=12, fourier_order=fourier_orders)

forecast_periods = [1,6,9]  # Define multiple periods for prediction
if growth == 'logistic':
     df2['cap'] = df2['y'].max() + 10
# Fit the model
model.fit(df2)
# Forecast for each period
for periods in forecast_periods:
    print(f"\n-----------Forecasting for {periods} days into the future-----------")

    # Generate future dates
    future = model.make_future_dataframe(periods=periods, freq='M')
    if growth == 'logistic':
        future['cap'] = df2['cap'].max()

    # Make predictions
    forecast = model.predict(future)

    # Print the last few forecasted values
    print(f"\n\n\nForecasted values for the last few days of {periods} months:")
    print(forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail())

    # Plot the forecast
    plt.figure(figsize=(12, 6))
    plt.plot(df2['ds'],df2['y'], label='Actual',color='black')
    plt.plot(forecast['ds'], forecast['yhat'], label='Forecast', linestyle='dashed',color='red')
    plt.fill_between(forecast['ds'], forecast['yhat_lower'], forecast['yhat_upper'], color='green', alpha=0.2, label='Confidence Interval')
    plt.title(f"Sunspot Forecast ({periods} {unit_monthly}(s)")
    plt.xlabel('Date')
    plt.ylabel('Sunspots')
    plt.legend()
    plt.show()

#Evalution matrix
actual = df2['y']
predicted = forecast['yhat'][:len(df2)]

# Plot the components (trend, yearly seasonality, weekly seasonality, etc.)
model.plot_components(forecast)
plt.show()

evalution_matrix=evaluation_matrix(actual,predicted)
print(evalution_matrix)

#for Monthly dataset
growth='logistic'
changepoint_prior_scale=0.1
n_changepoints=10
fourier_orders =5

model= Prophet(growth=growth, changepoint_prior_scale=changepoint_prior_scale, n_changepoints=n_changepoints)
model.add_seasonality(name='monthly', period=30, fourier_order=fourier_orders)

forecast_periods = [1,6,9]  # Define multiple periods for prediction
if growth == 'logistic':
     df2['cap'] = df2['y'].max() + 10
# Fit the model
model.fit(df2)
# Forecast for each period
for periods in forecast_periods:
    print(f"\n-----------Forecasting for {periods} days into the future-----------")

    # Generate future dates
    future = model.make_future_dataframe(periods=periods, freq='M')
    if growth == 'logistic':
        future['cap'] = df2['cap'].max()

    # Make predictions
    forecast = model.predict(future)

    # Print the last few forecasted values
    print(f"\n\n\nForecasted values for the last few days of {periods} months:")
    print(forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail())

    # Plot the forecast
    plt.figure(figsize=(12, 6))
    plt.plot(df2['ds'],df2['y'], label='Actual',color='black')
    plt.plot(forecast['ds'], forecast['yhat'], label='Forecast', linestyle='dashed',color='red')
    plt.fill_between(forecast['ds'], forecast['yhat_lower'], forecast['yhat_upper'], color='green', alpha=0.2, label='Confidence Interval')
    plt.title(f"Sunspot Forecast ({periods} {unit_monthly}(s)")
    plt.xlabel('Date')
    plt.ylabel('Sunspots')
    plt.legend()
    plt.show()

#Evalution matrix
actual = df2['y']
predicted = forecast['yhat'][:len(df2)]

# Plot the components (trend, yearly seasonality, weekly seasonality, etc.)
model.plot_components(forecast)
plt.show()

evalution_matrix=evaluation_matrix(actual,predicted)
print(evalution_matrix)

"""**EDA and Modeling of yearly data**"""

plt.figure(figsize=(12, 8))
plt.plot(df3['ds'], df3['y'])
plt.title('Yearly Sunspots Over Time')
plt.xlabel('Date')
plt.ylabel('Sunspots')
plt.show()

plt.figure(figsize=(8, 6))
sns.histplot(df3['y'], bins=50, kde=True, color='blue')
plt.title('Distribution of Yearly Sunspots')
plt.xlabel('Sunspots')
plt.ylabel('Frequency')

df3 = df3.drop(df3.index[0:111])

# Reset the index to ensure it starts from 0 again
df3.reset_index(drop=True, inplace=True)

df3.head()

#for Yearly dataset
growth='linear'
changepoint_prior_scale=0.1
n_changepoints=5
fourier_orders =3

model= Prophet(growth=growth, changepoint_prior_scale=changepoint_prior_scale, n_changepoints=n_changepoints)
model.add_seasonality(name='yearly', period=11, fourier_order=fourier_orders)

forecast_periods =[1,10,20] # Define multiple periods for prediction

# Fit the model
model.fit(df3)
# Forecast for each period
for periods in forecast_periods:
    print(f"\n-----------Forecasting for {periods} days into the future-----------")

    # Generate future dates
    future = model.make_future_dataframe(periods=periods, freq='Y')
    if growth == 'logistic':
        future['cap'] = df3['cap'].max()

    # Make predictions
    forecast = model.predict(future)

    # Print the last few forecasted values
    print(f"\n\n\nForecasted values for the last few days of {periods} Years:")
    print(forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail())

    # Plot the forecast
    plt.figure(figsize=(12, 6))
    plt.plot(df3['ds'],df3['y'], label='Actual',color='black')
    plt.plot(forecast['ds'], forecast['yhat'], label='Forecast', linestyle='dashed',color='red')
    plt.fill_between(forecast['ds'], forecast['yhat_lower'], forecast['yhat_upper'], color='green', alpha=0.2, label='Confidence Interval')
    plt.title(f"Sunspot Forecast ({periods} {unit_yearly}(s)")
    plt.xlabel('Date')
    plt.ylabel('Sunspots')
    plt.legend()
    plt.show()

#Evalution matrix
actual = df3['y']
predicted = forecast['yhat'][:len(df3)]

# Plot the components (trend, yearly seasonality, weekly seasonality, etc.)
model.plot_components(forecast)
plt.show()

evalution_matrix=evaluation_matrix(actual,predicted)
print(evalution_matrix)

#for Yearly dataset
growth='flat'
changepoint_prior_scale=0.1
n_changepoints=5
fourier_orders =3

model= Prophet(growth=growth, changepoint_prior_scale=changepoint_prior_scale, n_changepoints=n_changepoints)
model.add_seasonality(name='yearly', period=11, fourier_order=fourier_orders)

forecast_periods =[1,10,20] # Define multiple periods for prediction
# Fit the model
model.fit(df3)
# Forecast for each period
for periods in forecast_periods:
    print(f"\n-----------Forecasting for {periods} days into the future-----------")

    # Generate future dates
    future = model.make_future_dataframe(periods=periods, freq='Y')
    if growth == 'logistic':
        future['cap'] = df3['cap'].max()

    # Make predictions
    forecast = model.predict(future)

    # Print the last few forecasted values
    print(f"\n\n\nForecasted values for the last few days of {periods} Years:")
    print(forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail())

    # Plot the forecast
    plt.figure(figsize=(12, 6))
    plt.plot(df3['ds'],df3['y'], label='Actual',color='black')
    plt.plot(forecast['ds'], forecast['yhat'], label='Forecast', linestyle='dashed',color='red')
    plt.fill_between(forecast['ds'], forecast['yhat_lower'], forecast['yhat_upper'], color='green', alpha=0.2, label='Confidence Interval')
    plt.title(f"Sunspot Forecast ({periods} {unit_yearly}(s)")
    plt.xlabel('Date')
    plt.ylabel('Sunspots')
    plt.legend()
    plt.show()

#Evalution matrix
actual = df3['y']
predicted = forecast['yhat'][:len(df3)]

# Plot the components (trend, yearly seasonality, weekly seasonality, etc.)
model.plot_components(forecast)
plt.show()

evalution_matrix=evaluation_matrix(actual,predicted)
print(evalution_matrix)