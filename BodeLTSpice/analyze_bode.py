import numpy as np
import re

def analyze_bode_from_file(file_path):
    """
    Reads and analyzes various Bode plot data formats, automatically detecting
    if the filter is Low-Pass or Band-Pass and calculating the appropriate
    characteristics, including the order of the slopes.
    """
    try:
        with open(file_path, 'r', encoding='latin-1') as f:
            lines = f.readlines()
    except FileNotFoundError:
        raise FileNotFoundError(f"Error: The file '{file_path}' was not found.")

    # A flexible regex to handle various whitespace formats.
    pattern = re.compile(r"^\s*([\d.eE+-]+)\s+.*?\(+(-?[\d.eE+-]+)dB,(-?[\d.eE+-]+)°\)\s*$")
    
    parsed_matches = []
    for line in lines:
        match = pattern.search(line.strip())
        if match:
            parsed_matches.append(match.groups())

    if not parsed_matches:
        raise ValueError("No valid data lines could be parsed. Please check the file's format.")

    frequencies = np.array([float(m[0]) for m in parsed_matches])
    gains_db = np.array([float(m[1]) for m in parsed_matches])

    # --- Filter Type Detection ---
    peak_gain_db = np.max(gains_db)
    peak_index = np.argmax(gains_db)
    dc_gain = gains_db[0]
    hf_gain = gains_db[-1]

    # If the peak gain is substantially higher than both ends, it's a band-pass filter.
    if peak_gain_db > dc_gain + 6 and peak_gain_db > hf_gain + 6:
        filter_type = "Band-Pass Filter"
    else:
        filter_type = "Low-Pass Filter"

    # --- Analysis Branching ---
    results = {"filter_type": filter_type}

    if filter_type == "Band-Pass Filter":
        results["peak_gain_db"] = peak_gain_db
        results["center_frequency_hz"] = frequencies[peak_index]
        cutoff_gain_db = peak_gain_db - 3.0

        # --- Find Low Cutoff (fL) on the rising slope ---
        fL = None
        for i in range(peak_index):
            if gains_db[i] < cutoff_gain_db and gains_db[i+1] >= cutoff_gain_db:
                p1_freq, p1_gain = frequencies[i], gains_db[i]
                p2_freq, p2_gain = frequencies[i+1], gains_db[i+1]
                log_f1, log_f2 = np.log10(p1_freq), np.log10(p2_freq)
                log_fL = log_f1 + (log_f2 - log_f1) * (cutoff_gain_db - p1_gain) / (p2_gain - p1_gain)
                fL = 10**log_fL
                break
        results["low_cutoff_hz"] = fL

        # --- Find High Cutoff (fH) on the falling slope ---
        fH = None
        for i in range(peak_index, len(gains_db) - 1):
            if gains_db[i] >= cutoff_gain_db and gains_db[i+1] < cutoff_gain_db:
                p1_freq, p1_gain = frequencies[i], gains_db[i]
                p2_freq, p2_gain = frequencies[i+1], gains_db[i+1]
                log_f1, log_f2 = np.log10(p1_freq), np.log10(p2_freq)
                log_fH = log_f1 + (log_f2 - log_f1) * (cutoff_gain_db - p1_gain) / (p2_gain - p1_gain)
                fH = 10**log_fH
                break
        results["high_cutoff_hz"] = fH

        if fL is None or fH is None:
            raise ValueError("Could not determine both -3dB cutoff frequencies.")

        # --- Order Calculation ---
        # Low-side (high-pass) slope using the first two points
        low_slope = (gains_db[1] - gains_db[0]) / np.log10(frequencies[1] / frequencies[0])
        results["low_side_order"] = int(np.round(low_slope / 20))
        results["low_side_slope"] = low_slope

        # High-side (low-pass) slope using the last two points
        high_slope = (gains_db[-1] - gains_db[-2]) / np.log10(frequencies[-1] / frequencies[-2])
        results["high_side_order"] = int(np.round(abs(high_slope) / 20))
        results["high_side_slope"] = high_slope

    elif filter_type == "Low-Pass Filter":
        # --- Estimate passband gain as the average gain before -3dB point ---
        cutoff_gain_db = dc_gain - 3.0
        fH = None
        cutoff_idx = None
        for i in range(len(gains_db) - 1):
            if gains_db[i] >= cutoff_gain_db and gains_db[i+1] < cutoff_gain_db:
                p1_freq, p1_gain = frequencies[i], gains_db[i]
                p2_freq, p2_gain = frequencies[i+1], gains_db[i+1]
                log_f1, log_f2 = np.log10(p1_freq), np.log10(p2_freq)
                log_fH = log_f1 + (log_f2 - log_f1) * (cutoff_gain_db - p1_gain) / (p2_gain - p1_gain)
                fH = 10**log_fH
                cutoff_idx = i
                break
        results["high_cutoff_hz"] = fH

        # Use average gain before cutoff as passband gain
        if cutoff_idx is not None and cutoff_idx > 0:
            passband_gain_db = np.mean(gains_db[:cutoff_idx+1])
        else:
            passband_gain_db = dc_gain
        results["passband_gain_db"] = passband_gain_db

        # --- Order calculation using -3dB and -40dB points ---
        stopband_attenuation_target_db = passband_gain_db - 40.0

        idx_sb = np.where(gains_db < stopband_attenuation_target_db)[0]
        if len(idx_sb) == 0:
            raise ValueError("Could not find a suitable stopband point (-40 dB).")
        sb_index = idx_sb[0]

        s1_freq, s1_gain = frequencies[sb_index - 1], gains_db[sb_index - 1]
        s2_freq, s2_gain = frequencies[sb_index], gains_db[sb_index]

        log_s1, log_s2 = np.log10(s1_freq), np.log10(s2_freq)
        log_f_sb = log_s1 + (log_s2 - log_s1) * (stopband_attenuation_target_db - s1_gain) / (s2_gain - s1_gain)
        f_sb = 10**log_f_sb

        f_pb = fH  # -3dB point
        gain_drop_db = stopband_attenuation_target_db - (passband_gain_db - 3.0)
        num_decades = np.log10(f_sb / f_pb)
        slope = gain_drop_db / num_decades
        order_from_gain = int(round(abs(slope) / 20))

        results["high_side_order"] = order_from_gain
        results["high_side_slope"] = slope

    return results

