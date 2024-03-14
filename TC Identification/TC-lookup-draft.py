import os
import xattr
import errno
import sys
import pandas as pd

# Return file creator and type codes
file_path = sys.argv[1]

def get_finder_info(file_path):
    try:
        finder_info = xattr.getxattr(file_path, 'com.apple.FinderInfo')
        return finder_info
    except OSError as e:
        if e.errno == errno.ENOATTR:
            print("Attribute not found.")
        else:
            print("Error accessing attribute:", e)
        return None

if __name__ == "__main__":
    finder_info = get_finder_info(file_path)
    if finder_info:
        type_code = finder_info[:4]
        creator_code = finder_info[4:8]
        print("Type Code:", type_code.decode('mac_roman'))
        print("Creator Code:", creator_code.decode('mac_roman'))
        
def get_resource_fork_size(file_path):
    try:
        resource_fork_size = len(xattr.getxattr(file_path, 'com.apple.ResourceFork'))
        return resource_fork_size
    except OSError as e:
        if e.errno == errno.ENOATTR:
            return 0  # Resource fork not found or empty
        else:
            raise  # Unexpected error
            
file_stats = os.stat(file_path)
print(f'Size of Data Fork: {file_stats.st_size} bytes')
            
size = get_resource_fork_size(file_path)
print(f'Size of Resource Fork: {size} bytes')


# Load the CSV file into a DataFrame
df = pd.read_csv('MacintoshEarlyFormats.csv', encoding='mac_roman')
# Search for rows containing the type code
rows_with_codes = df[(df['Type'] == type_code.decode('mac_roman')) & (df['Creator'] == creator_code.decode('mac_roman'))]
        
if not rows_with_codes.empty:
	print("Rows with Type Code {} and Creator Code {}: ".format(type_code, creator_code))
	for index, row in rows_with_codes.iterrows():
		print("Row index:", index)
		for column, value in row.items():
			print(f"{column}: {value}")
		print("-" * 30)
else:
	print("No rows found with Type Code {} and Creator Code {}.".format(type_code.decode('mac_roman'), creator_code.decode('mac_roman')))