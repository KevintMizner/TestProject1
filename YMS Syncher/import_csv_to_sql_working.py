import pandas as pd
import pyodbc
from datetime import datetime
import logging
import re

# Configure logging
logging.basicConfig(
    filename='import_csv_to_sql.log',
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s: %(message)s'
)

def determine_facility(location: str, default_facility: str) -> str:
    """
    Determines the Facility value based on rules applied to the Location (end spot).
    Prints the return value to the console.
    """
    try:
        if not isinstance(location, str):
            result = default_facility
            print(f"Location: {location}, Default Facility: {result}")
            return result

        # Find all occurrences of 'Docks-' or 'Yard-' with their following two digits
        matches = re.findall(r'(Docks-|Yard-)(\d{2})', location)

        for prefix, code in matches:
            # Apply rules based on the two-digit code immediately following 'Docks-' or 'Yard-'
            if code in ['03', '04']:
                result = "Building 03"
            elif code in ['02', '01']:
                result = "Building 01"
            elif code == '05':
                result = "Building 05"
            elif code == '14':
                result = "Building 14"
            elif code == '06':
                result = "Building 06"
            else:
                continue

            # Print and return as soon as a matching rule is found
            print(f"Location: {location}, Determined Facility: {result}")
            return result

        # Handle special case for '1-5' with 'LOT' or 'Lot'
        if '1-5' in location and ('LOT' in location or 'Lot' in location):
            result = "Drop Lot"
            print(f"Location: {location}, Determined Facility: {result}")
            return result

        # Default facility if no matches are found
        result = default_facility
        print(f"Location: {location}, Default Facility: {result}")
        return result
    except Exception as e:
        logging.error(f"Error determining facility for location '{location}': {e}")
        print(f"Error determining facility for location '{location}': {e}")
        return default_facility

def safe_convert(value, data_type, column_name, row_index):
    """
    Converts and validates data types for SQL insertion. Handles NaN and missing values.
    """
    try:
        if pd.isnull(value) or value == '':
            return None  # Return None for SQL NULL

        if data_type == 'date':
            return pd.to_datetime(value, errors='coerce').date()
        elif data_type == 'time':
            return pd.to_datetime(value, errors='coerce').time()
        elif data_type == 'datetime':
            return pd.to_datetime(value, errors='coerce')
        elif data_type == 'int':
            return int(value) if pd.notnull(value) else None
        elif data_type == 'float':
            return float(value) if pd.notnull(value) else None
        elif data_type == 'str':
            return str(value)
    except ValueError as e:
        logging.error(f"Error converting value '{value}' for column '{column_name}' in row {row_index}: {e}")
        print(f"Error converting value '{value}' for column '{column_name}' in row {row_index}: {e}")
        return None

