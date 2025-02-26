import pandas as pd
import pyodbc
from datetime import datetime
import logging
import re
import sys

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

        matches = re.findall(r'(Docks-|Yard-)(\d{2})', location)

        for prefix, code in matches:
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

            print(f"Location: {location}, Determined Facility: {result}")
            return result

        if '1-5' in location and ('LOT' in location or 'Lot' in location):
            result = "Drop Lot"
            print(f"Location: {location}, Determined Facility: {result}")
            return result

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
            return None

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
        server = 'sql-wmsag'
        database = 'AD_Analysis'
        username = 'api_interface'
        password = 'Z@7824_aPi'

        logging.info("Connecting to the SQL Server...")
        conn = pyodbc.connect(
            f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'
        )
        cursor = conn.cursor()

        logging.info("Clearing the YMS_InventorySnapshot table...")
        cursor.execute('DELETE FROM Nova.YMS_InventorySnapshot')
        conn.commit()

        logging.info(f"Reading the CSV file: {csv_file}")
        df = pd.read_csv(csv_file, header=0)

        if df.empty:
            logging.warning("CSV file is empty. No records to process.")
            return

        columns_to_keep = [
            'Appt Date', 'Appt Time', 'Arrival Time', 'Time In Yard (Hrs)', 'Appt #', 'Appt Type',
            'Customer', 'Scac', 'Trailer #', 'Quality Check Requested', 'Pallet Staged', 'Fuel Level',
            'Trailer Type', 'Trailer Size', 'Facility', 'Location', 'Move Status', 'Trailer Status',
            'Ref 1', 'Ref 2', 'Load Type', 'Sub Load Type', 'Load Qty', 'Priority Move', 'Priority Load',
            'Seal Number', 'Trailer Condition', 'Origin/Destination', 'Comments', 'Latest Loaded Time',
            'Live Load', 'Preferred Door', 'Open Dock Ref'
        ]
        df = df[columns_to_keep]

        df.columns = [
            'Appt_Date', 'Appt_Time', 'Arrival_Time', 'Time_In_Yard_Hrs', 'Appt_Num', 'Appt_Type',
            'Customer', 'Scac', 'Trailer_Num', 'Quality_Check_Requested', 'Pallet_Staged', 'Fuel_Level',
            'Trailer_Type', 'Trailer_Size', 'Facility', 'Location', 'Move_Status', 'Trailer_Status',
            'Ref_1', 'Ref_2', 'Load_Type', 'Sub_Load_Type', 'Load_Qty', 'Priority_Move', 'Priority_Load',
            'Seal_Number', 'Trailer_Condition', 'Origin_Destination', 'Comments', 'Latest_Loaded_Time',
            'Live_Load', 'Preferred_Door', 'Open_Dock_Ref'
        ]

        current_timestamp = datetime.now()
        df['Download_Timestamp'] = current_timestamp

        for index, row in df.iterrows():
            try:
                facility_value = determine_facility(row['Location'], row['Facility'])

                cursor.execute('''
                INSERT INTO Nova.YMS_InventorySnapshot (
                    Appt_Date, Appt_Time, Arrival_Time, Time_In_Yard_Hrs, Appt_Num, Appt_Type,
                    Customer, Scac, Trailer_Num, Quality_Check_Requested, Pallet_Staged, Fuel_Level,
                    Trailer_Type, Trailer_Size, Facility, Location, Move_Status, Trailer_Status,
                    Ref_1, Ref_2, Load_Type, Sub_Load_Type, Load_Qty, Priority_Move, Priority_Load, Seal_Number,
                    Trailer_Condition, Origin_Destination, Comments, Latest_Loaded_Time, Live_Load,
                    Preferred_Door, Open_Dock_Ref, Download_Timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?)
            ''', (
                safe_convert(row['Appt_Date'], 'date', 'Appt_Date', index),
                safe_convert(row['Appt_Time'], 'time', 'Appt_Time', index),
                safe_convert(row['Arrival_Time'], 'datetime', 'Arrival_Time', index),
                safe_convert(row['Time_In_Yard_Hrs'], 'int', 'Time_In_Yard_Hrs', index),
                safe_convert(row['Appt_Num'], 'str', 'Appt_Num', index),
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
                safe_convert(row['Seal_Number'], 'str', 'Seal_Number', index),
                safe_convert(row['Trailer_Condition'], 'str', 'Trailer_Condition', index),
                safe_convert(row['Origin_Destination'], 'str', 'Origin_Destination', index),
                safe_convert(row['Comments'], 'str', 'Comments', index),
                safe_convert(row['Latest_Loaded_Time'], 'datetime', 'Latest_Loaded_Time', index),
                safe_convert(row['Live_Load'], 'str', 'Live_Load', index),
                safe_convert(row['Preferred_Door'], 'str', 'Preferred_Door', index),
                safe_convert(row['Open_Dock_Ref'], 'str', 'Open_Dock_Ref', index),
                row['Download_Timestamp']
            ))

            except Exception as e:
                logging.error(f"Error inserting row {index} into YMS_InventorySnapshot: {e}")
                print(f"Error inserting row {index} into YMS_InventorySnapshot: {e}")
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
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
    else:
        csv_file = input("Enter the path to the CSV file for testing: ").strip()

    try:
        import_csv_to_sql(csv_file)
    except Exception as e:
        print(f"Failed to process the CSV file: {e}")
