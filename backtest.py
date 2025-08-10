from utils.data_loader import load_data
from backtest_engine.engine import run_backtest
import pandas as pd
from backtest_engine.cli import main


csv_hour = 'data/nq-1h_bk.csv'
csv_minute = 'data/nq-1m_bk.csv'
tick_size = 0.25
min_tick_distance = tick_size * 10  # 2.5 points

def main():
    print("🔄 Loading datasets...")
    df_hour, df_min = load_data(csv_hour, csv_minute)
    print(f"✅ Hourly rows after filter: {len(df_hour)}")
    print(f"✅ Minute rows after filter: {len(df_min)}")

    results = run_backtest(df_hour, df_min, min_tick_distance)

    if not results:
        print("⚠️ No results found — check if your data covers the required conditions.")
        return

    results_df = pd.DataFrame(results)
    print("\nResults DataFrame preview:")
    print(results_df.head())

    total_setups = len(results_df)
    total_wins = (results_df['final_result'] == 'win').sum()
    total_losses = total_setups - total_wins
    overall_prob = (total_wins / total_setups * 100)

    print(f"\n🔢 Total setups: {total_setups}")
    print(f"✅ Total wins: {total_wins}")
    print(f"❌ Total losses: {total_losses}")
    print(f"🎯 Overall retracement probability: {overall_prob:.2f}%")

    output_file = 'nq_backtest_final_all_requirements.csv'
    results_df.to_csv(output_file, index=False)
    print(f"\n💾 Results saved to '{output_file}'.")

if __name__ == '__main__':
    main()