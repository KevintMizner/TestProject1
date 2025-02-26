from config import DB_CONFIG, LOG_FILE
import pyodbc
import logging
import sys
import pandas as pd
from datetime import datetime
import re
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Safe conversion helper
def safe_convert(value, data_type, column_name, row_index):
    try:
        if pd.isnull(value) or value == '':
            return None
        if data_type == 'date':
            return pd.to_datetime(value, errors='coerce').date()
        if data_type == 'time':
            return pd.to_datetime(value, errors='coerce').time()
        if data_type == 'datetime':
            return pd.to_datetime(value, errors='coerce')
        if data_type == 'int':
            return int(value) if pd.notnull(value) else 0
        if data_type == 'float':
            return float(value) if pd.notnull(value) else 0.0
        if data_type == 'str':
            return str(value)
    except ValueError as e:
        logger.error(f"Error converting value '{value}' for column '{column_name}' in row {row_index}: {e}")
        return None

# Facility determination helper
FACILITY_RULES = [
    (r'LOT-', "Drop Lot"),
    (r'01-', "Building 01"),
    (r'02-', "Building 01"),
    (r'03-', "Building 03"),
    (r'04-', "Building 03"),
    (r'05-', "Building 05"),
    (r'14-', "Building 14"),
    (r'06-', "Building 06"),
]

def determine_facility(end_spot, default_facility):
    if not isinstance(end_spot, str):
        return default_facility
    for pattern, facility in FACILITY_RULES:
        if re.match(pattern, end_spot, re.IGNORECASE):
            return facility
    return default_facility

# CSV Import function
def import_driver_event_log(csv_file):
    try:
        conn = pyodbc.connect(
            f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={DB_CONFIG['server']};DATABASE={DB_CONFIG['database']};UID={DB_CONFIG['username']};PWD={DB_CONFIG['password']}"
        )
        cursor = conn.cursor()
        
        logger.info(f"Reading CSV file: {csv_file}")
        df = pd.read_csv(csv_file)

        logger.info(f"CSV contains {len(df)} rows.")

        # Column standardization
        df.columns = [
            'Facility', 'Date', 'Requested By', 'Driver', 'Carrier Company', 'Scac',
            'Trailer Plate', 'Trailer #', 'Appt#', 'Customer', 'Load Type',
            'Vehicle Type', 'Start Location', 'Start Spot', 'End Location',
            'End Spot', 'Request Time', 'Time In Queue (Minutes)', 'Accept Time',
            'Start Time', 'Complete Time', 'Elapsed Time (Minutes)', 'Priority Move',
            'Priority Load', 'Comments', 'Move Comments', 'Cancelled By',
            'Cancelled Time', 'Decline Reason', 'Event', 'Username'
        ]

        # Apply facility rules
        df['Facility'] = df.apply(lambda row: determine_facility(row['End Spot'], row['Facility']), axis=1)

        # Extract date for purging
        first_date = pd.to_datetime(df['Date'], errors='coerce').iloc[0].date()
        logger.info(f"Purging records for date: {first_date}")

        cursor.execute("DELETE FROM Nova.YMS_DriverEventLog WHERE [Date] = ?", first_date)
        conn.commit()

        # Insert rows
        for index, row in df.iterrows():
            row_tuple = tuple(safe_convert(row[col], 'str', col, index) for col in df.columns)
            cursor.execute('''
                INSERT INTO Nova.YMS_DriverEventLog (
                    Facility, [Date], [Requested By], Driver, [Carrier Company], Scac,
                    [Trailer Plate], [Trailer #], [Appt#], Customer, [Load Type],
                    [Vehicle Type], [Start Location], [Start Spot], [End Location],
                    [End Spot], [Request Time], [Time In Queue (Minutes)], [Accept Time],
                    [Start Time], [Complete Time], [Elapsed Time (Minutes)], [Priority Move],
                    [Priority Load], Comments, [Move Comments], [Cancelled By],
                    [Cancelled Time], [Decline Reason], Event, Username
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', row_tuple)

        conn.commit()
        logger.info(f"Imported {len(df)} rows successfully.")

    except Exception as e:
        logger.error(f"Error during import: {e}", exc_info=True)
        raise
    finally:
        cursor.close()
        conn.close()

# Main entry point
if __name__ == "__main__":
    if len(sys.argv) < 2:
        logger.warning("No CSV file provided. Prompting for input...")
        csv_file = input("Please enter the path to the CSV file to process: ").strip()
        if not Path(csv_file).is_file():
            logger.error(f"File not found: {csv_file}")
            sys.exit(1)
    else:
        csv_file = sys.argv[1]

    logger.info(f"Starting import for file: {csv_file}")
    import_driver_event_log(csv_file)
