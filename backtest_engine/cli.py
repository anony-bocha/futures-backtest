import argparse
from backtest_engine.engine import run_backtest

def main():
    parser = argparse.ArgumentParser(description='Run futures backtest on provided data files.')

    parser.add_argument('--csv_hour', type=str, default='data/nq-1h_bk.csv',
                        help='Path to hourly CSV data file (default: data/nq-1h_bk.csv)')
    parser.add_argument('--csv_minute', type=str, default='data/nq-1m_bk.csv',
                        help='Path to minute CSV data file (default: data/nq-1m_bk.csv)')
    parser.add_argument('--tick_size', type=float, default=0.25,
                        help='Tick size for the instrument (default: 0.25)')
    parser.add_argument('--start_hour', type=str, default='08:00:00',
                        help='Trading session start time (HH:MM:SS, default: 08:00:00)')
    parser.add_argument('--end_hour', type=str, default='16:00:00',
                        help='Trading session end time (HH:MM:SS, default: 16:00:00)')
    parser.add_argument('--output_file', type=str, default='nq_backtest_final_all_requirements.csv',
                        help='Output CSV filename for results (default: nq_backtest_final_all_requirements.csv)')

    args = parser.parse_args()

    run_backtest(
        csv_hour=args.csv_hour,
        csv_minute=args.csv_minute,
        tick_size=args.tick_size,
        start_hour=args.start_hour,
        end_hour=args.end_hour,
        output_file=args.output_file
    )

if __name__ == '__main__':
    main()
