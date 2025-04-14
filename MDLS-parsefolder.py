import os
import subprocess
import csv
import sys

def get_metadata(file_path):
    result = subprocess.run(['mdls', file_path], capture_output=True, text=True)
    metadata = {}
    current_key = None
    for line in result.stdout.splitlines():
        if '=' in line:
            key, value = line.split('=', 1)
            key = key.strip()
            value = value.strip().strip('"')
            if value.startswith('('):
                current_key = key
                metadata[current_key] = value
            else:
                metadata[key] = value
        elif current_key:
            metadata[current_key] += ' ' + line.strip()
            if line.strip().endswith(')'):
                current_key = None
    return metadata

def process_files(folder_path, output_file):
    all_fieldnames = set(['Path', 'Filename', 'Extension', 'IsPackage'])
    files_metadata = []

    for root, dirs, files in os.walk(folder_path):
        # Check if the current directory has an extension
        if '.' in os.path.basename(root):
            metadata = get_metadata(root)
            metadata['Path'] = os.path.dirname(root)
            metadata['Filename'] = os.path.basename(root)
            metadata['Extension'] = os.path.splitext(root)[1][1:]
            metadata['IsPackage'] = True
            files_metadata.append(metadata)
            all_fieldnames.update(metadata.keys())
            # Skip processing files within this directory
            dirs[:] = []
            continue

        for file in files:
            # Ignore .DS_Store hidden files
            if file == '.DS_Store':
                continue

            file_path = os.path.join(root, file)
            metadata = get_metadata(file_path)
            metadata['Path'] = root
            metadata['Filename'] = file
            metadata['Extension'] = os.path.splitext(file)[1][1:]
            metadata['IsPackage'] = False
            files_metadata.append(metadata)
            all_fieldnames.update(metadata.keys())

    with open(output_file, mode='w', newline='') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=sorted(all_fieldnames))
        writer.writeheader()
        for metadata in files_metadata:
            writer.writerow(metadata)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: MDLS-parsefolder.py <folder_path> <output_csv>")
        sys.exit(1)

    folder_path = sys.argv[1]
    output_file = sys.argv[2]
    process_files(folder_path, output_file)
    print(f"Metadata extraction completed. CSV written to: {output_file}")