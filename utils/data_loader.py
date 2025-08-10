import pandas as pd

def load_data(csv_hour_path, csv_minute_path, start_time='08:00:00', end_time='16:00:00'):
    """Load and filter hourly and minute CSV files with timestamps."""
    
    df_hour = pd.read_csv(csv_hour_path, header=None, sep=';', 
                          names=['date', 'time', 'open', 'high', 'low', 'close', 'volume'], skiprows=1)
    df_hour['timestamp'] = pd.to_datetime(df_hour['date'] + ' ' + df_hour['time'], format='%d/%m/%Y %H:%M')
    df_hour = df_hour.set_index('timestamp').between_time(start_time, end_time).reset_index()

    df_min = pd.read_csv(csv_minute_path, header=None, sep=';', 
                         names=['date', 'time', 'open', 'high', 'low', 'close', 'volume'], skiprows=1)
    df_min['timestamp'] = pd.to_datetime(df_min['date'] + ' ' + df_min['time'], format='%d/%m/%Y %H:%M')
    df_min = df_min.set_index('timestamp').between_time(start_time, end_time).reset_index()

    return df_hour, df_min
