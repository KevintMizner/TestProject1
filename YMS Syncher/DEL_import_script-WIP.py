import pandas as pd
import pyodbc
from datetime import datetime
import logging

# Configure logging to print to both console and file
logging.basicConfig(filename='import_csv_to_sql.log', level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s: %(message)s')
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
console_handler.setFormatter(formatter)
logging.getLogger().addHandler(console_handler)

def import_csv_to_sql(csv_file: str) -> None:
    try:
        # Database connection details
        server = 'sql-wmsag'
        database = 'AD_Analysis'
        username = 'api_interface'
        password = 'Z@7824_aPi'

        logging.info("Connecting to the SQL Server...")
        # Create a connection to the SQL Server
        conn = pyodbc.connect(
            f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'
        )

        # Create a cursor from the connection
        cursor = conn.cursor()

        # Read the CSV file
        logging.info(f"Reading the CSV file: {csv_file}")
        df = pd.read_csv(csv_file)

        logging.debug(f"CSV file contains {df.shape[0]} rows and {df.shape[1]} columns.")
        logging.debug(f"CSV columns: {df.columns.tolist()}")

        # Ensure column names match the SQL table schema
        df.columns = [
            'Facility', 'Date', 'Requested By', 'Driver', 'Carrier Company', 'Scac',
            'Trailer Plate', 'Trailer #', 'Appt#', 'Customer', 'Load Type', 
            'Vehicle Type', 'Start Location', 'Start Spot', 'End Location', 
            'End Spot', 'Request Time', 'Time In Queue (Minutes)', 'Accept Time', 
            'Start Time', 'Complete Time', 'Elapsed Time (Minutes)', 'Priority Move',
            'Priority Load', 'Comments', 'Move Comments', 'Cancelled By', 
            'Cancelled Time', 'Decline Reason', 'Event', 'Username'
        ]

        logging.info("Renamed CSV columns to match SQL schema.")

        # Extract the date from the first record
        first_date = pd.to_datetime(df['Date'].iloc[0], errors='coerce').date()
        logging.info(f"Extracted date from first record: {first_date}")

        # Construct and print the exact SQL statement with the date value
        delete_query = f'''
            DELETE FROM [AD_Analysis].[Nova].[YMS_DriverEventLog]
            WHERE [Date] = '{first_date}'
        '''
        logging.info(f"Executing SQL: {delete_query}")

        # Execute the delete query
        cursor.execute(delete_query)
        conn.commit()

        logging.info(f"Records for {first_date} deleted successfully.")

        # Now, process each row in the CSV and insert it into the database
        def safe_convert(value, data_type, column_name, row_index):
            try:
                if pd.isnull(value) or value == '':
                    return None
                if data_type == 'date':
                    return pd.to_datetime(value, errors='coerce').date()
                elif data_type == 'time':
                    return pd.to_datetime(value, errors='coerce').time()
                elif data_type == 'datetime':
                    return pd.to_datetime(value, errors='coerce')
                elif data_type == 'int':
                    return int(value) if pd.notnull(value) else 0
                elif data_type == 'float':
                    return float(value) if pd.notnull(value) else 0.0
                elif data_type == 'str':
                    return str(value)
            except ValueError as e:
                logging.error(f"Error converting value '{value}' for column '{column_name}' in row {row_index}: {e}")
                return None

        # Insert data into the Nova.YMS_DriverEventLog table
        for index, row in df.iterrows():
            try:
                logging.debug(f"Processing row {index+1} of {df.shape[0]}...")

                # Create the row tuple
                row_tuple = (
                    safe_convert(row['Facility'], 'str', 'Facility', index),
                    safe_convert(row['Date'], 'date', 'Date', index),
                    safe_convert(row['Requested By'], 'str', 'Requested By', index),
                    safe_convert(row['Driver'], 'str', 'Driver', index),
                    safe_convert(row['Carrier Company'], 'str', 'Carrier Company', index),
                    safe_convert(row['Scac'], 'str', 'Scac', index),
                    safe_convert(row['Trailer Plate'], 'str', 'Trailer Plate', index),
                    safe_convert(row['Trailer #'], 'str', 'Trailer #', index),
                    safe_convert(row['Appt#'], 'int', 'Appt#', index),
                    safe_convert(row['Customer'], 'str', 'Customer', index),
                    safe_convert(row['Load Type'], 'str', 'Load Type', index),
                    safe_convert(row['Vehicle Type'], 'str', 'Vehicle Type', index),
                    safe_convert(row['Start Location'], 'str', 'Start Location', index),
                    safe_convert(row['Start Spot'], 'str', 'Start Spot', index),
                    safe_convert(row['End Location'], 'str', 'End Location', index),
                    safe_convert(row['End Spot'], 'str', 'End Spot', index),
                    safe_convert(row['Request Time'], 'time', 'Request Time', index),
                    safe_convert(row['Time In Queue (Minutes)'], 'float', 'Time In Queue (Minutes)', index),
                    safe_convert(row['Accept Time'], 'time', 'Accept Time', index),
                    safe_convert(row['Start Time'], 'time', 'Start Time', index),
                    safe_convert(row['Complete Time'], 'time', 'Complete Time', index),
                    safe_convert(row['Elapsed Time (Minutes)'], 'float', 'Elapsed Time (Minutes)', index),
                    safe_convert(row['Priority Move'], 'str', 'Priority Move', index),
                    safe_convert(row['Priority Load'], 'str', 'Priority Load', index),
                    safe_convert(row['Comments'], 'str', 'Comments', index),
                    safe_convert(row['Move Comments'], 'str', 'Move Comments', index),
                    safe_convert(row['Cancelled By'], 'str', 'Cancelled By', index),
                    safe_convert(row['Cancelled Time'], 'time', 'Cancelled Time', index),
                    safe_convert(row['Decline Reason'], 'str', 'Decline Reason', index),
                    safe_convert(row['Event'], 'str', 'Event', index),
                    safe_convert(row['Username'], 'str', 'Username', index)
                )

                logging.debug(f"Row tuple for row {index+1}: {row_tuple}")
                logging.debug(f"Row tuple length: {len(row_tuple)}")

                # Ensure 31 placeholders for each value in the row
                cursor.execute('''
                    INSERT INTO Nova.YMS_DriverEventLog (
                        Facility, [Date], [Requested By], Driver, [Carrier Company], Scac, 
                        [Trailer Plate], [Trailer #], [Appt#], Customer, [Load Type], 
                        [Vehicle Type], [Start Location], [Start Spot], [End Location], 
                        [End Spot], [Request Time], [Time In Queue (Minutes)], [Accept Time], 
                        [Start Time], [Complete Time], [Elapsed Time (Minutes)], [Priority Move], 
                        [Priority Load], Comments, [Move Comments], [Cancelled By], [Cancelled Time], 
                        [Decline Reason], Event, Username
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', row_tuple)

                logging.debug(f"Row {index+1} inserted successfully.")
            except Exception as e:
                logging.error(f"Error inserting row {index+1}: {e}")
                continue

        # Commit the transaction
        logging.info("Committing transaction...")
        conn.commit()

        # Check if any records were inserted
        cursor.execute("SELECT COUNT(*) FROM Nova.YMS_DriverEventLog")
        row_count = cursor.fetchone()[0]
        logging.info(f"Total rows in Nova.YMS_DriverEventLog after insert: {row_count}")

        # Close the cursor and connection
        cursor.close()
        conn.close()
        logging.info('SQL import completed successfully')

    except Exception as e:
        logging.error(f"An error occurred during the import process: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    csv_file = 'downloads/2024-10-22T11_25_39.801Z_new_driver_history (3).csv'
    logging.info(f"Starting import for {csv_file}")
    import_csv_to_sql(csv_file)
