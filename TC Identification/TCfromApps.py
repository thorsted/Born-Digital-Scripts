import os
import xattr
from rsrcfork import ResourceFile
import argparse
from openpyxl import Workbook
import tempfile
import subprocess
import shutil

ARCHIVE_EXTENSIONS = {'.sit', '.hqx', '.bin', '.cpt'}

def extract_with_unar(archive_path):
    temp_dir = tempfile.mkdtemp(prefix="unar_extract_")
    try:
        subprocess.run(['unar', '-o', temp_dir, archive_path], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"Extracted {archive_path} to {temp_dir}")
        return temp_dir
    except subprocess.CalledProcessError as e:
        print(f"Failed to extract {archive_path}: {e}")
        shutil.rmtree(temp_dir)
        return None

def scan_resource_forks(input_dir, ws, seen_rows):
    icon_types = [b'icl4', b'icl8', b'ICN#', b'ics#', b'ics4', b'ics8', b'ICON']

    for root, _, files in os.walk(input_dir):
        for filename in files:
            filepath = os.path.join(root, filename)
            try:
                xattrs = xattr.xattr(filepath)
                if b'com.apple.ResourceFork' not in xattrs:
                    # Could be a normal file or no resource fork
                    continue

                print(f"\nProcessing file: {filename}")
                with ResourceFile.open(filepath) as rf:
                    if b'BNDL' not in rf or b'FREF' not in rf:
                        print("Missing BNDL or FREF resources, skipping")
                        continue

                    bndl_res = next(iter(rf[b'BNDL'].values()))
                    creator_code = bndl_res.data[:4].decode('macroman', errors='replace')
                    print(f"Creator code: {creator_code}")

                    icon_lookup = {}
                    for icon_type in icon_types:
                        if icon_type not in rf:
                            continue
                        for icon_id, icon_res in rf[icon_type].items():
                            icon_name = icon_res.name.decode('macroman', errors='replace') if icon_res.name else ''
                            icon_lookup.setdefault(icon_id, []).append((icon_type.decode(), icon_name))

                    for fref_id, fref_res in rf[b'FREF'].items():
                        fref_data = fref_res.data
                        if len(fref_data) < 6:
                            continue
                        type_code = fref_data[0:4].decode('macroman', errors='replace')

                        icons = icon_lookup.get(fref_id, [])
                        if icons:
                            for icon_type, icon_name in icons:
                                row = (filename, creator_code, type_code, icon_type, icon_name)
                                if row not in seen_rows:
                                    ws.append(row)
                                    seen_rows.add(row)
                        else:
                            row = (filename, creator_code, type_code, '', '')
                            if row not in seen_rows:
                                ws.append(row)
                                seen_rows.add(row)

            except Exception as e:
                print(f"Error processing {filepath}: {e}")

def main():
    parser = argparse.ArgumentParser(description="Extract resource fork info from Mac files and archives")
    parser.add_argument('input_dir', help='Directory to scan for files')
    parser.add_argument('xlsx_output', help='Output XLSX file path')

    args = parser.parse_args()

    input_dir = args.input_dir
    xlsx_output = args.xlsx_output

    wb = Workbook()
    ws = wb.active
    ws.title = "Resource Fork Report"

    # Write header row
    ws.append(['filename', 'creator_code', 'type_code', 'icon_type', 'icon_name'])

    seen_rows = set()

    for root, _, files in os.walk(input_dir):
        for filename in files:
            filepath = os.path.join(root, filename)
            ext = os.path.splitext(filename)[1].lower()
            if ext in ARCHIVE_EXTENSIONS:
                print(f"Found archive: {filename}")
                extracted_dir = extract_with_unar(filepath)
                if extracted_dir:
                    scan_resource_forks(extracted_dir, ws, seen_rows)
                    shutil.rmtree(extracted_dir)
            else:
                # Regular file, scan directly
                scan_resource_forks(os.path.dirname(filepath), ws, seen_rows)
                # We break here because scan_resource_forks scans whole dir recursively
                # so avoid scanning same directory multiple times
                break

    wb.save(xlsx_output)
    print(f"\nXLSX report written to {xlsx_output}")

if __name__ == '__main__':
    main()
