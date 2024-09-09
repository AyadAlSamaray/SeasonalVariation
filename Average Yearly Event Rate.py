#!/usr/bin/env python
# coding: utf-8
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.dates as mdates
from sapphire.time_util import GPSTime

# Function to get average daily surface pressure
def get_surface_pressure(filename, start, end):
    weather_df = pd.read_csv(filename, delimiter='\t', comment='#', header=None,
                             names=['date', 'time', 'timestamp', 'temperature_inside', 'temperature_outside', 
                                    'humidity_inside', 'humidity_outside', 'atmospheric_pressure', 'wind_direction', 
                                    'wind_speed', 'solar_radiation', 'uv_index', 'evapotranspiration', 'rain_rate', 
                                    'heat_index', 'dew_point', 'wind_chill'])
    
    weather_df['datetime'] = pd.to_datetime(weather_df['date'] + ' ' + weather_df['time'])
    weather_df.set_index('datetime', inplace=True)
    weather_df = weather_df[start:end]
    daily_pressure = weather_df['atmospheric_pressure'].resample('D').mean()
    
    return daily_pressure.index.to_pydatetime(), daily_pressure.values

# Function to get event rate
def get_event_rate(filename, start, end):
    timestamp = np.loadtxt(filename, usecols=(2), unpack=True)
    alltime, time, event_rate, event_ratefit = [], [], [], []
    event_count, rate_time = 0, 86400
    rate_interval = start + rate_time
    for x in timestamp:
        if start < x < end: 
            if x < rate_interval and (end - x) > 10:
                event_count += 1
            else:    
                time.append(GPSTime(x).datetime())
                alltime.append(GPSTime(x).datetime().timestamp())
                if event_count == 0:
                    event_rate.append(np.nan)
                    event_ratefit.append(0)
                else: 
                    event_rate.append(event_count / rate_time)
                    event_ratefit.append(event_count / rate_time)
                event_count = 0
                rate_interval += rate_time
    
    return time, event_rate, alltime, event_ratefit

# Function to get corrected event rate
def get_corrected_event_rate(weather_file, event_file, start, end):
    # Load weather data
    weather_df = pd.read_csv(weather_file, delimiter='\t', comment='#', header=None,
                             names=['date', 'time', 'timestamp', 'temperature_inside', 'temperature_outside', 
                                    'humidity_inside', 'humidity_outside', 'atmospheric_pressure', 'wind_direction', 
                                    'wind_speed', 'solar_radiation', 'uv_index', 'evapotranspiration', 'rain_rate', 
                                    'heat_index', 'dew_point', 'wind_chill'])
    weather_df['datetime'] = pd.to_datetime(weather_df['date'] + ' ' + weather_df['time'])
    weather_df.set_index('datetime', inplace=True)
    daily_pressure = weather_df['atmospheric_pressure'].resample('D').mean()

    # Load event data
    events_df = pd.read_csv(event_file, delimiter='\t', comment='#', header=None,
                            names=['date', 'time', 'timestamp', 'nanoseconds', 'pulseheights_1', 'pulseheights_2', 
                                   'pulseheights_3', 'pulseheights_4', 'integral_1', 'integral_2', 'integral_3', 
                                   'integral_4', 'number_of_mips_1', 'number_of_mips_2', 'number_of_mips_3', 
                                   'number_of_mips_4', 'arrival_times_1', 'arrival_times_2', 'arrival_times_3', 
                                   'arrival_times_4', 'trigger_time', 'zenith', 'azimuth'])
    events_df['datetime'] = pd.to_datetime(events_df['timestamp'], unit='s')
    events_df.set_index('datetime', inplace=True)
    events_df = events_df[start:end]
    daily_events = events_df['timestamp'].resample('D').count()
    daily_event_rate = daily_events / (24 * 3600)

    # Combine data
    combined_df = pd.concat([daily_pressure, daily_event_rate], axis=1)
    combined_df.columns = ['Average Daily Surface Pressure (hPa)', 'Average Daily Event Rate (Hz)']
    combined_df.dropna(inplace=True)

    # Calculate log of event rate and differences
    combined_df['Log Event Rate'] = np.log(combined_df['Average Daily Event Rate (Hz)'])
    combined_df['Delta Log Event Rate'] = combined_df['Log Event Rate'].diff()
    combined_df['Delta Pressure'] = combined_df['Average Daily Surface Pressure (hPa)'].diff()
    combined_df.dropna(inplace=True)

    # Calculate beta (slope of the linear fit)
    slope, intercept = np.polyfit(combined_df['Delta Pressure'], combined_df['Delta Log Event Rate'], 1)
    beta = slope

    # Calculate corrected event rate
    corrected_event_rate = np.exp(beta * combined_df['Delta Pressure']) * combined_df['Average Daily Event Rate (Hz)'].shift(1)

    return combined_df.index.to_pydatetime(), corrected_event_rate.values

# File paths
weather_file = "/Users/resmarksupport/Desktop/HiSparc/weather.tsv"
event_file = "/Users/resmarksupport/Desktop/HiSparc/season.tsv"

# Load and process data for the year 2016
start_date = '2016-01-01'
end_date = '2016-12-31'
daily_pressure = load_weather_data(weather_file)
daily_event_rate = load_event_data(event_file, start_date, end_date)

# Combine data
combined_df = pd.concat([daily_pressure, daily_event_rate], axis=1)
combined_df.columns = ['Average Daily Surface Pressure (hPa)', 'Average Daily Event Rate (Hz)']
combined_df.dropna(inplace=True)

# Calculate log of event rate and differences
combined_df['Log Event Rate'] = np.log(combined_df['Average Daily Event Rate (Hz)'])
combined_df['Delta Log Event Rate'] = combined_df['Log Event Rate'].diff()
combined_df['Delta Pressure'] = combined_df['Average Daily Surface Pressure (hPa)'].diff()
combined_df.dropna(inplace=True)

# Calculate beta (slope of the linear fit)
slope, intercept = np.polyfit(combined_df['Delta Pressure'], combined_df['Delta Log Event Rate'], 1)
beta = slope

# Calculate corrected event rate
combined_df['Corrected Event Rate'] = np.exp(beta * combined_df['Delta Pressure']) * combined_df['Average Daily Event Rate (Hz)'].shift(1)

# Calculate average corrected event rate over the year
average_corrected_rate = combined_df['Corrected Event Rate'].mean()

# Calculate (R - <R>) / <R>
combined_df['Average Yearly Rate'] = (combined_df['Average Daily Event Rate (Hz)'] - average_corrected_rate) / average_corrected_rate

# Plotting
plt.figure(figsize=(20, 10))
plt.plot(combined_df.index, combined_df['Average Yearly Rate'], marker='', linestyle='-', color='blue')
plt.title(f'Average Yearly Rate: (R - <R>) / <R>\nβ = {beta:.4f}')
plt.xlabel('Date')
plt.ylabel('Average Yearly Rate')
plt.grid(True)

# Set y-axis limits to focus on the main part of the data
y_mean = combined_df['Average Yearly Rate'].mean()
y_std = combined_df['Average Yearly Rate'].std()
plt.ylim(y_mean - 3*y_std, y_mean + 3*y_std)

plt.show()
