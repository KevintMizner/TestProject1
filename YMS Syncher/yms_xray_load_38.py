import pyodbc
import json
import requests
from datetime import datetime, timedelta
import time

# Database connection details
server = 'sql-wmsag'
database = 'ASCTracEDI856'
username = 'api_interface'
password = 'Z@7824_aPi'
conn_str = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'

# API details
api_endpoint = "https://allen.prd.ymshub.com/api/v2/load_info"
api_headers = {
    "Authorization": "Bearer 7|ZPDSwXa5cyhF8OyrbHkK04RW6RTypI7dXnvcNRKD",
    "Content-Type": "application/json",
    "Accept": "application/json"
}

# Log file
log_file = "api_calls.log"

# Database connection
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

# Lists to keep track of transactions
successful_transactions = []
failed_transactions = []
skipped_records = []

# Step 1: Execute the provided query to get appointment details
query = """
SELECT 
      [Appt_Num]
      ,[Appt_Type]
      ,[Ref_1]
      ,[Ref_2]
      ,[Facility]
      ,[Load_Type]
      ,[Open_Dock_Appt_Id]
      ,[Download_Timestamp]
      ,[Customer]
      ,[Appt_Date]
      ,[Appt_Time]
      ,[Arrival_Time]
      ,[Time_In_Yard_Hrs]
      ,[Location]
      ,[Open_Dock_Appt_Id]
      ,[Download_Timestamp]
  FROM [AD_Analysis].[Nova].[YMS_InventorySnapshot]
  WHERE Appt_Type = 'inbound'
  AND Trailer_Status IN ('loaded','unloading')
  AND load_type IN ('Shuttle', 'bulk', 'Floor Load')
  AND LEN(ref_1) > 5 
  AND Facility IN ('Building 38')  -- Modified line to include both buildings
  ORDER BY ref_1 DESC
"""
cursor.execute(query)
rows = cursor.fetchall()

