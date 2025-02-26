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
    generated_payloads = []

    for record in data:
        appt_number = record['ApptNumber']
        ref_number = record['RefNumber']
        facility_code = record['FacilityCode']
        parts = json.loads(record['Parts']) if record['Parts'] != '[]' else []

        # Prepare POST payload
        post_payload = {
            "appt_number": appt_number,
            "facility_code": facility_code,
            "ref_number": ref_number,
            "parts": parts
        }

        # Log POST payload
        post_payload_log = {
            "url": "https://allen.prd.ymshub.com/api/v2/load_info",
            "method": "POST",
            "headers": {
                "Content-Type": "application/json",
                "Authorization": "Bearer 7|ZPDSwXa5cyhF8OyrbHkK04RW6RTypI7dXnvcNRKD"
            },
            "body": post_payload
        }
        generated_payloads.append(post_payload_log)

        # Prepare PUT payload and URL if ref_number already exists
        put_payload = {
            "facility_code": facility_code,
            "ref_number": ref_number,
            "parts": parts
        }
        put_payload_log = {
            "url": f"https://allen.prd.ymshub.com/api/v2/load_info/{ref_number}",
            "method": "PUT",
            "headers": {
                "Content-Type": "application/json",
                "Authorization": "Bearer 7|ZPDSwXa5cyhF8OyrbHkK04RW6RTypI7dXnvcNRKD"
            },
            "body": put_payload
        }
        generated_payloads.append(put_payload_log)

    # Write all payloads to a log file
    with open(log_file, "w") as log:
        for payload in generated_payloads:
            log.write(json.dumps(payload, indent=2) + "\n")
            log.write("\n")

    # Print payloads for debugging
    print("\nGenerated Payloads for Postman Testing:")
    for payload in generated_payloads:
        print(json.dumps(payload, indent=2))

# Main function to orchestrate the process
def main():
    data = fetch_data_from_sp()
    if data:
        log_payloads(data)
    else:
        print("No data returned from stored procedure.")

if __name__ == "__main__":
    main()
