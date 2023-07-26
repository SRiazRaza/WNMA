def extract_distance_from_filename(filename):
    # Split the filename by underscores
    parts = filename.split('.')
    
    # Look for the part containing "meters"
    for part in parts:
        if 'meters' in part:
            return part

    # If "meters" part is not found, return None
    return None

# Example usage:
filename1 = "/data/2023.07.15.10_meters.csv"
filename2 = "/data/2023.07.15.bg_after_10_meters.csv"

distance1 = extract_distance_from_filename(filename1)
distance2 = extract_distance_from_filename(filename2)

print("Distance from filename1:", distance1)
print("Distance from filename2:", distance2)