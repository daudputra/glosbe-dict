import json
import os

def save_json(data, subfolder, filename):
    base_directory = 'data'
    directory = os.path.join(base_directory, subfolder)

    os.makedirs(directory, exist_ok=True)
    file_path = os.path.join(directory, filename)

    with open(file_path, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False)