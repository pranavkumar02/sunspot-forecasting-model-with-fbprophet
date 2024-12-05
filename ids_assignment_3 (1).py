# -*- coding: utf-8 -*-
"""IDS_Assignment_3.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1frSg8QSakp44-PnFY_mshzxZ839PMA0v
"""

!pip install prophet  #Installing prophet package

import pandas as pd
from prophet import Prophet
from sklearn.metrics import mean_absolute_error, mean_absolute_percentage_error
from sklearn.metrics import r2_score
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt

df1 = pd.read_csv('/content/SN_d_tot_V2.0.csv',sep=';',header=None) # we are using ; as delimiter and assigning
 # numerical values as column names

df1.columns= ["Year", "Month", "Day", "Decimal_date", "Daily_Sunspot_Number",
              "Daily_mean_Std_Deviation", "Observations_Daily", "Indicator"]

#understanding the data
print(df1.head())
print(df1.info())
print(df1.shape)

df2=pd.read_csv('/content/SN_m_tot_V2.0.csv',sep=';',header=None)

df2.columns= ["Year", "Month", "Decimal_date", "Monthly_Sunspot_Number",
              "Monthly_mean_Std_Deviation", "Observations_Yearly", "Indicator"]

#understanding the data
print(df2.head())
print(df2.info())
print(df2.shape)

# Load the yearly dataset
df3 = pd.read_csv("SN_y_tot_V2.0.csv", delimiter=";", header=None)

df3.columns= ["Year", "Yearly_Sunspot_Number", "Yearly_mean_Std_Deviation",
              "Observations_Yearly", "Indicator"]

#understanding the data
print(df3.head())
print(df3.info())
print(df3.shape)

print(df1.duplicated().sum())
print(df2.duplicated().sum())
print(df3.duplicated().sum())

print(df1.isnull().sum())
print(df2.isnull().sum())
print(df3.isnull().sum())

"""**Preprocessing  and cleaning the Data**"""

df3['Year']=df3['Year'].astype(int)

df1['ds'] = pd.to_datetime(df1[['Year', 'Month', 'Day']])
unit_daily = 'Daily'
df1 = df1.rename(columns={'Daily_Sunspot_Number':'y'})
df1=df1[['ds','y']]
df1=df1[df1['y']>=0]   #Removing rows with 'y' column -1 value as it represents missing value
print(df1.head())

df2['ds'] = pd.to_datetime(df2[['Year', 'Month']].assign(Day=1))
unit_monthly = 'Monthly'
df2 = df2.rename(columns={'Monthly_Sunspot_Number':'y'})
df2=df2[['ds','y']]
df2=df2[df2['y']>=0] #Removing rows with 'y' column -1 value as it represents missing value
print(df2.head())

df2.info()

df3['ds']=pd.to_datetime(df3[['Year']].assign(Day=1,month=1))
unit_yearly = 'Yearly'
df3 = df3.rename(columns={'Yearly_Sunspot_Number':'y'})
df3=df3[['ds','y']]
df3=df3[df3['y']>=0] #Removing rows with 'y' column -1 value as it represents missing value
df3.drop(index=range(0,110),inplace=True)# removing data from 1700 to 1809
print(df3.head())

df3.info()

#For Daily dataset
growth='linear'
seasonality=None
changepoint_prior_scale=0.05
n_changepoints=25
model= Prophet(growth=growth, changepoint_prior_scale=changepoint_prior_scale, n_changepoints=n_changepoints)

forecast_periods = [100, 200, 365]  # Define multiple periods for prediction
if growth == 'logistic':
     df1['cap'] = df1['y'].max() + 10

