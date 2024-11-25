
# This script creates a client db in the data services Postgres RDS instance and then takes a folder of flatfiles and imports them as tables into the database.
# Created by Zac Cheatle, March 2024

# TABLE OF CONTENTS
## Dependencies
## Logging
## Create Database Function
## Connect to Database Function
## Create Table from File Function
## Import Files Function
## User Interface

# ----------------------------------------------------------------------- DEPENDENCIES

# Import Dependencies
import os
import pandas as pd
import psycopg2
from psycopg2 import sql
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import logging

# ----------------------------------------------------------------------- LOGGING

# Truncate the log file to empty it before each use
with open('csdata-flatfile-postgres-import.log', 'w'):
    pass

# Create logger
logger = logging.getLogger()

# Set logging level for the logger
logger.setLevel(logging.DEBUG)

# Create Formatter
formatter = logging.Formatter('%(lineno)d - %(asctime)s - %(levelname)s - %(message)s')

# Create Console Handler for DEBUG levels
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG) 
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# Create File Handler
file_handler = logging.FileHandler('csdata-flatfile-postgres-import.log')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter) 
logger.addHandler(file_handler) 

# --------------------------------------------------------------------------------------- CREATE DATABASE FUNCTION

# Define function to create the client database
def create_database_if_not_exists(dbname, user, password, host, port):
    try:
        conn = psycopg2.connect(
            dbname='postgres',  # Establish connection to the RDS instance via the administrative database
            user='postgres',
            password='xxxxxxx',
            host='xxxxxxxx',
            port=5432
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Check if the database name already exists
        cursor.execute(sql.SQL("SELECT datname FROM pg_database WHERE datname = %s"), (dbname,))
        if cursor.fetchone():
            # If the database exists connect to it
            #cursor.execute(sql.SQL("DROP DATABASE IF EXISTS {}").format(sql.Identifier(dbname)))
            #cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(dbname)))
            logging.info(f"Database '{dbname}' already exists: connection successful.")
        else:
            # If the database doesn't exist, create it
            cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(dbname)))
            logging.info(f"Database '{dbname}' created successfully.")
        
        cursor.close()
        conn.close()
    except Exception as e:
        logging.critical(f"Error creating or accessing database '{dbname}': {str(e)}")
        error_occurred = True  # Set the flag to True if an error occurs

# --------------------------------------------------------------------------------------- CONNECT TO DATABASE FUNCTION

# Function for UI button to initiate database connection
def connect_to_database(dbname):
    create_database_if_not_exists(dbname, 'postgres', 'xxxxxxx', 'xxxxxxxx', 5432)

# --------------------------------------------------------------------------------------- CREATE TABLE FROM FILE FUNCTION

# Define Function to read .csv or .xlsx files 
def create_table_from_file(cursor, file_path, table_name):
    # Determine file type based on extension
    file_extension = file_path.split('.')[-1].lower()

    table_created = False
    
    try:
        # Read the file based on its type
        if file_extension == 'csv':
            # Try reading the file with different encodings
            encodings = ['utf-8', 'latin-1', 'iso-8859-1']
            for encoding in encodings:
                try:
                    df = pd.read_csv(file_path, encoding=encoding, dtype=str)
                    break  # Stop trying encodings if successful
                except Exception as e:
                    if encoding == encodings[-1]:
                        logging.error(f"Error reading CSV file '{file_path}' with encoding '{encoding}': {e}")
                        raise  # Raise exception if all encodings fail

        elif file_extension == 'xlsx':
            try:
                df = pd.read_excel(file_path, dtype=str)
                # Perform database operations to create table from dataframe
                # Example: df.to_sql(table_name, con=your_database_connection)
                #logging.info(f"XLSX file '{file_path}' read successfully.")
                #return True
            except Exception as e:
                logging.error(f"Error reading XLSX file '{file_path}': {e}")
                return False

        else:
            logging.warning(f"The file '{file_path}' can't be read, it has an invalid file extension '.{file_extension}'. Only '.csv' and '.xlsx' are permitted: file skipped.")
            return False

        # Convert all columns to object type first so we can treat blanks as NULL
        #df = df.astype('string')

        # Handle blank values by replacing them with NULL
        df = df.where(pd.notnull(df), None)
        
        # Extract column names and construct column definitions
        columns = df.columns.tolist()
        column_definitions = ['"{}" TEXT'.format(col) for col in columns]

        # Drop existing table if it exists
        drop_table_query = sql.SQL("DROP TABLE IF EXISTS {};").format(sql.Identifier(table_name))
        cursor.execute(drop_table_query)

        # Create table for each file in the folder
        create_table_query = sql.SQL("CREATE TABLE {} ({})").format(
            sql.Identifier(table_name),
            sql.SQL(', ').join(map(sql.SQL, column_definitions))
        )
        cursor.execute(create_table_query)
        table_created = True
        # Log a message when the table is successfully created
        logging.info(f"Table '{table_name}' succesfully created from {table_name}.{file_extension} file.")

        # establish row count for each table
        rows_inserted = 0

        # Insert data into the tables
        data_inserted = True  # Initialize data_inserted
        for index, row in df.iterrows():
            try:
                insert_query = sql.SQL("INSERT INTO {} ({}) VALUES ({});").format(
                    sql.Identifier(table_name),
                    sql.SQL(', ').join(map(sql.Identifier, columns)),
                    sql.SQL(', ').join([sql.Placeholder()] * len(columns))
                )
                cursor.execute(insert_query, row.tolist())
                rows_inserted += 1
            except psycopg2.Error as e:
                logging.error(f"Error inserting data into table '{table_name}': {e}")
                data_inserted = False  # Set data_inserted to False if an error occurs
                break  # Exit the loop if an error occurs
        
        # count of columns in each dataframe
        num_columns = len(columns)

        if data_inserted:
            logging.info(f"Data successfully inserted into '{table_name}': {num_columns} columns and {rows_inserted} rows inserted.")


    except ValueError as ve:
        logging.error(f"ValueError creating table {table_name}: {ve}")
    
    except Exception as e:
        # Log an error message with detailed exception information for table creation failure
        if not table_created:
            logging.error(f"Error creating table '{table_name}' from {file_extension} file: {str(e)}")
            logging.exception(f"Exception occurred during table creation: {e}")
        # Log an error message with detailed exception information for data insertion failure
        elif not data_inserted:
            logging.error(f"Error inserting data into table '{table_name}' from {file_extension} file: {str(e)}")
            logging.exception(f"Exception occurred during data insertion: {e}")
        # Re-raise the exception to see more detailed traceback in the console
        raise
    
    return table_created, data_inserted