# --- Main Execution Block ---
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        data_file = sys.argv[1]
    else:
        data_file = "bode_data.txt"
    try:
        results = analyze_bode_from_file(data_file)
        
        print("Bode Plot Analysis Results:")
        print("=" * 50)
        print(f"Detected Filter Type: {results['filter_type']}")
        print("-" * 50)

        if results['filter_type'] == "Band-Pass Filter":
            print(f"Peak Gain:            {results['peak_gain_db']:.6f} dB")
            print(f"Center Frequency:     {results['center_frequency_hz']/1e3:.6f} kHz")
            print(f"Low Cutoff (fL):      {results['low_cutoff_hz']/1e3:.6f} kHz")
            print(f"High Cutoff (fH):     {results['high_cutoff_hz']/1e3:.6f} kHz")
            print("-" * 50)
            print("Slope Analysis:")
            print(f"Low-Side Order:       {results['low_side_order']} ({results['low_side_slope']:.6f} dB/decade)")
            print(f"High-Side Order:      {results['high_side_order']} ({results['high_side_slope']:.6f} dB/decade)")
        
        elif results['filter_type'] == "Low-Pass Filter":
            print(f"Passband Gain:        {results['passband_gain_db']:.6f} dB")
            print(f"High Cutoff (fH):     {results['high_cutoff_hz']/1e3:.6f} kHz")
            print("-" * 50)
            print("Slope Analysis:")
            print(f"High-Side Order:      {results['high_side_order']} ({results['high_side_slope']:.6f} dB/decade)")
            
        print("=" * 50)

    except (ValueError, FileNotFoundError) as e:
        print(f"\nAn error occurred: {e}")