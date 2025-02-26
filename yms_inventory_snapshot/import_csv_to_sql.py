import pandas as pd
import pyodbc
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(filename='import_csv_to_sql.log', level=logging.INFO,
                    format='%(asctime)s %(levelname)s: %(message)s')

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

        # Clear the YMS_InventorySnapshot table
        logging.info("Clearing the YMS_InventorySnapshot table...")
        cursor.execute('DELETE FROM Nova.YMS_InventorySnapshot')
        conn.commit()

        # Verify that the table is empty
        cursor.execute('SELECT COUNT(*) FROM Nova.YMS_InventorySnapshot')
        row_count = cursor.fetchone()[0]
        logging.info(f"Rows in YMS_InventorySnapshot after delete: {row_count}")

        # Read the CSV file
        logging.info(f"Reading the CSV file: {csv_file}")
        df = pd.read_csv(csv_file)

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

        # Function to convert and validate data types
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

        # Insert data into the YMS_InventorySnapshotLog table
        for index, row in df.iterrows():
            try:
                logging.info(f"Inserting row {index} into YMS_InventorySnapshotLog with Time_In_Yard_Hrs: {row['Time_In_Yard_Hrs']}")
                cursor.execute('''
                    INSERT INTO Nova.YMS_InventorySnapshotLog (
                        Appt_Date, Appt_Time, Arrival_Time, Time_In_Yard_Hrs, Appt_Num, Appt_Type,
                        Customer, Scac, Trailer_Num, Quality_Check_Requested, Pallet_Staged, Fuel_Level,
                        Trailer_Type, Trailer_Size, Facility, Location, Move_Status, Trailer_Status,
                        Ref_1, Ref_2, Load_Type, Sub_Load_Type, Load_Qty, Priority_Move, Priority_Load,
                        Trailer_Condition, Origin_Destination, Comments, Latest_Loaded_Time, Live_Load,
                        Associate, Open_Dock_Appt_Id, Download_Timestamp
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''',
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
                safe_convert(row['Fuel_Level'], 'str', 'Fuel_Level', index),
                safe_convert(row['Trailer_Type'], 'str', 'Trailer_Type', index),
                safe_convert(row['Trailer_Size'], 'str', 'Trailer_Size', index),
                safe_convert(row['Facility'], 'str', 'Facility', index),
                safe_convert(row['Location'], 'str', 'Location', index),
                safe_convert(row['Move_Status'], 'str', 'Move_Status', index),
                safe_convert(row['Trailer_Status'], 'str', 'Trailer_Status', index),
                safe_convert(row['Ref_1'], 'str', 'Ref_1', index),
                safe_convert(row['Ref_2'], 'str', 'Ref_2', index),
                safe_convert(row['Load_Type'], 'str', 'Load_Type', index),
                safe_convert(row['Sub_Load_Type'], 'str', 'Sub_Load_Type', index),
                safe_convert(row['Load_Qty'], 'int', 'Load_Qty', index),
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
                )
            except Exception as e:
                logging.error(f"Error inserting row into YMS_InventorySnapshotLog {index}: {e}")
                continue

        # Insert data into the YMS_InventorySnapshot table
        for index, row in df.iterrows():
            try:
                logging.info(f"Inserting row {index} into YMS_InventorySnapshot with Time_In_Yard_Hrs: {row['Time_In_Yard_Hrs']}")
                cursor.execute('''
                    INSERT INTO Nova.YMS_InventorySnapshot (
                        Appt_Date, Appt_Time, Arrival_Time, Time_In_Yard_Hrs, Appt_Num, Appt_Type,
                        Customer, Scac, Trailer_Num, Quality_Check_Requested, Pallet_Staged, Fuel_Level,
                        Trailer_Type, Trailer_Size, Facility, Location, Move_Status, Trailer_Status,
                        Ref_1, Ref_2, Load_Type, Sub_Load_Type, Load_Qty, Priority_Move, Priority_Load,
                        Trailer_Condition, Origin_Destination, Comments, Latest_Loaded_Time, Live_Load,
                        Associate, Open_Dock_Appt_Id, Download_Timestamp
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''',
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
                safe_convert(row['Fuel_Level'], 'str', 'Fuel_Level', index),
                safe_convert(row['Trailer_Type'], 'str', 'Trailer_Type', index),
                safe_convert(row['Trailer_Size'], 'str', 'Trailer_Size', index),
                safe_convert(row['Facility'], 'str', 'Facility', index),
                safe_convert(row['Location'], 'str', 'Location', index),
                safe_convert(row['Move_Status'], 'str', 'Move_Status', index),
                safe_convert(row['Trailer_Status'], 'str', 'Trailer_Status', index),
                safe_convert(row['Ref_1'], 'str', 'Ref_1', index),
                safe_convert(row['Ref_2'], 'str', 'Ref_2', index),
                safe_convert(row['Load_Type'], 'str', 'Load_Type', index),
                safe_convert(row['Sub_Load_Type'], 'str', 'Sub_Load_Type', index),
                safe_convert(row['Load_Qty'], 'int', 'Load_Qty', index),
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
                )
            except Exception as e:
                logging.error(f"Error inserting row into YMS_InventorySnapshot {index}: {e}")
                continue

        # Commit the transaction
        conn.commit()

        # Verify that data has been inserted
        cursor.execute('SELECT COUNT(*) FROM Nova.YMS_InventorySnapshot')
        row_count = cursor.fetchone()[0]
        logging.info(f"Rows in YMS_InventorySnapshot after insert: {row_count}")

        # Close the cursor and connection
        cursor.close()
        conn.close()
        logging.info('SQL import completed')

    except Exception as e:
        logging.error(f"An error occurred during the import process: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
        import_csv_to_sql(csv_file)
    else:
        print("Please provide the CSV file path as an argument.")
