import re
import argparse
import sys

def parse_simulation_data(file_path):
    """
    Parses the simulation file to extract the peak V(out) for each step.

    The file is expected to have blocks of data, each starting with a
    'Step Information' line.

    Args:
        file_path (str): The path to the input .txt file.

    Returns:
        list: A list of dictionaries, where each dictionary contains the
              'ck_value', 'step_label', and 'peak_voltage' for a step.
              Returns an empty list if no data could be parsed.
    """
    # Regex to capture Ck value and Step label from the info line
    # It captures:
    # 1. The value after "Ck=" (e.g., '100', '1K')
    # 2. The value inside "(Step: ...)" (e.g., '1/100')
    step_info_pattern = re.compile(r"Ck=([\w\.]+)\s+\(Step: ([\d\/]+)\)")

    all_steps_data = []
    current_voltages = []
    current_step_info = {}

    try:
        with open(file_path, 'r') as f:
            # Skip the initial header line "time  V(out)"
            next(f, None)

            for line in f:
                line = line.strip()
                if not line:
                    continue

                # Check if the line is a step separator
                if line.startswith("Step Information:"):
                    # If we have data from a previous step, process it first
                    if current_voltages and current_step_info:
                        peak_v = max(current_voltages)
                        current_step_info['peak_voltage'] = peak_v
                        all_steps_data.append(current_step_info)

                    # Now, parse the new step's information
                    match = step_info_pattern.search(line)
                    if match:
                        current_step_info = {
                            'ck_value': match.group(1),
                            'step_label': match.group(2)
                        }
                        # Reset the list for the new step's voltages
                        current_voltages = []
                    else:
                        # If a line starts with "Step Information" but doesn't match,
                        # something is wrong with the format.
                        current_step_info = {} # Reset to avoid misattribution
                        
                # Otherwise, it's a data line (time, voltage)
                else:
                    try:
                        # Split by whitespace and take the second column (voltage)
                        parts = line.split()
                        if len(parts) >= 2:
                           voltage = float(parts[1])
                           current_voltages.append(voltage)
                    except (ValueError, IndexError):
                        # Ignore lines that are not valid data pairs
                        # print(f"Warning: Could not parse data line: {line}")
                        pass
            
            # Don't forget to process the very last step after the loop finishes
            if current_voltages and current_step_info:
                peak_v = max(current_voltages)
                current_step_info['peak_voltage'] = peak_v
                all_steps_data.append(current_step_info)

    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)

    return all_steps_data


def find_nearest_peak(steps_data, target_value):
    """
    Finds the step whose peak voltage is nearest to the target value.

    Args:
        steps_data (list): A list of step data dictionaries from parse_simulation_data.
        target_value (float): The target voltage value.

    Returns:
        dict: The dictionary of the best matching step, or None if no data.
    """
    if not steps_data:
        return None

    best_match_step = None
    # Initialize minimum difference to a very large number
    min_difference = float('inf')

    for step in steps_data:
        difference = abs(step['peak_voltage'] - target_value)
        if difference < min_difference:
            min_difference = difference
            best_match_step = step
            
    return best_match_step

# This makes the script runnable from the command line
if __name__ == "__main__":
    # Set up argument parser for a professional command-line interface
    parser = argparse.ArgumentParser(
        description="Find the step in a simulation file whose peak V(out) is nearest to a target value."
    )
    parser.add_argument("file", help="Path to the input data file (.txt)")
    parser.add_argument("target_voltage", type=float, help="The target V(out) value to match.")
    
    args = parser.parse_args()

    # 1. Parse the entire file to get all step peaks
    parsed_data = parse_simulation_data(args.file)

    if not parsed_data:
        print("Could not find any valid step data in the file.")
        sys.exit(1)

    # 2. Find the step with the peak nearest to the target
    best_step = find_nearest_peak(parsed_data, args.target_voltage)

    # 3. Print the result
    if best_step:
        print("\n--- Analysis Complete ---")
        print(f"Target V(out): {args.target_voltage:.4f}")
        print("\n🏆 Best match found:")
        print(f"  - Step:         {best_step['step_label']}")
        print(f"  - Ck Value:     {best_step['ck_value']}")
        print(f"  - Peak V(out):  {best_step['peak_voltage']:.4f}")
        
        diff = abs(best_step['peak_voltage'] - args.target_voltage)
        print(f"  - Difference:   {diff:.4f}")
    else:
        print("No suitable step data was found to analyze.")