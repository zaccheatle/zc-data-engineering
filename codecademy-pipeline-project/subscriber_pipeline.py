#!/usr/bin/env python
# coding: utf-8

# Subscriber Data Pipeline Portfolio Project
# **Objective**: build a data engineering pipeline to regularly transform a messy database into a clean source of truth for an analytics team.
# **Data Source:** Cademycode customer data sqlite3 Database
# **Author**: Zac Cheatle

# ---------------------------------------------------------------------------------------------------------------------------------------

# import dependencies
import os
import pandas as pd
import numpy as np
import json
import sqlite3
from sqlite3 import Error
import logging
from contextlib import contextmanager

# set pandas column width
pd.set_option('display.max_colwidth', None)

# Logging Set Up
logging.basicConfig(
    filename="cleanse_db.log",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filemode='w',
    level=logging.DEBUG,
    force=True)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------------------------------------------------------------------

# resource management
@contextmanager
def database_connection(database):
    """
    Context manager for managing SQLite database connections.
    """
    connection = sqlite3.connect('cademycode.db')
    try:
        yield connection  # Provide the connection to the context block
    finally:
        connection.close()  # Ensure the connection is closed

# function to clean tables
def main(database):
    """
    Cleanse the three tables from the SQLite database according to predefined cleansing steps, import cleaned dataframes into target db and return a cleaned csv. 

    Parameters:
        database_path (str): Path to the SQLite database.

    Returns:
        dict: A dictionary containing cleaned DataFrames for each table:
        {'dataframes['students']': cleaned_dataframes['students'], 'dataframes['courses']': cleaned_dataframes['courses'], 'dataframes['student_jobs']': cleaned_dataframes['student_jobs']}
    """
    try:
        # Use the context manager to handle database connection
        with database_connection(database) as source_conn:
            # Retrieve all table names
            cursor = source_conn.cursor()
            tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
            logging.info(f'Successfully connected to source database tables {tables}.')
            
            # Load tables into DataFrames
            logging.info(f'loading {tables} tables to datframes....')
            dataframes = {}
            for table_tuple in tables:
                table_name = table_tuple[0]
                query = f"SELECT * FROM {table_name}"
                df = pd.read_sql_query(query, source_conn)
                logging.info(f'Successfully loaded {table_name} as a dataframe.')

                # Modify the table name for dictionary keys (after first underscore)
                modified_table_name = table_name.split('_', 1)[-1],
                dataframes[modified_table_name] = df
                logging.info(f'{table_name} succesfully modified to {modified_table_name}.')

            # DATA PREP -------------------------
            # Column clean up
            try:
                # split contact_info column into separate email and address columns
                dataframes['students']['contact_info'] = dataframes['students']['contact_info'].apply(lambda x: json.loads(x) if isinstance(x, str) else x)
                dataframes['students']['mailing_address'] = dataframes['students']['contact_info'].apply(lambda x: x.get('mailing_address') if isinstance(x, dict) else None)
                dataframes['students']['email'] = dataframes['students']['contact_info'].apply(lambda x: x.get('email') if isinstance(x, dict) else None)
            except:



            # split up mailing address into separate columns
            try:
                dataframes['students'][['address', 'city', 'state', 'zip']] = dataframes['students']['mailing_address'].str.extract(r'^(.*),\s*([\w\s]+),\s*([\w\s]+),\s*(\d+)$')
            except: 



            # drop contact_info and mailing_address columns
            try:
                dataframes['students'] = dataframes['students'].drop(columns=['mailing_address'])
                dataframes['students'] = dataframes['students'].drop(columns=['contact_info'])
            except:



            # Duplicates
            try:
                dataframes['students']=dataframes['students'].drop_duplicates(keep='last')
                dataframes['student_jobs']=dataframes['student_jobs'].drop_duplicates(keep='last')
                dataframes['courses']=dataframes['courses'].drop_duplicates(keep='last')
            except:



            # drop all rows with a null value
            try:
                dataframes['students'] = dataframes['students'].dropna()
                dataframes['student_jobs'] = dataframes['student_jobs'].dropna()
                dataframes['courses'] = dataframes['courses'].dropna()
            except:



            # set datatypes for each table
            try:
                # dataframes['courses'] table
                c_dtype_dict = {'career_path_id': 'int16', 'career_path_name': 'string', 'hours_to_complete':'int16'}
                dataframes['courses'] = dataframes['courses'].astype(c_dtype_dict)

                # dataframes['student_jobs'] table
                sj_dtype_dict = {'job_id':'int16', 'job_category':'category', 'avg_salary':'int16'}

                # dataframes['students'] table
                dtype_dict = {'uuid':'int16',
                            'name':'string', 
                            'dob':'datetime64[ns]', 
                            'sex':'category', 
                            'job_id':'float16', 
                            'num_course_taken':'float16', 
                            'current_career_path_id':'float16', 
                            'time_spent_hrs':'float16',
                            'email':'string',
                            'address':'string',
                            'city':'string',
                            'state':'category',
                            'zip': 'string'}

                dataframes['students'] = dataframes['students'].astype(dtype_dict)
                dataframes['students']['num_course_taken'] = dataframes['students']['num_course_taken'].astype(int)
                dataframes['students']['job_id'] = dataframes['students']['job_id'].astype(int)
                dataframes['students']['current_career_path_id'] = dataframes['students']['current_career_path_id'].astype(int)
            except:


            cleaned_students = dataframes['students']
            cleaned_courses = dataframes['courses']
            cleaned_student_jobs = dataframes['student_jobs']
            
            # Return cleaned tables
            return cleaned_students, cleaned_courses, cleaned_student_jobs
            logger.info('Cleaned tables ready!')

    except Error as e:
        logger.error(f"Source DB SQLite error: {e}")
        raise
    except KeyError as e:
        logger.error(f"Source DB Missing table or key: {e}")
        raise

    # connect to target db and import cleaned tables
    def import_cleaned_tables(cleaned_students, cleaned_courses, cleaned_student_jobs):
        try: 
            # Create new sqlite3 database with cleaned tables
            with database_connection('cleaned_cademycode.db') as target_conn:
                target_cursor = target_conn.cursor()
                clean_tables = target_cursor.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
                logger.info(f'{clean_tables} are the tables in the target database.')

                cleaned_students.to_sql('students', target_conn, index=False, if_exists='append')
                logger.info("'Students table' successfully loaded with clean data.")
                cleaned_courses.to_sql('courses', target_conn, index=False, if_exists='append')
                logger.info("'Courses' table successfully loaded with clean data.")
                cleaned_student_jobs.to_sql('student_jobs', target_conn, index=False, if_exists='append')
                logger.info("'Student Jobs' table successfully loaded with clean data.")

                # Create csv with all tables merged together for analysts
                dataframes['students'] = dataframes['students'].merge(dataframes['courses'], left_on='current_career_path_id', right_on='career_path_id', how='left')
                cleaned_cademycode_data = dataframes['students'].merge(dataframes['student_jobs'], on='job_id', how='left')
                cleaned_cademycode_data.drop(['career_path_id'], axis=1, inplace=True)
                cleaned_cademycode_data.head()
                logger.info("Clean tables combined successfully.")

                # create csv
                cleaned_cademycode_data.to_csv('cleaned_cademycode_data', index=False)
                logger.info('CSV file created!')

        except Error as e:
            logger.error(f"Target DB SQLite error: {e}")
            raise


# ---------------------------------------------------------------------------------------------------------------------------------------
