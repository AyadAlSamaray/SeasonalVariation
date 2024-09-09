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

#Date range of interest
start = '2016-01-01'
end = '2016-12-31'
start_gps = GPSTime(2016, 1, 1).gpstimestamp()
end_gps = GPSTime(2016, 12, 31).gpstimestamp()

# File paths
weather_file = "/Users/resmarksupport/Desktop/HiSparc/weather.tsv"
event_file = "/Users/resmarksupport/Desktop/HiSparc/season.tsv"

# Get data
t_pressure, p = get_surface_pressure(weather_file, start, end)
t_event, e_rate, at_event, erfit = get_event_rate(event_file, start_gps, end_gps)
t_corrected, corrected_rate = get_corrected_event_rate(weather_file, event_file, start, end)

# Plotting
fig, ax1 = plt.subplots(figsize=(20, 6))

# Plot surface pressure
color = 'gold'
ax1.set_xlabel('Time [Date]', fontsize=12)
ax1.set_ylabel('Average Daily Surface Pressure (hPa)', color=color, fontsize=12)
ax1.plot(t_pressure, p, color=color, label='Surface Pressure')
ax1.tick_params(axis='y', labelcolor=color)

# Create a second y-axis
ax2 = ax1.twinx()

# Plot event rate (excluding values over 0.4)
color = 'black'
ax2.set_ylabel('Event Rate [Hz]', color=color, fontsize=12)
valid_event_mask = np.array(e_rate) <= 0.4
ax2.plot(np.array(t_event)[valid_event_mask], np.array(e_rate)[valid_event_mask], color=color, label='Event Rate')
ax2.tick_params(axis='y', labelcolor=color)

# Plot corrected event rate (excluding values over 0.4)
color = 'blue'
valid_corrected_mask = corrected_rate <= 0.4
ax2.plot(np.array(t_corrected)[valid_corrected_mask], corrected_rate[valid_corrected_mask], color=color, label='Corrected Event Rate')

# Set title and format
plt.title("Surface Pressure, Event Rate, and Corrected Event Rate for 2016", fontsize=16)
plt.xticks(rotation=45)
fig.tight_layout()

# Add legend
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')

plt.grid(True)
plt.show()
