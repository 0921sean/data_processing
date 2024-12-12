import requests
import json
import time
import os
import re

url = "https://www.chatcsv.co/api/v1/chat"
headers = {
    "accept": "text/event-stream",
    "Authorization": "Bearer sk_3ZZPwiUqxNpUKYTWAj1AVt9z"
}

# Base GitHub URL
base_github_url = "https://raw.githubusercontent.com/0921sean/chatcsv/refs/heads/main/"

metric_description = {
    '1': "Center of Mass distance - Projects the center of mass (CoM) of the body on the ground and measures the distance from the support surface. The closer to the maximum value, the more stable the posture; the closer to the minimum value, the more unstable the posture, with a falling motion.",
    '2': "Symmetry - Compares the left and right sides of the body. The closer to the maximum value, the more symmetry between the left and right sides; the closer to the minimum value, the less symmetry.",
    '3': "Kinetic Energy - Represents the kinetic energy of the whole body. The closer to the maximum value, the higher the kinetic energy; the closer to the minimum value, the lower the kinetic energy.",
    '4': "Potential Energy - Indicates the potential energy of the whole body. Near the maximum value, it represents a jumping position; near the minimum value, it represents a prone or sitting position.",
}

# Directory paths
input_dir = "processed_csv"  # Directory containing the CSV files
output_dir = "metric_description"  # Directory to save the response JSON files
error_log_file = "error_log.txt"  # File to log errors
os.makedirs(output_dir, exist_ok=True)

# Pattern to match the filename
pattern = re.compile(r"(\d+)_(\d+)_\.csv")

# Sort files in the input directory
file_list = sorted(
    [f for f in os.listdir(input_dir) if pattern.match(f)],
    key=lambda x: int(pattern.match(x).group(1))  # Sort by the first identifier (i) numerically
)

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

    # Define the output JSON file path
    output_file = os.path.join(output_dir, f"motion_{i}_{j}.json")
    motion_data = {}  # Dictionary to store all metric responses for this file

    # Iterate over all metrics to get descriptions
    for metric_key, full_description in metric_description.items():
        short_description = full_description.split(' -')[0]

        max_or_min = "minimum" if int(metric_key) == 1 else "maximum"

        question = f"{full_description}. Based on the description above, identify a 20-frame range in the motion data where this metric is most strongly represented ({max_or_min} value), indicating notable patterns or changes. Provide the range in the format '[start_frame, end_frame]' and include a brief explanation of the observed motion characteristics that justify your choice."

        file_url = f"{base_github_url}{filename}"

        data = {
            "model": "gpt-4-0613",
            "messages": [
                {"role": "user", "content": "whats your name"},
                {"role": "assistant", "content": "metric : Metric Name range : [start_frame, end_frame], description: Brief explanation of the observed characteristics. Example: 1. [metric: Symmetry range : [100, 120] description: Symmetry is maximized during this range.]"},
                {"role": "user", "content": question},
            ],
            "files": [
                file_url  # Use the GitHub URL for the file
            ]
        }

        retry = True  # Flag to control retries
        while retry:
            try:
                response = requests.post(url, headers=headers, data=json.dumps(data), stream=True)
                response.raise_for_status()

                response_text = ""
                for line in response.iter_lines():
                    if line:
                        decoded_line = line.decode("utf-8")
                        response_text += decoded_line + "\n"
                        print(decoded_line)  # Print the response line by line

                # Check if the response starts with the expected format
                if response_text.startswith("The 20-frame range where"):
                    # Add the response for this metric to the motion_data dictionary
                    motion_data[f"Metric_{metric_key}"] = {
                        "metric": short_description,
                        "description": response_text.strip()
                    }
                    print(f"Metric {metric_key} response saved for file {output_file}.")
                    retry = False  # Correct format, stop retrying

                else:
                    print("Unexpected format, retrying in 2 seconds...")
                    time.sleep(2)  # Delay before retrying

            except requests.exceptions.RequestException as e:
                with open(error_log_file, "a", encoding="utf-8") as error_file:
                    error_file.write(f"Error with file {filename}, metric {metric_key}: {e}\n")
                print(f"An error occurred with file {filename}, metric {metric_key}. Logged to {error_log_file}.")
                retry = False  # Stop retrying on request failure

    # Save the motion data to a JSON file
    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(motion_data, file, ensure_ascii=False, indent=4)

    print(f"Response has been saved to {output_file}.")