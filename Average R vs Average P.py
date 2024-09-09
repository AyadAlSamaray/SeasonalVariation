import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Function to load and process weather data
def load_weather_data(filepath):
    weather_df = pd.read_csv(filepath, delimiter='\t', comment='#', header=None,
                             names=['date', 'time', 'timestamp', 'temperature_inside', 'temperature_outside', 
                                    'humidity_inside', 'humidity_outside', 'atmospheric_pressure', 'wind_direction', 
                                    'wind_speed', 'solar_radiation', 'uv_index', 'evapotranspiration', 'rain_rate', 
                                    'heat_index', 'dew_point', 'wind_chill'])
    
    weather_df['datetime'] = pd.to_datetime(weather_df['date'] + ' ' + weather_df['time'])
    weather_df.set_index('datetime', inplace=True)
    
    # Calculate daily average surface pressure
    daily_pressure = weather_df['atmospheric_pressure'].resample('D').mean()
    
    return daily_pressure

# Function to load and process event data
def load_event_data(filepath, start, end):
    events_df = pd.read_csv(filepath, delimiter='\t', comment='#', header=None,
                            names=['date', 'time', 'timestamp', 'nanoseconds', 'pulseheights_1', 'pulseheights_2', 
                                   'pulseheights_3', 'pulseheights_4', 'integral_1', 'integral_2', 'integral_3', 
                                   'integral_4', 'number_of_mips_1', 'number_of_mips_2', 'number_of_mips_3', 
                                   'number_of_mips_4', 'arrival_times_1', 'arrival_times_2', 'arrival_times_3', 
                                   'arrival_times_4', 'trigger_time', 'zenith', 'azimuth'])
    
    events_df['datetime'] = pd.to_datetime(events_df['timestamp'], unit='s')
    events_df.set_index('datetime', inplace=True)
    
    # Filter data within the date range
    events_df = events_df[start:end]
    
    # Calculate daily event count
    daily_events = events_df['timestamp'].resample('D').count()
    
    # Calculate daily event rate (events per second)
    daily_event_rate = daily_events / (24 * 3600)
    
    return daily_event_rate

# File paths
weather_file = "/Users/resmarksupport/Desktop/HiSparc/weather.tsv"
event_file = "/Users/resmarksupport/Desktop/HiSparc/season.tsv"

# Load and process data
daily_pressure = load_weather_data(weather_file)
daily_event_rate = load_event_data(event_file, '2016-01-01', '2016-12-31')

# Combine data
combined_df = pd.concat([daily_pressure, daily_event_rate], axis=1)
combined_df.columns = ['Average Daily Surface Pressure (hPa)', 'Average Daily Event Rate (Hz)']

# Drop rows with missing values
combined_df.dropna(inplace=True)

# Calculate log of event rate
combined_df['Log Event Rate'] = np.log(combined_df['Average Daily Event Rate (Hz)'])

# Calculate differences
combined_df['Delta Log Event Rate'] = combined_df['Log Event Rate'].diff()
combined_df['Delta Pressure'] = combined_df['Average Daily Surface Pressure (hPa)'].diff()

# Drop the first row with NaN values
combined_df.dropna(inplace=True)

# Plotting
plt.figure(figsize=(10, 6))
plt.scatter(combined_df['Delta Pressure'], combined_df['Delta Log Event Rate'], color='blue')
plt.plot(np.unique(combined_df['Delta Pressure']), 
         np.poly1d(np.polyfit(combined_df['Delta Pressure'], combined_df['Delta Log Event Rate'], 1))
         (np.unique(combined_df['Delta Pressure'])), color='red', linestyle='--')

plt.title('Change in Log Event Rate vs. Change in Surface Pressure (2016)')
plt.xlabel('Change in Surface Pressure (hPa)')
plt.ylabel('Change in Log Event Rate')
plt.grid(True)
plt.show()
