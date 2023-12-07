import requests
import os
import sys
import json
from datetime import datetime
from dateutil import parser as date_parser
from urllib.parse import urlparse

with open(sys.argv[1]) as json_data:
    data = json.load(json_data)
    
cs_dir = 'Consent Forms'
if not os.path.isdir(cs_dir):
    os.mkdir(cs_dir)
sub_dir = 'Submissions'
if not os.path.isdir(sub_dir):
    os.mkdir(sub_dir)

# Download file from URL
def download_files(url, filename):
    response = requests.get(url)
    modified_header = response.headers.get('Last-Modified')

# Maintain date stamps from original upload to AirTable
    if modified_header:
        modified_datetime = date_parser.parse(modified_header)
        modified_timestamp = modified_datetime.timestamp()
    else:
        modified_timestamp = None
    
    response = requests.get(url, stream=True)
    response.raise_for_status()

    with open(filename, "wb") as file:
            file.write(response.content)
            os.utime(filename, (modified_timestamp, modified_timestamp))
            
      
for entry in data:
	if 'export' in entry:
		continue
	consent_forms = entry.get("Consent Forms", [])
	identifier = entry["Identifier"]
	for form in consent_forms:
		filename = form.get("filename")
		url = form.get("url")
		if entry.get("Export") == True:
			download_files(url, "Consent Forms/" + identifier + "_" + filename)
			print(f"Downloaded: {filename}")
	submission = entry.get("Submission", [])
	for form in submission:
		filename = form.get("filename")
		url = form.get("url")
		if entry.get("Export") == True:
			download_files(url, "Submissions/" + identifier + "_" + filename)
			print(f"Downloaded: {filename}")