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
    # '3': "Grounding - Indicates whether and to what extent both feet are grounded. Near the maximum value, both feet are in contact with the ground; near the minimum value, both legs are far from the ground.",
    # '4': "Arm fold - Quantifies the angle of the arm (wrist-elbow-shoulder angle). Near the maximum value, both arms are fully extended; near the minimum value, both arms are folded.",
    # '5': "Leg fold - Numerical representation of the angle of the legs (ankle-knee-pelvis angle). Near the maximum value, the legs are fully extended; near the minimum value, the legs are folded.",
    '3': "Kinetic Energy - Represents the kinetic energy of the whole body. The closer to the maximum value, the higher the kinetic energy; the closer to the minimum value, the lower the kinetic energy.",
    '4': "Potential Energy - Indicates the potential energy of the whole body. Near the maximum value, it represents a jumping position; near the minimum value, it represents a prone or sitting position.",
    # '8': "Bone length coherence - Measures how well the initial inter-articular length is maintained throughout the motion sequence.",
    # '9': "Torque - Calculates the torque value on the limbs. The closer to the maximum value, the higher the torque value; the closer to the minimum value, the lower the torque value.",
    # '10': "Center velocity - Represents the speed of movement of the body's center of gravity. Near the maximum value, the body moves faster; near the minimum value, it moves slower.",
    # '11': "Extremity speed - Represents the speed of movement of the end joints of the limbs (wrists, ankles). The closer to the maximum value, the faster the movement of the extremities.",
    # '12': "Left arm extremity angular velocity - Represents the angular velocity of the left arm. The closer to the maximum value, the faster the rotation of the joint.",
    # '13': "Right arm extremity angular velocity - Represents the angular velocity of the right arm. The closer to the maximum value, the faster the rotation of the joint.",
    # '14': "Left leg extremity angular velocity - Represents the angular velocity of the left leg. The closer to the maximum value, the faster the rotation of the joint.",
    # '15': "Right leg extremity angular velocity - Represents the angular velocity of the right leg. The closer to the maximum value, the faster the rotation of the joint.",
    # '16': "Partial joint attention - Measures how much one part of the body moves more prominently than the others. Near the maximum value, one part moves overwhelmingly more; near the minimum value, all parts move similarly.",
    # '17': "Efficiency - Measures the straightness of joint movement. Near the maximum value, the movement is straight and efficient; near the minimum value, the movement is jerky and inefficient.",
    # '18': "Spatiality - Represents the amount of space occupied by a motion. Near the maximum value, the whole body moves in a larger and faster manner."
}

# Directory paths
input_dir = "processed_csv"  # Directory containing the CSV files
output_dir = "formatted"  # Directory to save the response text files
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

    # Define the output file path based on the identifiers
    output_file = os.path.join(output_dir, f"{i}_{j}.txt")

    while True:
        # Open output file for appending all metric descriptions
        with open(output_file, "w", encoding="utf-8") as file:
            # Iterate over all metrics to get descriptions
            for metric_key, description in metric_description.items():
                # Determine if the metric requires "maximum" or "minimum" frames
                max_or_min = "minimum" if int(metric_key) == 1 else "maximum"

                # Formulate the question based on the metric description
                question = f"{description}. Based on the description above, identify a 20-frame range in the motion data where this metric is most strongly represented ({max_or_min} value), indicating notable patterns or changes.Provide the range in the format '[start_frame, end_frame]' and include a brief explanation of the observed motion characteristics that justify your choice."

                # Construct the file URL based on the filename
                file_url = f"{base_github_url}{filename}"

                # Prepare request data
                data = {
                    "model": "gpt-4-0613",
                    "messages": [
                        {"role": "user", "content": "whats your name"},
                        {"role": "assistant", "content": "metric : Metric Namerange : [start_frame, end_frame],description: Brief explanation of the observed characteristicsFor example: 1. [metric:  Symmetry range : [100, 120] description : Symmetry is maximized during this range.] 2. [metric: Leg foldrange: [253, 273]description: In this range, the 'Leg fold' metric reaches its maximum value, indicating that the legs are fully extended.]"},
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
                    
                    # Check if description starts with the correct format
                    if response.iter_lines[0].startswith(f"The 20-frame range where the "):
                        # Process the response line by line
                        file.write(f"Metric {metric_key}:\n")
                        for line in response.iter_lines():
                            if line:
                                decoded_line = line.decode("utf-8")
                                file.write(decoded_line + "\n")  # Save response to file
                                print(decoded_line)  # Optionally print the line
                        file.write("\n")  # Add space between metrics
                        print(f"Metric {metric_key} response saved for file {output_file}.")
                        break  # 올바른 포맷이 나왔으므로 while 루프를 종료

                    # 기다렸다가 다시 요청을 보내기 전에 딜레이를 추가
                    time.sleep(2)
                    
                except requests.exceptions.RequestException as e:
                    # Log the error in the error log file
                    with open(error_log_file, "a", encoding="utf-8") as error_file:
                        error_file.write(f"Error with file {filename}, metric {metric_key}: {e}\n")
                    print(f"An error occurred with file {filename}, metric {metric_key}. Logged to {error_log_file}.")

# for i in range(1, 21):
#     motion_data = {f'motion_{i}': []}  # Initialize motion data as a list
#     for j in range(1, 5):
#         max_or_min = "minimum" if j == 1 else "maximum"
        
#         # 메트릭 이름 추출 (첫 번째 '-' 이전까지)
#         metric_name = metric_description[str(j)].split(' - ')[0]
        
#         while True:  # 계속 반복해서 같은 i, j에 대해 실행
#             question = f"{metric_description[str(j)]}. Based on the description above, identify a 20-frame range in the motion data where this metric is most strongly represented ({max_or_min} value), indicating notable patterns or changes.Provide the range in the format '[start_frame, end_frame]' and include a brief explanation of the observed motion characteristics that justify your choice."
            
#             data = {
#                 "model": "gpt-4-0613",
#                 "messages": [
#                     {"role": "user", "content": "whats your name"},
#                     {"role": "assistant", "content": "metric : Metric Namerange : [start_frame, end_frame],description: Brief explanation of the observed characteristicsFor example: 1. [metric:  Symmetry range : [100, 120] description : Symmetry is maximized during this range.] 2. [metric: Leg foldrange: [253, 273]description: In this range, the 'Leg fold' metric reaches its maximum value, indicating that the legs are fully extended.]"},
#                     {"role": "user", "content": question},
#                 ],
#                 "files": [
#                     f"https://raw.githubusercontent.com/0921sean/chatcsv/refs/heads/main/motion_{i}.csv"
#                 ]
#             }

#             response = requests.post(url, headers=headers, data=json.dumps(data), stream=True)

#             description = ""
#             for line in response.iter_lines():
#                 if line:
#                     decoded_line = line.decode("utf-8")
#                     description += decoded_line + "\n"
                    
#             print(description)

#             # Check if description starts with the correct format
#             if description.strip().startswith(f"The 20-frame range where the "):
#                 motion_data[f'motion_{i}'].append({
#                     'description': description.strip()
#                 })
#                 break  # 올바른 포맷이 나왔으므로 while 루프를 종료

#             # 기다렸다가 다시 요청을 보내기 전에 딜레이를 추가
#             time.sleep(2)
            
#         # Save the motion data to a JSON file
#         with open(f"motion_{i}.json", "w", encoding="utf-8") as file:
#             json.dump(motion_data, file, ensure_ascii=False, indent=4)

#         print(f"Response has been saved to motion_{i}.json.")