import pyodbc
import json
import requests
from datetime import datetime

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

# Step 1: Execute the query to get appointment details
query = """
SELECT 
    [Appt_Num],
    [Customer],
    [Facility],
    [Ref_1],
    [Trailer_Status]
FROM [AD_Analysis].[Nova].[YMS_InventorySnapshot]
WHERE 
    Customer LIKE '%knouse%' 
    AND Ref_1 IS NOT NULL
    AND (Trailer_Status LIKE '%loaded%' OR Trailer_Status LIKE '%loading%')
"""
cursor.execute(query)
rows = cursor.fetchall()

for row in rows:
    po_number = str(row.Ref_1)  # Ensure po_number is a string
    confirmation_number = str(row.Appt_Num)  # Ensure confirmation_number is a string
    # building_id = row.Facility[-2:]  # Extract the rightmost two characters
    building_id = '0614'  # Assign as a string directly
    custid = str(row.Customer)  # Ensure custid is a string

    print(f"Building ID: {building_id}")

    # Check if building_id is valid
    if building_id in ['0614']:
        print(f"Processing PO Number: {po_number}, Confirmation Number: {confirmation_number}, Building ID: {building_id}")
        # Call the stored procedure
        cursor.execute("{CALL API_YMS_Inbound_LookupV2(?, ?)}", custid, po_number)
        result = cursor.fetchone()

        if not result or not result[0]:
            skipped_records.append((po_number, confirmation_number, building_id))
            print(f"No JSON returned for PO Number: {po_number}, Confirmation Number: {confirmation_number}, Building ID: {building_id}")
            continue

        json_output = result[0]  # Extract the JSON string
        print(f"Stored Procedure JSON Output: {json_output}")

        try:
            # Parse the JSON output
            parts = json.loads(json_output)
            for part in parts:
                part["qty"] = str(part["qty"])  # Convert quantity to string if required

            # Prepare the API payload
            post_payload = {
                "appt_number": confirmation_number,
                "facility_code": building_id,
                "ref_number": po_number,
                "parts": parts
            }

            print(f"API Payload: {json.dumps(post_payload, indent=2)}")

            # Make the POST API call
            response = requests.post(api_endpoint, headers=api_headers, json=post_payload)

            if response.status_code == 200:
                print(f"POST Successful: {response.status_code}, Response: {response.json()}")
                successful_transactions.append(post_payload)
            else:
                print(f"POST Failed: {response.status_code}, Response: {response.text}")
                failed_transactions.append({
                    "payload": post_payload,
                    "response_status": response.status_code,
                    "response_data": response.text
                })

        except json.JSONDecodeError as e:
            print(f"Error parsing JSON for PO Number: {po_number}: {e}")
            skipped_records.append((po_number, confirmation_number, building_id))
            continue
    else:
        print(f"Building ID {building_id} is not valid. Skipping...")

# Print the list of successful transactions
print("\nSuccessful Transactions:")
for transaction in successful_transactions:
    print(json.dumps(transaction, indent=2))

# Print the list of failed transactions
print("\nFailed Transactions:")
for transaction in failed_transactions:
    print(json.dumps(transaction, indent=2))

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
