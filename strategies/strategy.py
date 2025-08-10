def detect_sweep_and_trade(prev_row, curr_row, df_minute, min_tick_distance):
    """
    Detects a sweep (high or low) and calculates trade parameters and results.

    Args:
        prev_row (pd.Series): Previous hourly candle.
        curr_row (pd.Series): Current hourly candle.
        df_minute (pd.DataFrame): Minute data filtered for current hour.
        min_tick_distance (float): Minimum tick distance threshold.

    Returns:
        dict or None: Trade result details or None if no valid trade.
    """
    # Check if current open inside previous candle body
    if not (prev_row['low'] < curr_row['open'] < prev_row['high']):
        return None

    # Consider only first 20 minutes for sweep
    df_first_20 = df_minute[df_minute['timestamp'].dt.minute < 20]

    sweep_type = None
    sweep_min_row = None
    entry_price = None
    tp = None
    sl = None

    # Sweep detection loop
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

    if not sweep_type or sweep_min_row is None:
        return None

    # After sweep, check TP/SL hit and reverse trades
    df_after_sweep = df_minute[df_minute['timestamp'] >= sweep_min_row['timestamp']]

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

    return {
        'sweep_type': sweep_type,
        'entry_price': entry_price,
        'tp': tp,
        'sl': sl,
        'hit_tp': hit_tp,
        'hit_sl': hit_sl,
        'reverse_win': reverse_win,
        'final_result': 'win' if retraced else 'loss'
    }