for row in rows:
    po_number = row.Ref_1
    confirmation_number = row.Appt_Num
    building_id = row.Facility[-2:]  # Extract the rightmost two characters
    print (f"{building_id}")

    # Check if building_id is either '38' or '72'
    if building_id in ['38']:
        # Apply the refnum processing logic (uncomment if needed)
        # if not po_number.startswith("BW") and po_number[0].isdigit():
        #     po_number = "BW" + po_number

        print(f"PO Number: {po_number}, Confirmation Number: {confirmation_number}, Building ID: {building_id}")

        # Call the stored procedure using the correct database
        cursor.execute("{CALL API_YMS_XRAY_GenerateJsonPayload_bldg38 (?, ?, ?)}", 
                       po_number, confirmation_number, building_id)
        result = cursor.fetchone()

        if not result or not result[3]:
            skipped_records.append((po_number, confirmation_number, building_id))
            print(f"Insufficient data for PO Number: {po_number}, Confirmation Number: {confirmation_number}, Building ID: {building_id}")

            # Log the skipped record
            with open(log_file, "a") as log:
                log_entry = {
                    "timestamp": datetime.now().isoformat(),
                    "po_number": po_number,
                    "confirmation_number": confirmation_number,
                    "building_id": building_id,
                    "message": "API was not made - No JSON"
                }
                log.write(json.dumps(log_entry) + "\n")
            continue

        ref_number, appt_number, facility_code, json_output = result
        print(f"Stored Procedure Result - Ref Number: {ref_number}, Appt Number: {appt_number}, Facility Code: {facility_code}, JSON Output: {json_output}")

        if json_output:
            # Convert JSON output to a list of dictionaries, ensuring qty is a string
            parts = json.loads(json_output)
            for part in parts:
                part["qty"] = str(part["qty"])  # Convert qty to string

            # Convert the parts back to a JSON string
            json_output = json.dumps(parts)
            # Prepare the payload with the exact JSON string for POST
            post_payload = {
                "appt_number": appt_number,
                "facility_code": facility_code,
                "ref_number": ref_number,
                "parts": json_output  # Use the JSON string directly
            }

            # Print the exact JSON string being submitted for POST
            print(f"Exact JSON Payload for POST: {json.dumps(post_payload)}")

            # Make the POST API call
            response = requests.post(api_endpoint, headers=api_headers, data=json.dumps(post_payload))

            # Check if response is valid JSON
            try:
                response_data = response.json()
            except requests.exceptions.JSONDecodeError:
                response_data = response.text

            if response.status_code == 200:
                # Log the successful POST request
                successful_transactions.append({
                    "method": "POST",
                    "ref_number": ref_number,
                    "appt_number": appt_number,
                    "building_id": building_id,
                    "json_output": json_output,
                    "response_status": response.status_code,
                    "response_data": response_data
                })
                print(f"POST API Call Success - Status Code: {response.status_code}, Data: {response_data}")
            else:
                failure_reason = "POST failed"
                if response.status_code == 422 and 'ref_number' in response_data.get('errors', {}) and response_data['errors']['ref_number'] == ['The ref number has already been taken.']:
                    print("Ref number already taken, attempting PUT request...")
                    put_endpoint = f"{api_endpoint}/{ref_number}"
                    put_payload = {
                        "facility_code": facility_code,
                        "ref_number": ref_number,
                        "parts": json_output  # Use the JSON string directly
                    }

                    # Print the exact JSON string being submitted for PUT
                    print(f"PUT URL: {put_endpoint}")
                    print(f"Exact JSON Payload for PUT: {json.dumps(put_payload)}")

                    # Make the PUT API call
                    response = requests.put(put_endpoint, headers=api_headers, data=json.dumps(put_payload))

                    # Handle 204 No Content as success
                    if response.status_code == 204:
                        response_data = 'No Content'

                    # Check if response is valid JSON
                    try:
                        response_data = response.json()
                    except requests.exceptions.JSONDecodeError:
                        response_data = response.text

                    if response.status_code == 200 or response.status_code == 204:
                        # Log the successful PUT request
                        successful_transactions.append({
                            "method": "PUT",
                            "ref_number": ref_number,
                            "appt_number": appt_number,
                            "building_id": building_id,
                            "json_output": json_output,
                            "response_status": response.status_code,
                            "response_data": response_data
                        })
                    else:
                        # Log the failed PUT request
                        failed_transactions.append({
                            "method": "PUT",
                            "ref_number": ref_number,
                            "appt_number": appt_number,
                            "building_id": building_id,
                            "json_output": json_output,
                            "response_status": response.status_code,
                            "response_data": response_data,
                            "failure_reason": "PUT failed after POST failed"
                        })

                    print(f"PUT API Call Response - Status Code: {response.status_code}, Data: {response_data}")

                else:
                    # Log the failed POST request
                    failed_transactions.append({
                        "method": "POST",
                        "ref_number": ref_number,
                        "appt_number": appt_number,
                        "building_id": building_id,
                        "json_output": json_output,
                        "response_status": response.status_code,
                        "response_data": response_data,
                        "failure_reason": failure_reason
                    })

                print(f"POST API Call Response - Status Code: {response.status_code}, Data: {response_data}")

            # Log the API call
            with open(log_file, "a") as log:
                log_entry = {
                    "timestamp": datetime.now().isoformat(),
                    "method": "PUT" if response.status_code == 200 or response.status_code == 204 else "POST",
                    "ref_number": ref_number,
                    "appt_number": appt_number,
                    "building_id": building_id,
                    "json_output": json_output,
                    "payload": put_payload if response.status_code == 200 or response.status_code == 204 else post_payload,
                    "response_status": response.status_code,
                    "response_data": response_data,
                    "message": "Successful API call" if response.status_code == 200 or response.status_code == 204 else "API call failed"
                }
                log.write(json.dumps(log_entry) + "\n")

        else:
            skipped_records.append((po_number, confirmation_number, building_id))
            print(f"Insufficient data for PO Number: {po_number}, Confirmation Number: {confirmation_number}, Building ID: {building_id}")

            # Log the skipped record
            with open(log_file, "a") as log:
                log_entry = {
                    "timestamp": datetime.now().isoformat(),
                    "po_number": po_number,
                    "confirmation_number": confirmation_number,
                    "building_id": building_id,
                    "message": "API was not made - No JSON"
                }
                log.write(json.dumps(log_entry) + "\n")
    else:
        print(f"Building ID {building_id} is not 38 or 72. Skipping...")

# Print the list of successful transactions
print("\nSuccessful Transactions:")
for transaction in successful_transactions:
    print(f"Method: {transaction['method']}, Ref Number: {transaction['ref_number']}, Appt Number: {transaction['appt_number']}, Building ID: {transaction['building_id']}")

# Print the list of failed transactions
print("\nFailed Transactions:")
for transaction in failed_transactions:
    print(f"Method: {transaction['method']}, Ref Number: {transaction['ref_number']}, Appt Number: {transaction['appt_number']}, Building ID: {transaction['building_id']}, Reason: {transaction['failure_reason']}")

# Print and log skipped records
if skipped_records:
    print("\nSkipped Records:")
    for record in skipped_records:
        print(f"PO Number: {record[0]}, Confirmation Number: {record[1]}, Building ID: {record[2]} - API was not made - No JSON")

    with open(log_file, "a") as log:
        log.write("\nSkipped Records:\n")
        for record in skipped_records:
            log.write(f"PO Number: {record[0]}, Confirmation Number: {record[1]}, Building ID: {record[2]} - API was not made - No JSON\n")

# Close connection
cursor.close()
conn.close()
