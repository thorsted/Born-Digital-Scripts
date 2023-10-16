import pandas as pd
import sys

inputcsv = sys.argv[1]
outputcsv = sys.argv[2]
identifier = input("IE Identifer: ") # Identifier (DC)
rights = input("Rights: ")
collection = input("Collection: ") # Maps to the DC Terms "Is Part of"
qualifier = input("Path Separator: ") # This is the folder right before the content wanting to ingest.

# read CSV input file
df = pd.read_csv(sys.argv[1])
df = df.replace(r"\\", "/", regex=True) # Converts paths from Windows backslashes to forward slashes needed for Linux


# Create a new DataFrame for the desired output format
output_df = pd.DataFrame(columns=["Object Type", "Title (DC)", "Title (DC)", "Creator (DC)", "Description (DC)",
                                  "Date (DC)", "Type (DC)", "Format (DC)", "Identifier (DC)", "Rights (DC)",
                                  "Source (DC)", "Language (DC)", "Publisher (DC)", "Subject (DC)",
                                  "Is Part Of (DCTERMS)", "Created (DCTERMS)", "Modified (DCTERMS)",
                                  "Provenance (DC)", "Submission Reason", "Abstract (DCTERMS)",
                                  "Digital Original", "Preservation Type", "Physical Carrier Media",
                                  "File Original Path", "File Original Name", "SHA1", "SHA256",
                                  "Note", "Inhibitor Key", "Inhibitor Target", "Inhibitor Type",
                                  "File Label", "FILE - Title (DC)", "FILE - Subject (DC)",
                                  "FILE - Description (DC)", "FILE - Creator (DC)", "FILE - Format (DC)",
                                  "FILE - Medium (DC)", "MD5"])

# Populate the new DataFrame with the mapped values
output_df.loc[0] = ["SIP", df.iloc[0]["NAME"], "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""]
output_df.loc[1] = ["IE", "", df.iloc[0]["NAME"], "HBLL Special Collections", "Files archived and processed from " + df.iloc[0]["NAME"], "", "", "", identifier, rights, "", "", "", "", collection, "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""]
output_df.loc[2] = ["REP", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "true", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""]

# Start populating data from the fourth row (index 3) in the new DataFrame
for index, row in df.iterrows():
	if row["TYPE"] != "Folder" and row["NAME"] != ".DS_Store":
    	# For subsequent rows, use "FILE" as the Object Type
		file_path = row["FILE_PATH"].split(qualifier + '/')[1]  # Get the portion after "Qualifier"
		file_path = file_path.rsplit('/', 1)[0]  # Remove the filename at the end of the path
   		
		output_df.loc[index + 3] = ["File", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", row["LAST_MODIFIED"], "", "", "", "", "", "", file_path + '/', row["NAME"], row["SHA1_HASH"], "", "", "", "", "", row["NAME"], row["NAME"], "", "", "", "", "", ""]

# Save the mapped data to a new CSV file
output_df.to_csv(sys.argv[2], index=False)
