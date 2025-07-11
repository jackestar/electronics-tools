import re
import os
import math
import sys

def parse_data_file(filepath):
    """
    Parses the simulation data file into a structured format.

    The file has blocks, each starting with 'Step Information:'.
    Each block contains frequency and V(out) data.

    Args:
        filepath (str): The path to the input data file.

    Returns:
        list: A list of dictionaries, where each dictionary represents a step
              and contains its info and data points.
              Example:
              [
                {
                  'info': 'Ck=1K  (Step: 1/31)',
                  'ck_value': '1K',
                  'data': [
                    {'freq': 1.0, 'gain_db': -0.146, 'phase': -87.1},
                    ...
                  ]
                },
                ...
              ]
    """
    if not os.path.exists(filepath):
        print(f"Error: File not found at '{filepath}'")
        return None

    all_steps_data = []
    current_step_data = None

    # Regex to parse the V(out) column like: (1.23dB,-45.6°)
    vout_regex = re.compile(r"\((?P<gain>.*?)dB,(?P<phase>.*?)°\)")
    
    # Regex to parse the Step Information line
    step_info_regex = re.compile(r"Ck=([\w.-]+)")

    with open(filepath, 'r', encoding='latin1') as f:  # <-- Use latin1 encoding
        for line in f:
            line = line.strip()
            if not line:
                continue

            # Check if this line is the start of a new step
            if line.startswith("Step Information:"):
                # If we were processing a previous step, save it
                if current_step_data:
                    all_steps_data.append(current_step_data)
                
                # Start a new step
                ck_match = step_info_regex.search(line)
                ck_value = ck_match.group(1) if ck_match else "Unknown"
                current_step_data = {
                    'info': line.replace("Step Information: ", ""),
                    'ck_value': ck_value,
                    'data': []
                }
                continue

            # Ignore header lines
            if line.startswith("Freq."):
                continue

            # If we are inside a step block, parse the data row
            if current_step_data:
                parts = line.split(maxsplit=1)
                if len(parts) == 2:
                    try:
                        freq = float(parts[0])
                        vout_str = parts[1]
                        
                        match = vout_regex.match(vout_str)
                        if match:
                            gain_db = float(match.group('gain'))
                            phase = float(match.group('phase'))
                            current_step_data['data'].append({
                                'freq': freq,
                                'gain_db': gain_db,
                                'phase': phase
                            })
                    except (ValueError, IndexError):
                        # Ignore malformed data lines
                        print(f"Warning: Could not parse line: {line}")
                        continue
    
    # Append the very last step's data after the loop finishes
    if current_step_data:
        all_steps_data.append(current_step_data)

    return all_steps_data


def find_best_step(all_steps_data, target_freq, target_gain_db):
    """
    Finds the best step that matches the target frequency and gain.

    1. For each step, it finds the data point with the frequency closest to target_freq.
    2. Among those results, it finds the one whose gain is closest to target_gain_db.

    Args:
        all_steps_data (list): The parsed data from the file.
        target_freq (float): The desired frequency.
        target_gain_db (float): The desired gain in dB.

    Returns:
        dict: A dictionary containing the details of the best match found,
              or None if no suitable match could be found.
    """
    best_match = None
    smallest_gain_diff = float('inf')

    if not all_steps_data:
        print("Error: No data was parsed from the file.")
        return None

    for step in all_steps_data:
        if not step['data']:
            continue # Skip steps with no data points

        # 1. Find the row with the frequency closest to the target for THIS step
        closest_freq_point = min(
            step['data'],
            key=lambda point: abs(point['freq'] - target_freq)
        )

        # 2. Calculate the difference in gain for this best-frequency point
        gain_diff = abs(closest_freq_point['gain_db'] - target_gain_db)

        # 3. Check if this step is the best one we've found so far
        if gain_diff < smallest_gain_diff:
            smallest_gain_diff = gain_diff
            best_match = {
                'step_info': step['info'],
                'ck_value': step['ck_value'],
                'found_freq': closest_freq_point['freq'],
                'found_gain_db': closest_freq_point['gain_db'],
                'gain_difference': gain_diff
            }

    return best_match

