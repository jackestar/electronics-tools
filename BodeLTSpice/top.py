import pandas as pd
import sys

if len(sys.argv) < 2:
    print("Usage: python top.py <datafile.txt>")
    sys.exit(1)

filename = sys.argv[1]

df = pd.read_csv(filename, sep='\t')

signals = [col for col in df.columns if col != 'time']

for signal in signals:
    max_row = df.loc[df[signal].idxmax()]
    min_row = df.loc[df[signal].idxmin()]

    highest = max_row[signal]
    time_at_highest = max_row['time']

    lowest = min_row[signal]
    time_at_lowest = min_row['time']

    peak_to_peak = highest - lowest
    amplitude = peak_to_peak / 2
    mid = (highest + lowest) / 2

    print(f"\nSignal: {signal}")
    print(f"  Highest value: {highest:.6f} (at time {time_at_highest:.6f})")
    print(f"  Lowest value:  {lowest:.6f} (at time {time_at_lowest:.6f})")
    print(f"  Peak-to-peak:  {peak_to_peak:.6f}")
    print(f"  Mid value:     {mid:.6f}")
    print(f"  Amplitude:     {amplitude:.6f}")