# Fit the model
model.fit(df1)
# Forecast for each period
for periods in forecast_periods:
    print(f"\n-----------Forecasting for {periods} days into the future-----------")

    # Generate future dates
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
    plt.plot(df1['ds'],df1['y'], label='Actual',color='blue')
    plt.plot(forecast['ds'], forecast['yhat'], label='Forecast', linestyle='dashed',color='red')
    plt.fill_between(forecast['ds'], forecast['yhat_lower'], forecast['yhat_upper'], color='yellow', alpha=0.2, label='Confidence Interval')
    plt.title(f"Sunspot Forecast ({periods} {unit_daily}(s)")
    plt.xlabel('Date')
    plt.ylabel('Sunspots')
    plt.legend()
    plt.show()

    #Evalution matrix
    actual = df1['y']
    predicted = forecast['yhat'][:len(df1)]
    mae = mean_absolute_error(actual, predicted)
    mape = mean_absolute_percentage_error(actual, predicted)
    r2 = r2_score(actual, predicted)
    evalution_matrix=pd.DataFrame({'MAE':[mae],'MAPE':[mape],'R2':[r2]})
    print(f"Evaluation Metrics for {unit_daily} dataset:")
    print(evalution_matrix)
    print("\n\n\n")

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
    plt.plot(df2['ds'],df2['y'], label='Actual',color='blue')
    plt.plot(forecast['ds'], forecast['yhat'], label='Forecast', linestyle='dashed',color='red')
    plt.fill_between(forecast['ds'], forecast['yhat_lower'], forecast['yhat_upper'], color='yellow', alpha=0.2, label='Confidence Interval')
    plt.title(f"Sunspot Forecast ({periods} {unit_monthly}(s)")
    plt.xlabel('Date')
    plt.ylabel('Sunspots')
    plt.legend()
    plt.show()

    #Evalution matrix
    actual = df2['y']
    predicted = forecast['yhat'][:len(df2)]
    mae = mean_absolute_error(actual, predicted)
    mape = mean_absolute_percentage_error(actual, predicted)
    r2 = r2_score(actual, predicted)
    evalution_matrix=pd.DataFrame({'MAE':[mae],'MAPE':[mape],'R2':[r2]})
    print(f"Evaluation Metrics for {unit_monthly} dataset:")
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
    plt.plot(df2['ds'],df2['y'], label='Actual',color='blue')
    plt.plot(forecast['ds'], forecast['yhat'], label='Forecast', linestyle='dashed',color='red')
    plt.fill_between(forecast['ds'], forecast['yhat_lower'], forecast['yhat_upper'], color='yellow', alpha=0.2, label='Confidence Interval')
    plt.title(f"Sunspot Forecast ({periods} {unit_monthly}(s)")
    plt.xlabel('Date')
    plt.ylabel('Sunspots')
    plt.legend()
    plt.show()

    #Evalution matrix
    actual = df2['y']
    predicted = forecast['yhat'][:len(df2)]
    mae = mean_absolute_error(actual, predicted)
    mape = mean_absolute_percentage_error(actual, predicted)
    r2 = r2_score(actual, predicted)
    evalution_matrix=pd.DataFrame({'MAE':[mae],'MAPE':[mape],'R2':[r2]})
    print(f"Evaluation Metrics for {unit_monthly} dataset:")
    print(evalution_matrix)

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
    plt.plot(df3['ds'],df3['y'], label='Actual',color='blue')
    plt.plot(forecast['ds'], forecast['yhat'], label='Forecast', linestyle='dashed',color='red')
    plt.fill_between(forecast['ds'], forecast['yhat_lower'], forecast['yhat_upper'], color='yellow', alpha=0.2, label='Confidence Interval')
    plt.title(f"Sunspot Forecast ({periods} {unit_yearly}(s)")
    plt.xlabel('Date')
    plt.ylabel('Sunspots')
    plt.legend()
    plt.show()

    #Evalution matrix
    actual = df3['y']
    predicted = forecast['yhat'][:len(df3)]
    mae = mean_absolute_error(actual, predicted)
    mape = mean_absolute_percentage_error(actual, predicted)
    r2 = r2_score(actual, predicted)
    evalution_matrix=pd.DataFrame({'MAE':[mae],'MAPE':[mape],'R2':[r2]})
    print(f"Evaluation Metrics for {unit_yearly} dataset:")
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
    plt.plot(df3['ds'],df3['y'], label='Actual',color='blue')
    plt.plot(forecast['ds'], forecast['yhat'], label='Forecast', linestyle='dashed',color='red')
    plt.fill_between(forecast['ds'], forecast['yhat_lower'], forecast['yhat_upper'], color='yellow', alpha=0.2, label='Confidence Interval')
    plt.title(f"Sunspot Forecast ({periods} {unit_yearly}(s)")
    plt.xlabel('Date')
    plt.ylabel('Sunspots')
    plt.legend()
    plt.show()

    #Evalution matrix
    actual = df3['y']
    predicted = forecast['yhat'][:len(df3)]
    mae = mean_absolute_error(actual, predicted)
    mape = mean_absolute_percentage_error(actual, predicted)
    r2 = r2_score(actual, predicted)
    evalution_matrix=pd.DataFrame({'MAE':[mae],'MAPE':[mape],'R2':[r2]})
    print(f"Evaluation Metrics for {unit_yearly} dataset:")
    print(evalution_matrix)