def find_minus3db_points(all_steps_data):
    """
    For each step, finds the frequency where the gain is closest to (peak gain - 3 dB).
    Returns a list of dictionaries with info for each step.
    """
    results = []
    for step in all_steps_data:
        if not step['data']:
            continue
        # Find peak gain for this step
        peak_gain = max(point['gain_db'] for point in step['data'])
        target_gain = peak_gain - 3
        # Find the point closest to target_gain
        closest_point = min(
            step['data'],
            key=lambda point: abs(point['gain_db'] - target_gain)
        )
        results.append({
            'step_info': step['info'],
            'ck_value': step['ck_value'],
            'peak_gain': peak_gain,
            'target_gain': target_gain,
            'found_freq': closest_point['freq'],
            'found_gain_db': closest_point['gain_db'],
            'gain_difference': abs(closest_point['gain_db'] - target_gain)
        })
    return results

def find_step_closest_to_minus3db_at_freq(all_steps_data, target_freq):
    """
    For each step, finds the peak gain, computes (peak gain - 3),
    then finds the gain at the target frequency (or closest frequency in that step),
    and returns the step whose gain at that frequency is closest to (peak gain - 3).
    """
    results = []
    for step in all_steps_data:
        if not step['data']:
            continue
        # Find peak gain for this step
        peak_gain = max(point['gain_db'] for point in step['data'])
        target_gain = peak_gain - 3
        # Find the point in this step closest to the target frequency
        closest_point = min(
            step['data'],
            key=lambda point: abs(point['freq'] - target_freq)
        )
        gain_at_freq = closest_point['gain_db']
        freq_at_freq = closest_point['freq']
        gain_diff = abs(gain_at_freq - target_gain)
        results.append({
            'step_info': step['info'],
            'ck_value': step['ck_value'],
            'peak_gain': peak_gain,
            'target_gain': target_gain,
            'freq': freq_at_freq,
            'gain_at_freq': gain_at_freq,
            'gain_difference': gain_diff
        })
    # Find the step whose gain at the target frequency is closest to (peak gain - 3)
    if results:
        return min(results, key=lambda res: res['gain_difference'])
    else:
        return None

# --- Main execution part of the script ---
if __name__ == "__main__":
    # Usage: python findStepinBode.py <datafile.txt> <frequency>
    if len(sys.argv) < 3:
        print("Usage: python findStepinBode.py <datafile.txt> <frequency>")
        sys.exit(1)
    file_path = sys.argv[1]
    try:
        target_freq = float(sys.argv[2])
        print(f"\nYou entered: Frequency = {target_freq} Hz")
    except ValueError:
        print("\nError: Invalid input. Please enter a numeric value for frequency.")
        exit()

    print("\nParsing file...")
    parsed_data = parse_data_file(file_path)

    if parsed_data:
        print(f"Successfully parsed {len(parsed_data)} steps.")
        closest = find_step_closest_to_minus3db_at_freq(parsed_data, target_freq)
        if closest:
            print("\n" + "="*40)
            print("   STEP CLOSEST TO -3dB AT YOUR FREQUENCY")
            print("="*40)
            print(f"Target Frequency: {target_freq:.4g} Hz")
            print("-" * 40)
            print(f"Step Info:   {closest['step_info']}")
            print(f"Ck Value:    {closest['ck_value']}")
            print(f"Peak Gain:   {closest['peak_gain']:.4f} dB")
            print(f"-3dB Gain:   {closest['target_gain']:.4f} dB")
            print(f"Freq Used:   {closest['freq']:.4g} Hz")
            print(f"Gain at Freq:{closest['gain_at_freq']:.4f} dB")
            print(f"Difference:  {closest['gain_difference']:.4f} dB")
            print("="*40)
        else:
            print("\nNo valid steps found in the data.")
    else:
        print("\nCould not parse any steps from the provided data.")