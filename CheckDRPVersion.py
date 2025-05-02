import os
import zipfile
import argparse

def find_files_with_extensions(folder_path, extensions):
    files_found = {ext: [] for ext in extensions}
    if os.path.isfile(folder_path):
        for ext in extensions:
            if folder_path.endswith(ext):
                files_found[ext].append(folder_path)
    else:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                for ext in extensions:
                    if file.endswith(ext):
                        full_path = os.path.join(root, file)
                        files_found[ext].append(full_path)
    return files_found

def extract_xml_from_zip(zip_path):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        for file in zip_ref.namelist():
            if file.endswith('project.xml'):
                with zip_ref.open(file) as xml_file:
                    return xml_file.read().decode('utf-8')
    return None

def parse_xml_for_dbappver(xml_content):
    lines = xml_content.split('\n')
    if len(lines) > 1 and lines[1].startswith('<!--DbAppVer'):
        return lines[1]
    return None

def main(input_path):
    extensions = ['.drp', '.drt']
    files_found = find_files_with_extensions(input_path, extensions)
    
    results = []
    for ext, files in files_found.items():
        for file in files:
            xml_content = extract_xml_from_zip(file)
            if xml_content:
                dbappver_line = parse_xml_for_dbappver(xml_content)
                if dbappver_line:
                    results.append(f"{file}: {dbappver_line}")
    
    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process some files.")
    parser.add_argument("input_path", type=str, help="Path to the folder or file to process")
    args = parser.parse_args()
    
    results = main(args.input_path)
    for result in results:
        print(result)
