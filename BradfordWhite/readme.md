

# Bradford White Watchdog Script for CSV to JSON Processing and API Calls

## Purpose

To notify Bradford White in real-time if an order/update has been accepted or rejected, along with a reason code.

## General Description

-  This project involves a Python script that monitors a specified directory for new CSV files, processes them to create JSON payloads, and sends the payloads to an API endpoint at Bradford White. The script also moves the processed files to a "processed" directory and logs the processing events.

- When an order is received, RAMP will inspect the incoming order and determine whether or not the order will be processed.

## There are several reasons that an update to an existing order will be rejected in ASC:

```
'B': 'B - Being Picked', 'C': 'C - Closed', 'D': 'D - On Truck',
'G': 'G - Truck', 'H': 'H - Credit Hold', 'I': 'I - Short Inventory',
'K': 'K - Pick Hold', 'L': 'L - On Loading Dock', 'O': 'O - Pick Complete-In Transit', 
'P': 'P - Partial Pick', 'S': 'S - Scheduled', 'X': 'X - Cancelled'
```

For any of these status codes, a CSV file will be generated and placed in the directory:
```
\\allen-files\edi\ASC\BRAWHI-ORDER-STATUS
```


An example filename: `922989660C.csv

```csv
922989660,585507,,,35514,,C
922989660,585507,,,35514,,C
922989660,585507,,,35514,,C
```

This file will be converted to JSON:

```json
{
    "executionId": "35514",
    "deliveryId": "922989660",
    "processStatus": 0,
    "errorMessage": "C - Closed"
}
```

and submitted to Bradford White's system via the endpoint:

```
https://oicproduction-bradfordwhiteoic.integration.ocp.oraclecloud.com:443/ic/api/integration/v1/flows/rest/BWC_AD_CUSTOM_ORDER_RECEIP/1.0/T3Receipt
```

## Table of Contents

- [Summary](#summary)
- [Setup](#setup)
- [Usage](#usage)
- [Technical Details](#technical-details)
- [Contact](#contact)

## Summary

This script is designed to automate the process of monitoring a directory for new CSV files, processing them to extract specific information, and sending this information to an API endpoint. The script performs the following tasks:
1. Monitors a specified directory for new CSV files.
2. Reads and processes each CSV file to create a JSON payload.
3. Sends the JSON payload to a specified API endpoint.
4. Moves the processed CSV and JSON files to a "processed" directory.
5. Logs each processing event with relevant details.

## Setup

To set up the script, follow these steps:

1. Clone this repository to your local machine.
2. Navigate to the project directory.
3. Create a virtual environment:
   ```bash
   python -m venv venv
   ```
4. Activate the virtual environment:
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```
5. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

### Python Version

This script requires Python 3.7 or higher. Ensure you have the correct version installed by running:

```bash
python --version
```

## Usage

To run the script, make sure your virtual environment is activated and then execute the script:

```bash
python api_status_reply.py
```

The script will start monitoring the specified directory for new CSV files and process them as described in the summary.

## Technical Details

Make sure that the script has read/write/update/delete access on the directory:

```
\\allen-fs\EDI\ASC\BRAWHI-ORDER-STATUS
```

### Script Functionality

- **File Monitoring**: The script uses the `watchdog` library to monitor a specified directory for new CSV files. When a new file is detected, it triggers the processing function.
- **CSV Processing**: The script reads each CSV file, extracts specific fields, and constructs a JSON payload based on these fields.
- **API Integration**: The constructed JSON payload is sent to a predefined API endpoint using the `requests` library.
- **File Management**: After processing, the CSV and JSON files are moved to a "processed" directory.
- **Logging**: Each processing event is logged with a timestamp, filename, payload, and response code.

### Requirements

The script requires the following Python packages, specified in `requirements.txt`:
- `watchdog`
- `requests`

### Execution

The script should be executed from within the virtual environment to ensure all dependencies are correctly resolved. Here are the steps to run the script:

1. Activate the virtual environment:
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```
2. Run the script:
   ```bash
   python api_status_reply.py
   ```

### Error Handling

The script includes error handling for:
- Locked files: Retries file access multiple times if the file is locked.
- JSON processing: Catches and logs any JSON decoding errors.
- API communication: Logs the response code and any errors from the API call.

## Contact

Contact EDISupport@allendistribution.com for support. 

This `README.md` provides both a layman's summary and a section with technical details, including instructions on setting up and running the script from a virtual environment.
```

This version should render correctly on most Markdown editors and viewers. If you still face issues, please let us know the specific rendering problem you're encountering.