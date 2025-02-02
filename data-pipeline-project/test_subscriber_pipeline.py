
# import dependencies
import unittest
import logging
import pandas as pd
import numpy as np
import os
import sqlite3
from subscriber_pipeline import cleanse_tables

# set pandas column width
pd.set_option('display.max_colwidth', None)

# Logging Set Up
logging.basicConfig(
    filename="test_cleanse_db.log",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filemode='w',
    level=logging.DEBUG,
    force=True)
logger = logging.getLogger(__name__)


# Start unit tests --------------------------------------------------------------------------------------------------
# Setup class
class MockData(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # set up connection to in memory sqlite db
        cls.conn = sqlite3.Connection(":memory")
        cls.cur = cls.conn.cursor()

        # create test student, courses, and student job tables
        # courses table
        cls.cur.execute(""" CREATE TABLE courses (
                        career_path_id INTEGER PRIMARY KEY,
                        career_path_name TEXT,
                        hours_to_complete REAL
                        )""")
        
        # student jobs table
        cls.cur.execute(""" CREATE TABLE student_jobs (
                        job_id INTEGER PRIMARY KEY,
                        job_category TEXT,
                        avg_salary INTEGER
                        )""")

        # students table
        cls.cur.execute(""" CREATE TABLE students (
                        uuid INTEGER,
                         name TEXT,
                        dob NUMERIC,
                        sex TEXT,
                        job_id INTEGER,
                        num_courses_taken REAL,
                        current_career_path_id INTEGER,
                        time_spent_hrs REAL,
                        contact_info TEXT
                         )""")
        
        # insert mock data in each table
        # courses table
        cls.conn.executemany(""" INSERT INTO courses (job_id, job_category, avg_salary) VALUES (
                             (1, "scientist", 25.2),
                             (2, "teacher", 55.758),
                             (2, "teacher", 55.758),
                             (3, "engineer", 105),
                             (NULL, NULL, NULL),
                             (4, "coach", NULL)
                             )""")
        
        # student_jobs table
        cls.conn.executemany(""" INSERT INTO courses (career_path_id, career_path_name, hours_to_complete) VALUES (
                             (1, "A", 50000),
                             (2, "B", 75000),
                             (3, "C", None),
                             (4, NULL, 10000),
                             (5, "C", 150000),
                             (5, "C", 150000)
                             (NULL, "D", 80000),
                             (6, NULL, NULL)
                             )""")
        
        # students table
        cls.conn.executemany(""" INSERT INTO courses (uuid, name, dob, sex, job_id, num_courses_taken, current_career_path_id, time_spent_hrs, contact_info TEXT) VALUES (
                            (1, 'John Doe', '1985-03-15', 'M', 101, 5.0, 201, 120.5, 'john@example.com, 123 Elm St, Seattle, WA, 98101'),
                            (2, 'Jane Smith', NULL, 'F', 102, 3.0, 202, NULL, 'jane@example.com, 456 Maple Rd, Denver, CO, 80203'),
                            (3, 'Alice Lee', '1992-07-20', 'F', 101, NULL, 203, 85.0, 'alice@example.com, 789 Pine Ave, Austin, TX, 73301'),
                            (4, 'Bob Brown', '1985-03-15', 'M', NULL, 5.0, 201, 120.5, NULL),
                            (5, 'Charlie King', '1990-12-12', 'M', 103, 2.0, NULL, 40.0, 'charlie@example.com, 1010 Oak Blvd, Miami, FL, 33101'),
                            (6, 'Jane Smith', NULL, 'F', 102, 3.0, 202, NULL, 'jane@example.com, 456 Maple Rd, Denver, CO, 80203'),
                            (7, 'Alice Lee', '1992-07-20', 'F', 101, NULL, 203, 85.0, 'alice@example.com, 789 Pine Ave, Austin, TX, 73301')
                             )""")
        return super().setUpClass()
    
    # Tear down
    @classmethod
    def tearDownClass(cls):
        cls.conn.close()
        return super().tearDownClass()


# tests

# tests to check for foreign key errors
class IdCheck(MockData):
    def test_for_path_id(self):
        """
        Unit test to ensure that join keys exist between the students and courses tables.

        This test checks that all `current_career_path_id` values from the `students` table
        exist in the `career_path_id` column of the `courses` table.
        """
        # Fetch data and convert to pandas DataFrames
        cur = self.cur

        # Query the tables
        students_query = "SELECT current_career_path_id FROM students"
        courses_query = "SELECT career_path_id FROM courses"

        # Convert to DataFrames
        students_df = pd.DataFrame(cur.execute(students_query).fetchall(), columns=["current_career_path_id"])
        courses_df = pd.DataFrame(cur.execute(courses_query).fetchall(), columns=["career_path_id"])

        # Extract unique IDs
        student_ids = students_df["current_career_path_id"].dropna().unique()  # Remove NULLs
        course_ids = courses_df["career_path_id"].unique()

        # Check if all student IDs are in course IDs
        is_subset = np.isin(student_ids, course_ids)
        missing_ids = student_ids[~is_subset]

        # Assert no missing IDs
        try:
            assert len(missing_ids) == 0, f"Missing career_path_id(s): {list(missing_ids)} in 'courses' table"
        except AssertionError as ae:
            logger.error("Test failed: %s", ae)
            raise ae
        else:
            logger.info("All career_path_ids are present in the 'courses' table.")
            print("All career_path_ids are present in the 'courses' table.")

    def test_for_job_id(self):
        """
        Unit test to ensure that join keys exist between the students and student_jobs tables.

        This test checks that all `job_id` values from the `students` table
        exist in the `job_id` column of the `student_jobs` table.
        """
        # Fetch data and convert to pandas DataFrames
        cur = self.cur

        # Query the tables
        students_query = "SELECT job_id FROM students"
        student_jobs_query = "SELECT job_id FROM student_jobs"

        # Convert to DataFrames
        students_df = pd.DataFrame(cur.execute(students_query).fetchall(), columns=["job_id"])
        student_jobs_df = pd.DataFrame(cur.execute(student_jobs_query).fetchall(), columns=["job_id"])

        # Extract unique IDs
        student_job_ids = students_df["job_id"].dropna().unique()  # Remove NULLs
        job_ids_in_student_jobs = student_jobs_df["job_id"].unique()

        # Check if all student job IDs are in student_jobs table
        is_subset = np.isin(student_job_ids, job_ids_in_student_jobs)
        missing_ids = student_job_ids[~is_subset]

        # Assert no missing IDs
        try:
            assert len(missing_ids) == 0, f"Missing job_id(s): {list(missing_ids)} in `student_jobs` table"
        except AssertionError as ae:
            logger.error("Test failed: %s", ae)
            raise ae
        else:
            logger.info("All job_ids are present in the `student_jobs` table.")
            print("All job_ids are present in the `student_jobs` table.")

# class to test for data integrity i.e. null values, duplicates, incorrect formats, invalid schema
class DataIntegrity(MockData):
    def test_NULLs(self):
        """
        Unit test to ensure there are no rows in the cleaned tables with NULL values.

        This test checks all tables in the database for rows with NULL values.
        """
        # Fetch table names
        cur = self.cur
        cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cur.fetchall()]

        # Iterate over tables and check for NULLs
        for table in tables:
            query = f"SELECT * FROM {table}"
            df = pd.DataFrame(cur.execute(query).fetchall(), columns=[col[0] for col in cur.description])

            # Identify rows with NULLs
            df_missing = df[df.isnull().any(axis=1)]
            cnt_missing = len(df_missing)

            try:
                assert cnt_missing == 0, f"There are {cnt_missing} rows with NULLs in the `{table}` table."
            except AssertionError as ae:
                logger.error("Test failed for table `%s`: %s", table, ae)
                raise ae
            else:
                logger.info("No NULLs found in the `%s` table.", table)
                print(f"No NULLs found in the `{table}` table.")

    def test_num_cols(self, local_df, db_table_name):
        """
        Unit test to ensure that the number of columns in the cleaned DataFrame match the
        number of columns in the SQLite3 database table.

        Parameters:
            local_df (DataFrame): DataFrame of the cleansed table
            db_table_name (str): Name of the table in the clean SQLite database

        Returns:
            None
        """
        # Fetch table schema from SQLite
        cur = self.cur
        cur.execute(f"PRAGMA table_info({db_table_name});")
        db_columns = [col[1] for col in cur.fetchall()]  # Second field is the column name

        try:
            assert len(local_df.columns) == len(db_columns), (
                f"Column count mismatch: DataFrame ({len(local_df.columns)} columns) vs "
                f"Database table '{db_table_name}' ({len(db_columns)} columns)"
            )
        except AssertionError as ae:
            logger.exception(ae)
            raise
        else:
            logger.info(f"Column count matches for table '{db_table_name}'.")

    def test_schema(self, local_df, db_table_name):
        """
        Unit test to ensure that the column dtypes in the cleaned DataFrame match the
        column dtypes in the SQLite3 database table.

        Parameters:
            local_df (DataFrame): DataFrame of the cleansed table
            db_table_name (str): Name of the table in the clean SQLite database

        Returns:
            None
        """
        # Fetch table schema from SQLite
        cur = self.cur
        cur.execute(f"PRAGMA table_info({db_table_name});")
        db_schema = {col[1]: col[2] for col in cur.fetchall()}  # Map: column name -> data type

        # Map SQLite dtypes to Pandas dtypes
        sqlite_to_pandas = {
            "INTEGER": "int64",
            "REAL": "float64",
            "TEXT": "object",
            "NUMERIC": "float64",
            "BLOB": "object",  # Pandas doesn't directly handle BLOB types
        }

        errors = []
        for col in local_df.columns:
            if col not in db_schema:
                errors.append(f"Column '{col}' is missing in database schema.")
                continue

            db_dtype = sqlite_to_pandas.get(db_schema[col], "unknown")
            if str(local_df[col].dtype) != db_dtype:
                errors.append(f"Column '{col}': DataFrame dtype '{local_df[col].dtype}' "
                              f"does not match database dtype '{db_dtype}'.")

        try:
            assert not errors, f"Schema mismatches found:\n" + "\n".join(errors)
        except AssertionError as ae:
            logger.exception(ae)
            raise
        else:
            logger.info(f"Schema matches for table '{db_table_name}'.")
   
