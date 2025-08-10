from tqdm import tqdm
from strategies.strategy import detect_sweep_and_trade

def run_backtest(df_hour, df_min, min_tick_distance):
    results = []
    print("🚀 Starting backtest...")
    
    for i in tqdm(range(1, len(df_hour))):
        prev_row = df_hour.iloc[i-1]
        curr_row = df_hour.iloc[i]

        hour_start = curr_row['timestamp'].replace(minute=0, second=0, microsecond=0)
        hour_end = hour_start + pd.Timedelta(hours=1)
        
        df_hour_minute = df_min[(df_min['timestamp'] >= hour_start) & (df_min['timestamp'] < hour_end)]
        
        trade_result = detect_sweep_and_trade(prev_row, curr_row, df_hour_minute, min_tick_distance)
        if trade_result:
            trade_result['hour'] = hour_start
            results.append(trade_result)

    return results
