import requests
import json
import os
import re

url = "https://www.chatcsv.co/api/v1/chat"
headers = {
    "accept": "text/event-stream",
    "Authorization": "Bearer sk_3ZZPwiUqxNpUKYTWAj1AVt9z"
}

# Base GitHub URL
base_github_url = "https://raw.githubusercontent.com/0921sean/chatcsv/refs/heads/main/"

# Metric descriptions
metric_description = {
    '1': "Center of Mass distance - Projects the center of mass (CoM) of the body on the ground and measures the distance from the support surface. The closer to the maximum value, the more stable the posture; the closer to the minimum value, the more unstable the posture, with a falling motion.",
    '2': "Symmetry - Compares the left and right sides of the body. The closer to the maximum value, the more symmetry between the left and right sides; the closer to the minimum value, the less symmetry.",
    '3': "Grounding - Indicates whether and to what extent both feet are grounded. Near the maximum value, both feet are in contact with the ground; near the minimum value, both legs are far from the ground.",
    '4': "Arm fold - Quantifies the angle of the arm (wrist-elbow-shoulder angle). Near the maximum value, both arms are fully extended; near the minimum value, both arms are folded.",
    '5': "Leg fold - Numerical representation of the angle of the legs (ankle-knee-pelvis angle). Near the maximum value, the legs are fully extended; near the minimum value, the legs are folded.",
    '6': "Kinetic energy - Represents the kinetic energy of the whole body. The closer to the maximum value, the higher the kinetic energy; the closer to the minimum value, the lower the kinetic energy.",
    '7': "Potential energy - Indicates the potential energy of the whole body. Near the maximum value, it represents a jumping position; near the minimum value, it represents a prone or sitting position.",
    '8': "Bone length coherence - Measures how well the initial inter-articular length is maintained throughout the motion sequence.",
    '9': "Torque - Calculates the torque value on the limbs. The closer to the maximum value, the higher the torque value; the closer to the minimum value, the lower the torque value.",
    '10': "Center velocity - Represents the speed of movement of the body's center of gravity. Near the maximum value, the body moves faster; near the minimum value, it moves slower."
}

# Directory paths
input_dir = "processed_csv"  # Directory containing the CSV files
output_dir = "responses"  # Directory to save the response text files
error_log_file = "error_log.txt"  # File to log errors
os.makedirs(output_dir, exist_ok=True)

# Pattern to match the filename
pattern = re.compile(r"(\d+)_(\d+)_\.csv")

# Sort files in the input directory
file_list = sorted(
    [f for f in os.listdir(input_dir) if pattern.match(f)],
    key=lambda x: int(pattern.match(x).group(1))  # Sort by the first identifier (i) numerically
)

# Iterate over each file in the directory
for filename in file_list:
    match = pattern.match(filename)
    if not match:
        print(f"Skipping file {filename} - does not match expected pattern.")
        continue

    # Extract identifiers from the filename
    i, j = match.groups()
    
    # Stop if the first identifier exceeds 79
    if int(i) > 79:
        break

    # Define the output file path based on the identifiers
    output_file = os.path.join(output_dir, f"{i}_{j}.txt")

    # Open output file for appending all metric descriptions
    with open(output_file, "w", encoding="utf-8") as file:
        # Iterate over all metrics to get descriptions
        for metric_key, description in metric_description.items():
            # Determine if the metric requires "maximum" or "minimum" frames
            max_or_min = "minimum" if int(metric_key) in [1, 3, 4] else "maximum"

            # Formulate the question based on the metric description
            question = f"{description}. Based on the description above, identify a 20-frame range in the motion data where this metric is most strongly represented ({max_or_min} value), indicating notable patterns or changes. Provide the range in the format '[start_frame, end_frame]' and include a brief explanation of the observed motion characteristics that justify your choice."

            # Construct the file URL based on the filename
            file_url = f"{base_github_url}{filename}"

            # Prepare request data
            data = {
                "model": "gpt-4-0613",
                "messages": [
                    {"role": "user", "content": "whats your name"},
                    {"role": "assistant", "content": "헤이즐넛"},
                    {"role": "user", "content": question},
                ],
                "files": [
                    file_url  # Use the GitHub URL for the file
                ]
            }

            # Attempt to send the request and handle any errors
            try:
                # Make the API request
                response = requests.post(url, headers=headers, data=json.dumps(data), stream=True)
                response.raise_for_status()  # Raise an error for bad status codes

                # Process the response line by line
                file.write(f"Metric {metric_key}:\n")
                for line in response.iter_lines():
                    if line:
                        decoded_line = line.decode("utf-8")
                        file.write(decoded_line + "\n")  # Save response to file
                        print(decoded_line)  # Optionally print the line
                file.write("\n")  # Add space between metrics
                print(f"Metric {metric_key} response saved for file {output_file}.")
                
            except requests.exceptions.RequestException as e:
                # Log the error in the error log file
                with open(error_log_file, "a", encoding="utf-8") as error_file:
                    error_file.write(f"Error with file {filename}, metric {metric_key}: {e}\n")
                print(f"An error occurred with file {filename}, metric {metric_key}. Logged to {error_log_file}.")