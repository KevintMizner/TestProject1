import pyodbc
import json
from datetime import datetime

# Database connection details
server = 'sql-wmsag'
database = 'ASCTracEDI856'
username = 'api_interface'
password = 'Z@7824_aPi'
conn_str = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'

# Log file for payloads
log_file = "payload_test.log"

# Facility code to include in the test (building 6 only)
allowed_facility_code = '06'

# Function to fetch data from the stored procedure
def fetch_data_from_sp():
    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        cursor.execute("EXEC [ASCTracEDI856].[dbo].[API_YMS_XRAY_GenerateJsonPayloadFromSnapshot]")
        rows = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        data = [dict(zip(columns, row)) for row in rows]
        return data
    except Exception as e:
        print(f"Error fetching data from stored procedure: {e}")
        return []
    finally:
        conn.close()

# Function to log POST and PUT payloads for testing
def log_payloads(data):
    with open(log_file, "w") as log:
        for record in data:
            appt_number = str(record['ApptNumber'])  # Ensure appt_number is a string
            ref_number = record['RefNumber']
            facility_code = record['FacilityCode']
            parts = json.loads(record['Parts']) if record['Parts'] != '[]' else []

            # Filter for building 6 only
            if facility_code != allowed_facility_code:
                print(f"Skipping Facility Code: {facility_code} (only building 6 is allowed)")
                continue

            # Properly format parts as a stringified JSON array
            parts_as_string = json.dumps(parts)  # Convert list to JSON string

            # Prepare POST payload
            post_payload = {
                "appt_number": appt_number,  # Ensured as a string
                "facility_code": facility_code,
                "ref_number": ref_number,
                "parts": parts_as_string  # Stringified JSON array as a string
            }

            post_payload_log = {
                "url": "https://allen.prd.ymshub.com/api/v2/load_info",
                "method": "POST",
                "headers": {
                    "Content-Type": "application/json",
                    "Authorization": "Bearer 7|ZPDSwXa5cyhF8OyrbHkK04RW6RTypI7dXnvcNRKD"
                },
                "body": post_payload  # Full JSON body
            }

            # Log POST payload
            log.write(json.dumps(post_payload_log, indent=2) + "\n\n")
            print(f"Logged POST Payload for RefNumber: {ref_number}")

            # Prepare PUT payload
            put_payload = {
                "facility_code": facility_code,
                "ref_number": ref_number,
                "parts": parts_as_string  # Stringified JSON array as a string
            }

            put_payload_log = {
                "url": f"https://allen.prd.ymshub.com/api/v2/load_info/{ref_number}",
                "method": "PUT",
                "headers": {
                    "Content-Type": "application/json",
                    "Authorization": "Bearer 7|ZPDSwXa5cyhF8OyrbHkK04RW6RTypI7dXnvcNRKD"
                },
                "body": put_payload  # Full JSON body
            }

            # Log PUT payload
            log.write(json.dumps(put_payload_log, indent=2) + "\n\n")
            print(f"Logged PUT Payload for RefNumber: {ref_number}")

# Main function to orchestrate the process
def main():
    # Step 1: Fetch data from the stored procedure
    data = fetch_data_from_sp()

    # Step 2: Display total number of records returned
    total_records = len(data)
    print(f"\nTotal records returned from stored procedure: {total_records}")

    # Step 3: Log the payloads for API testing (building 6 only)
    if total_records > 0:
        log_payloads(data)
    else:
        print("No records to process.")

if __name__ == "__main__":
    main()
