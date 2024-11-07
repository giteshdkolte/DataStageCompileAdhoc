import yaml
import os, sys
import subprocess
from colorama import Fore, Style, init
from tqdm import tqdm
import re

# Initialize colorama on Windows
init()
# Read YAML data from configurations.yaml
with open(r'..\config\configurations.yml', 'r') as file:
    yaml_data = yaml.safe_load(file)
# Access assetDependencies from 'datastageLegacy'
asset_dependencies = yaml_data.get('datastageLegacy', {}).get('assetDependencies', '')
# Access other keys in 'datastageLegacy'
dataDS = yaml_data.get('datastageLegacy', {})
# Extract variables dynamically
classicPath = dataDS['classicPath']
isUser = dataDS['isUser']
isPwd = dataDS['isPwd']
isDomain = dataDS['isDomain']
host = dataDS['host']
isProject = dataDS['isProject']
csv_file_path = dataDS['compileJobListTXT']
statusPath = dataDS['statusPath']
statusFileCompileAdhoc = dataDS['statusFileCompileAdhoc']
statusFile = os.path.join(statusPath, f'{isProject}{statusFileCompileAdhoc}.csv')

def check_and_create_folder(folder_path):
    # Create status file path if doesnot exists
    os.makedirs(folder_path, exist_ok=True)

def status_update(master_asset, status, comment):
    with open(statusFile, 'a') as output:
        output.write(f"{master_asset}|{status}|{comment}\n")

def doCompileFunc(master_asset, assetType):
    # Check if the asset type is a job or a routine
    typeParameter = None
    if (assetType == 'routine'):
        typeParameter = 'r'
    elif (assetType == 'job'):
        typeParameter = 'j'
    else:
        print("The compile code only supports job and routine.")
        status = "Skipped"
        comment = "The compile code only supports job and routine. Please give either 'job' or 'routine' in input file"
        status_update(master_asset, status, comment)
        return
    
    # Call the ds_compile_command script with dependent_asset_name as an argument
    # Construct the command for job
    ds_compile_command = [
        f"{classicPath}\\dscc.exe",
		"/h",f"{host}",
        "/u",f"{isUser}",
        "/p",f"{isPwd}",
        f"{isProject}",
        f"/{typeParameter}",f"{master_asset}"
        ]
    
    try:
        result = subprocess.run(ds_compile_command, shell=True, 
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # Get the standard output
        output = result.stdout
        
        # If the login creds fails to establish a connection
        if "Logon Failed" in output:
            pattern = r"(?s)Initializing\s*Logon Failed\s-\s.+?\n(.+?)\n"

            match = re.search(pattern, output)
            if match:
                status = "Failed"
                comment = match.group(1).strip().replace("\n", ". ")
                status_update(master_asset, status, comment)
        # Get the success or failed status of compiling the job
        else:
            pattern = r"(?s)Initializing\s*(?:Compiling)?\s*\".+?\"\s*-?\s*(.+?)\n(.+?)\d+\s+Items Processed\s*Done"
            
            match = re.search(pattern, output)
            if match:
                status = match.group(1).strip()
                comment = match.group(2).strip().replace("\n", " ")
                status_update(master_asset, status, comment)

    except subprocess.CalledProcessError as e:
        # Access the standard error from the exception
        error_output = e.stderr
        # Optionally, you can also call status_update here if needed
        status_update(master_asset, "Failed", error_output.strip())

def check_master_asset(csv_file_path):
    try:
        with open(csv_file_path, 'r', newline='') as csv_file:
            with open(statusFile, 'w') as output:
                fieldnames = ['Asset', 'Status', 'Comment']
                output.write(f"{'|'.join(fieldnames)}\n")

            assetLst = [line.strip() for line in csv_file.readlines() if line.strip()]
            if assetLst:
                with tqdm(total=len(assetLst), bar_format='{desc} {percentage:3.0f}%|{bar:60}') as pbar:
                    for idx, asset in enumerate(assetLst, start=1):
                        assetType, master_asset = asset.split(',')
                        # Setting tqdm description
                        pbar.set_description(f"Compile initializing for {Fore.YELLOW}{master_asset}{Style.RESET_ALL} [{idx}/{len(assetLst)}]")
                        # Call get_dep_asset function to get dependentAsset
                        doCompileFunc(master_asset.strip(), assetType.strip())
                        pbar.update()
                print(f"Compile process completed. Please refer to the status file path {Fore.GREEN}{statusFile}{Style.RESET_ALL}.")
            else:
                print(f"INPUT CSV FILE {Fore.RED}{csv_file_path}{Style.RESET_ALL} EMPTY")
    except FileNotFoundError:
        print(f"Error: Input CSV file not found - {Fore.RED}{csv_file_path}{Style.RESET_ALL}")
    except Exception as e:
        print(f"Error: {e}")

# Main calling
print(f"Input File Path: {Fore.YELLOW} {csv_file_path}{Style.RESET_ALL}") 
check_master_asset(csv_file_path)
