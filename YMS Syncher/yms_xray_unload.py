import pyodbc
import requests
import json
import os
from datetime import datetime, timedelta

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

# Log file details
log_file = "xray_unload_api_calls.log"
purge_interval = timedelta(hours=1)  # Set the purge interval to 1 hour

# Function to check and purge log file
def check_and_purge_log_file(log_file):
    if os.path.exists(log_file):
        file_mod_time = datetime.fromtimestamp(os.path.getmtime(log_file))
        if datetime.now() - file_mod_time > purge_interval:
            # Archive the old log file (optional)
            os.rename(log_file, log_file.replace(".log", f"_{file_mod_time.strftime('%Y%m%d%H%M%S')}.log"))
            # Create a new log file
            with open(log_file, "w") as log:
                log.write("")

# Function to execute the main logic
def main():
    # Check and purge log file if necessary
    check_and_purge_log_file(log_file)

    # Database connection
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()

    # Lists to keep track of transactions
    successful_transactions = []
    failed_transactions = []

    # Step 1: Execute the provided query to get appointment details
    query = """
    SELECT TOP 1000
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
      AND Trailer_Status = 'empty'
      AND load_type IN ('Shuttle', 'bulk', 'Floor Load')

    """
    cursor.execute(query)
    rows = cursor.fetchall()

    for row in rows:
        ref_number = row.Ref_1
        confirmation_number = row.Appt_Num
        building_id = row.Facility[-2:]  # Extract the rightmost two characters

        print(f"Ref Number: {ref_number}, Confirmation Number: {confirmation_number}, Building ID: {building_id}")

        # Prepare the payload for the PUT request
        put_payload = {
            "facility_code": building_id,
            "ref_number": ref_number,
            "parts": "[]"  # This will remove any load details
        }

        # Print the exact JSON string being submitted for PUT
        print(f"Exact JSON Payload for PUT: {json.dumps(put_payload)}")

        # Make the PUT API call
        put_endpoint = f"{api_endpoint}/{ref_number}"
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
                "confirmation_number": confirmation_number,
                "building_id": building_id,
                "json_output": "[]",
                "response_status": response.status_code,
                "response_data": response_data
            })
            print(f"PUT API Call Success - Status Code: {response.status_code}, Data: {response_data}")
        else:
            # Log the failed PUT request
            failed_transactions.append({
                "method": "PUT",
                "ref_number": ref_number,
                "confirmation_number": confirmation_number,
                "building_id": building_id,
                "json_output": "[]",
                "response_status": response.status_code,
                "response_data": response_data,
                "failure_reason": "PUT failed"
            })
            print(f"PUT API Call Failure - Status Code: {response.status_code}, Data: {response_data}")

        # Log the API call
        with open(log_file, "a") as log:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "method": "PUT",
                "ref_number": ref_number,
                "confirmation_number": confirmation_number,
                "building_id": building_id,
                "json_output": "[]",
                "payload": put_payload,
                "response_status": response.status_code,
                "response_data": response_data,
                "message": "Successful API call" if response.status_code == 200 or response.status_code == 204 else "API call failed"
            }
            log.write(json.dumps(log_entry) + "\n")

    # Print the list of successful transactions
    print("\nSuccessful Transactions:")
    for transaction in successful_transactions:
        print(f"Method: {transaction['method']}, Ref Number: {transaction['ref_number']}, Confirmation Number: {transaction['confirmation_number']}, Building ID: {transaction['building_id']}")

    # Print the list of failed transactions
    print("\nFailed Transactions:")
    for transaction in failed_transactions:
        print(f"Method: {transaction['method']}, Ref Number: {transaction['ref_number']}, Confirmation Number: {transaction['confirmation_number']}, Building ID: {transaction['building_id']}, Reason: {transaction['failure_reason']}")

    # Close connection
    cursor.close()
    conn.close()

# Main entry point
if __name__ == "__main__":
    main()