# --------------------------------------------------------------------------------------- IMPORT FILES

def import_files(dbname):
    error_occurred = False  # Initialize error_occurred variable
    file_count = 0 # Establish count of how many files are in the folder
    tables_imported = 0 # Establish count of how many files successfully imported as tables

    # Connect to PostgreSQL and create the database if it doesn't exist
    #create_database_if_not_exists(dbname, 'postgres', 'xxxxxxxxx', 'xxxxxxxx', 5432)

    # Open folder dialog to select folder containing files
    folder_path = filedialog.askdirectory()  
    if not folder_path:
        logging.error(f"No Folder Selected")
        return  # No folder selected
    
    # Connect to PostgreSQL RDS
    try:
        conn = psycopg2.connect(
            dbname=dbname,  # Connect to the specified database
            user='postgres',
            password='xxxxxxxxx',
            host='xxxxxxxxxxxxxxx',
            port=5432
        )
        cursor = conn.cursor()

        # Logging: Starting file import process
        logging.info("Starting file import process...")

        for file_name in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file_name)
            file_extension = file_path.split('.')[-1].lower()
            table_name = os.path.splitext(file_name)[0].lower() # Use file name as table name without extension

            try:
                if file_extension in ("csv", "xlsx"):
                    logging.info(f"Importing file '{file_name}'...")
                    create_table_from_file(cursor, file_path, table_name)
                    conn.commit()
                    tables_imported +=1
                else:
                    logging.warning(f"The file '{table_name}.{file_extension}' has an invalid file extension '.{file_extension}'. Only '.csv' and '.xlsx' are permitted: Table not created, file skipped.")
                    error_occurred = True
            except psycopg2.Error as e:
                logging.error(f"Psycopg2 error when creating table '{table_name}': {e}")
                error_occurred = True
            except Exception as ex:
                logging.error(f"File import error when creating table '{table_name}': {ex}")
                error_occurred = True

            file_count += 1 # increment file count for every file in the folder

        cursor.close()
        conn.close()

        if not error_occurred:
            logging.info(f"File import process successfully completed. {tables_imported}/{file_count} files imported.")  # Log that script was completed successfully
        else:
            logging.error(f"File import process completed with errors or warnings. {tables_imported}/{file_count} files imported successfully.")  # Log that script was completed with errors

    except psycopg2.Error as e:
        logging.error(f"Psycopg2 Database Connection Error: {e}")
        error_occurred = True

    except Exception as e:
        logging.error(f"Database Connection Error: {str(e)}")
        error_occurred = True  # Set the flag to True if an error occurs


# ----------------------------------------------------------------------------------------------- USER INTERFACE

# Define function to center the user input on the screen
def center_window(window, width, height):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    x = (screen_width - width) // 2
    y = (screen_height - height) // 2

    window.geometry(f"{width}x{height}+{x}+{y}")

# Function to display instructions
def display_instructions():
    instructions = """
    Welcome to the Flat File Import Tool!

    Please follow these steps:
    
    1. Enter the name of the database in the field below.
    2. Click the button to select a folder containing flat files to import.
    3. Wait for the import process to complete. Progress will be shown in the console.
    4. Close this window to stop the application.

    Note: Only CSV and Excel files (.csv, .xlsx) are supported for import.

    """
    instructions_label.config(text=instructions)

# Function to kill/close application
def on_closing():
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        messagebox.showinfo("Info", "Application stopped")
        root.destroy()

# Create the root window
root = tk.Tk()
root.title("Flat File Import Tool")
root.protocol("WM_DELETE_WINDOW", on_closing)

# Label to display instructions (global variable)
instructions_label = tk.Label(root, text="")
instructions_label.pack(pady=(10, 15))  # Added padding below the instructions

# Display instructions
display_instructions()

# Entry for database name
dbname_label = tk.Label(root, text="Enter Database Name:")
dbname_label.pack(pady=2)

dbname_entry = tk.Entry(root)
dbname_entry.pack(pady=2)

# Button to connect to the database
connect_button = tk.Button(root, text="Connect to Database", command=lambda: connect_to_database(dbname_entry.get()))
connect_button.pack(pady=10)

# Button to trigger file import
import_button = tk.Button(root, text="Select Folder of Files to Import", command=lambda: import_files(dbname_entry.get()))
import_button.pack(pady=5)

# Center the window on the screen
window_width = 500
window_height = 500
center_window(root, window_width, window_height)

root.mainloop()
