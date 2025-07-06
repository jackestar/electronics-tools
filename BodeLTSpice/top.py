import pandas as pd
import sys

if len(sys.argv) < 2:
    print("Usage: python top.py <datafile.txt>")
    sys.exit(1)

filename = sys.argv[1]

df = pd.read_csv(filename, sep='\t')
max_vout_row = df.loc[df['V(out)'].idxmax()]
min_vout_row = df.loc[df['V(out)'].idxmin()]

highest_vout = max_vout_row['V(out)']
time_at_highest_vout = max_vout_row['time']

lowest_vout = min_vout_row['V(out)']
time_at_lowest_vout = min_vout_row['time']

peak_to_peak = highest_vout - lowest_vout
amplitude = peak_to_peak/2
mid = (highest_vout + lowest_vout)/2

print(f"The highest value of V(out) is: {highest_vout:.6f} (at time {time_at_highest_vout:.6f})")
print(f"The lowest value of V(out) is: {lowest_vout:.6f} (at time {time_at_lowest_vout:.6f})")
print(f"Peak-to-peak value is: {peak_to_peak:.6f}")
print(f"mid value: {mid:.6f}")
print(f"amplitude value: {amplitude:.6f}")