def import_csv_to_sql(csv_file: str) -> None:
    try:
        # Database connection details
        server = 'sql-wmsag'
        database = 'AD_Analysis'
        username = 'api_interface'
        password = 'Z@7824_aPi'

        logging.info("Connecting to the SQL Server...")
        conn = pyodbc.connect(
            f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'
        )
        cursor = conn.cursor()

        # Clear the YMS_InventorySnapshot table
        logging.info("Clearing the YMS_InventorySnapshot table...")
        cursor.execute('DELETE FROM Nova.YMS_InventorySnapshot')
        conn.commit()

        # Read the CSV file
        logging.info(f"Reading the CSV file: {csv_file}")
        df = pd.read_csv(csv_file, header=0)

        if df.empty:
            logging.warning("CSV file is empty. No records to process.")
            return

        # Drop the "Pictures" column if it exists
        if 'Pictures' in df.columns:
            df.drop(columns=['Pictures'], inplace=True)
            logging.info("Dropped the 'Pictures' column from the DataFrame")

        # Rename columns to match SQL table schema
        df.columns = [
            'Appt_Date', 'Appt_Time', 'Arrival_Time', 'Time_In_Yard_Hrs', 'Appt_Num', 'Appt_Type',
            'Customer', 'Scac', 'Trailer_Num', 'Quality_Check_Requested', 'Pallet_Staged', 'Fuel_Level',
            'Trailer_Type', 'Trailer_Size', 'Facility', 'Location', 'Move_Status', 'Trailer_Status',
            'Ref_1', 'Ref_2', 'Load_Type', 'Sub_Load_Type', 'Load_Qty', 'Priority_Move', 'Priority_Load',
            'Trailer_Condition', 'Origin_Destination', 'Comments', 'Latest_Loaded_Time', 'Live_Load',
            'Associate', 'Open_Dock_Appt_Id'
        ]

        # Add Download_Timestamp column
        current_timestamp = datetime.now()
        df['Download_Timestamp'] = current_timestamp

        # Insert data into the YMS_InventorySnapshotLog table
        for index, row in df.iterrows():
            try:
                # Apply facility rules for the current row
                facility_value = determine_facility(row['Location'], row['Facility'])

                print(f"Processing Row {index}: {row.to_dict()}")
                print(f"Facility after rules: {facility_value}")

                cursor.execute('''
                    INSERT INTO Nova.YMS_InventorySnapshot (
                        Appt_Date, Appt_Time, Arrival_Time, Time_In_Yard_Hrs, Appt_Num, Appt_Type,
                        Customer, Scac, Trailer_Num, Quality_Check_Requested, Pallet_Staged, Fuel_Level,
                        Trailer_Type, Trailer_Size, Facility, Location, Move_Status, Trailer_Status,
                        Ref_1, Ref_2, Load_Type, Sub_Load_Type, Load_Qty, Priority_Move, Priority_Load,
                        Trailer_Condition, Origin_Destination, Comments, Latest_Loaded_Time, Live_Load,
                        Associate, Open_Dock_Appt_Id, Download_Timestamp
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    safe_convert(row['Appt_Date'], 'date', 'Appt_Date', index),
                    safe_convert(row['Appt_Time'], 'time', 'Appt_Time', index),
                    safe_convert(row['Arrival_Time'], 'datetime', 'Arrival_Time', index),
                    safe_convert(row['Time_In_Yard_Hrs'], 'int', 'Time_In_Yard_Hrs', index),
                    safe_convert(row['Appt_Num'], 'int', 'Appt_Num', index),
                    safe_convert(row['Appt_Type'], 'str', 'Appt_Type', index),
                    safe_convert(row['Customer'], 'str', 'Customer', index),
                    safe_convert(row['Scac'], 'str', 'Scac', index),
                    safe_convert(row['Trailer_Num'], 'str', 'Trailer_Num', index),
                    safe_convert(row['Quality_Check_Requested'], 'str', 'Quality_Check_Requested', index),
                    safe_convert(row['Pallet_Staged'], 'str', 'Pallet_Staged', index),
                    safe_convert(row['Fuel_Level'], 'float', 'Fuel_Level', index),
                    safe_convert(row['Trailer_Type'], 'str', 'Trailer_Type', index),
                    safe_convert(row['Trailer_Size'], 'str', 'Trailer_Size', index),
                    facility_value,  # Facility is already determined
                    safe_convert(row['Location'], 'str', 'Location', index),
                    safe_convert(row['Move_Status'], 'str', 'Move_Status', index),
                    safe_convert(row['Trailer_Status'], 'str', 'Trailer_Status', index),
                    safe_convert(row['Ref_1'], 'str', 'Ref_1', index),
                    safe_convert(row['Ref_2'], 'str', 'Ref_2', index),
                    safe_convert(row['Load_Type'], 'str', 'Load_Type', index),
                    safe_convert(row['Sub_Load_Type'], 'str', 'Sub_Load_Type', index),
                    safe_convert(row['Load_Qty'], 'float', 'Load_Qty', index),
                    safe_convert(row['Priority_Move'], 'str', 'Priority_Move', index),
                    safe_convert(row['Priority_Load'], 'str', 'Priority_Load', index),
                    safe_convert(row['Trailer_Condition'], 'str', 'Trailer_Condition', index),
                    safe_convert(row['Origin_Destination'], 'str', 'Origin_Destination', index),
                    safe_convert(row['Comments'], 'str', 'Comments', index),
                    safe_convert(row['Latest_Loaded_Time'], 'datetime', 'Latest_Loaded_Time', index),
                    safe_convert(row['Live_Load'], 'str', 'Live_Load', index),
                    safe_convert(row['Associate'], 'str', 'Associate', index),
                    safe_convert(row['Open_Dock_Appt_Id'], 'str', 'Open_Dock_Appt_Id', index),
                    row['Download_Timestamp']
                ))
                print(f"Row {index} successfully inserted into YMS_InventorySnapshotLog.")
            except Exception as e:
                logging.error(f"Error inserting row {index} into YMS_InventorySnapshotLog: {e}")
                print(f"Error inserting row {index} into YMS_InventorySnapshotLog: {e}")
                continue

        conn.commit()
        logging.info("SQL import completed successfully.")
        print("SQL import completed successfully.")

        cursor.close()
        conn.close()

    except Exception as e:
        logging.error(f"An error occurred during the import process: {e}", exc_info=True)
        print(f"An error occurred during the import process: {e}")
        raise

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
        import_csv_to_sql(csv_file)
    else:
        print("Please provide the CSV file path as an argument.")
