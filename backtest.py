import pandas as pd
from tqdm import tqdm

# Paths to data files
csv_hour = 'data/nq-1h_bk.csv'
csv_minute = 'data/nq-1m_bk.csv'

tick_size = 0.25
min_tick_distance = tick_size * 10  # 10 ticks = 2.5 points

def run_backtest():
    print("🔄 Loading datasets...")
    try:
        # Load hourly data
        df_hour = pd.read_csv(csv_hour, header=None, sep=';', 
                              names=['date', 'time', 'open', 'high', 'low', 'close', 'volume'], skiprows=1)
        df_hour['timestamp'] = pd.to_datetime(df_hour['date'] + ' ' + df_hour['time'], format='%d/%m/%Y %H:%M')
        df_hour = df_hour.set_index('timestamp').between_time('08:00:00', '16:00:00').reset_index()
        print(f"✅ Hourly rows after filter: {len(df_hour)}")

        # Load minute data
        df_min = pd.read_csv(csv_minute, header=None, sep=';', 
                             names=['date', 'time', 'open', 'high', 'low', 'close', 'volume'], skiprows=1)
        df_min['timestamp'] = pd.to_datetime(df_min['date'] + ' ' + df_min['time'], format='%d/%m/%Y %H:%M')
        df_min = df_min.set_index('timestamp').between_time('08:00:00', '16:00:00').reset_index()
        print(f"✅ Minute rows after filter: {len(df_min)}")

        results = []
        print("🚀 Starting backtest...")

        for i in tqdm(range(1, len(df_hour))):
            prev_row = df_hour.iloc[i-1]
            curr_row = df_hour.iloc[i]

            # Check if current open is inside previous candle body
            if not (prev_row['low'] < curr_row['open'] < prev_row['high']):
                continue

            hour_start = curr_row['timestamp'].replace(minute=0, second=0, microsecond=0)
            hour_end = hour_start + pd.Timedelta(hours=1)

            df_hour_minute = df_min[(df_min['timestamp'] >= hour_start) & (df_min['timestamp'] < hour_end)]
            df_first_20 = df_hour_minute[df_hour_minute['timestamp'].dt.minute < 20]

            sweep_type = None
            sweep_min_row = None
            entry_price = None
            tp = None
            sl = None

            for _, mrow in df_first_20.iterrows():
                if mrow['high'] > prev_row['high']:
                    if abs(prev_row['high'] - prev_row['close']) < min_tick_distance:
                        continue
                    sweep_type = 'high'
                    entry_price = mrow['close']
                    tp = prev_row['close']
                    sl = entry_price + abs(entry_price - tp)
                    sweep_min_row = mrow
                    break
                elif mrow['low'] < prev_row['low']:
                    if abs(prev_row['close'] - prev_row['low']) < min_tick_distance:
                        continue
                    sweep_type = 'low'
                    entry_price = mrow['close']
                    tp = prev_row['close']
                    sl = entry_price - abs(entry_price - tp)
                    sweep_min_row = mrow
                    break

            if sweep_type and sweep_min_row is not None:
                df_after_sweep = df_hour_minute[df_hour_minute['timestamp'] >= sweep_min_row['timestamp']]

                hit_tp = False
                hit_sl = False
                reverse_win = False

                twenty_min_later = sweep_min_row['timestamp'] + pd.Timedelta(minutes=20)

                for _, rrow in df_after_sweep.iterrows():
                    if sweep_type == 'high':
                        if rrow['low'] <= tp:
                            hit_tp = True
                            break
                        if rrow['high'] >= sl:
                            hit_sl = True
                            break
                    else:
                        if rrow['high'] >= tp:
                            hit_tp = True
                            break
                        if rrow['low'] <= sl:
                            hit_sl = True
                            break

                if not hit_tp and twenty_min_later <= df_after_sweep['timestamp'].max() and hit_sl:
                    reverse_df = df_after_sweep[df_after_sweep['timestamp'] >= twenty_min_later]
                    reverse_tp = abs(entry_price - tp)
                    if sweep_type == 'high':
                        for _, revrow in reverse_df.iterrows():
                            if revrow['low'] <= entry_price - reverse_tp:
                                reverse_win = True
                                break
                    else:
                        for _, revrow in reverse_df.iterrows():
                            if revrow['high'] >= entry_price + reverse_tp:
                                reverse_win = True
                                break

                retraced = hit_tp or reverse_win

                results.append({
                    'hour': hour_start,
                    'sweep_type': sweep_type,
                    'entry_price': entry_price,
                    'tp': tp,
                    'sl': sl,
                    'hit_tp': hit_tp,
                    'hit_sl': hit_sl,
                    'reverse_win': reverse_win,
                    'final_result': 'win' if retraced else 'loss'
                })

        if len(results) == 0:
            print("⚠️ No results found — check if your data covers the required conditions.")

        results_df = pd.DataFrame(results)

        print("\nResults DataFrame preview:")
        print(results_df.head())

        if 'final_result' in results_df.columns and len(results_df) > 0:
            total_setups = len(results_df)
            total_wins = (results_df['final_result'] == 'win').sum()
            total_losses = total_setups - total_wins
            overall_prob = (total_wins / total_setups * 100)

            print(f"\n🔢 Total setups: {total_setups}")
            print(f"✅ Total wins: {total_wins}")
            print(f"❌ Total losses: {total_losses}")
            print(f"🎯 Overall retracement probability: {overall_prob:.2f}%")
        else:
            print("❌ No 'final_result' column found in results DataFrame or no results to show.")

        output_file = 'nq_backtest_final_all_requirements.csv'
        results_df.to_csv(output_file, index=False)
        print(f"\n💾 Results saved to '{output_file}'.")

    except Exception as e:
        print(f"❌ Error processing file: {e}")

if __name__ == "__main__":
    run_backtest()
