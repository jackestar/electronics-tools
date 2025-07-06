import pandas as pd
import sys

if len(sys.argv) < 2:
    print("Usage: python top.py <datafile.txt>")
    sys.exit(1)

filename = sys.argv[1]

df = pd.read_csv(filename, sep='\t')
max_vout_row = df.loc[df['V(out)'].idxmax()]

highest_vout = max_vout_row['V(out)']
time_at_highest_vout = max_vout_row['time']

print(f"The highest value of V(out) is: {highest_vout}")
print(f"This occurred at time: {time_at_highest_vout}")

