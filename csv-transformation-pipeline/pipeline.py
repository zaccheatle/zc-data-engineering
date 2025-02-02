

# import dependencies
from bs4 import BeautifulSoup
import csv
import datetime
import numpy as np
import logging
import os
import pandas as pd
import re
import requests
import sys
import time
import unittest


# ------------------------------------ Logging

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.DEBUG,  # Ensure all logs appear
    handlers=[
        logging.FileHandler("pipeline.log"),  # Log to file
        logging.StreamHandler()  # Log to console
    ]
)

# ------------------------------------ self.data Pipeline Steps

## base class to initialize time and file size tracking
class BasePipeline:
    def __init__(self, file_path):
        """Initialize file tracking and start time."""
        self.file_path = file_path
        self.file_size = os.path.getsize(file_path)
        self.start_time = time.time()

    def track_step(self, step_name):
        """Allow step tracking using `with` statement (context manager)."""
        return StepTimer(step_name)  # Return an instance of StepTimer

class StepTimer:
    """Context manager to measure step execution time."""
    def __init__(self, step_name):
        self.step_name = step_name

    def __enter__(self):
        self.start_time = time.time()  # Start timer
        logging.info(f"Starting {self.step_name}...")
        return self  # Allows `as` keyword if needed

    def __exit__(self, exc_type, exc_value, traceback):
        elapsed_time = time.time() - self.start_time
        logging.info(f"{self.step_name} completed in {elapsed_time:.2f} seconds.")
        logging.info("")
    
## class to extract self.data from a csv
class DataExtractor(BasePipeline):
    def __init__(self, file_path):
        """Initialize BasePipeline and prepare DataExtractor."""
        super().__init__(file_path)

    def read_csv(self):
        """Read data from CSV and return as a DataFrame."""
        try:
            self.data = pd.read_csv(self.file_path)
            input_file_size = os.path.getsize(self.file_path) / (1024 * 1024)
            logging.info(f"Initial file size: {input_file_size} MB.")
            logging.info(f"Successfully read {len(self.data)} rows from {self.file_path}.")
            return self.data
        except FileNotFoundError:
            logging.error(f"File not found: {self.file_path}")
            return pd.DataFrame()
        except Exception as e:
            logging.error(f"error occurred trying to open csv: {e}")
            return pd.DataFrame()

class DataTransformer(BasePipeline):
    def __init__(self, file_path):
        super().__init__(file_path)

    def remove_dupes(self):
        """Removes duplicate rows from self.data."""
        if hasattr(self, 'data') and not self.data.empty:
            original_size = len(self.data)
            self.data.drop_duplicates(inplace=True)
            logging.info(f"Removed {original_size - len(self.data)} duplicate rows.")

    def clean_text_columns(self):
        """Cleans and formats text columns."""
        if hasattr(self, 'data') and not self.data.empty:
            str_cols = self.data.select_dtypes(include=['object']).columns
            self.data[str_cols] = self.data[str_cols].apply(lambda x: x.str.strip().str.replace(r'\s+', ' ', regex=True).str.title())
            self.data[str_cols] = self.data[str_cols].apply(lambda x: x.str.strip()
                                                        .replace(r'^\s*[-_]*\s*$', 'UNKNOWN', regex=True)  # Replace various blank-like values
                                                        .fillna('UNKNOWN'))  # Ensure NaN values are also replaced
    def clean_numeric_columns(self):
        """Cleans all numeric columns by removing non-numeric characters and ensuring proper format."""
        if hasattr(self, 'data') and not self.data.empty:
            
            # Identify columns that contain numbers but are stored as text
            numeric_like_cols = self.data.select_dtypes(include=['object']).columns  

            for col in numeric_like_cols:
                if self.data[col].str.contains(r'^\$?\d+[\d,]*\.?\d*$', regex=True, na=False).all():
                    logging.info(f"Cleaning numeric-like column: {col}")

                    # Remove $ and commas
                    self.data[col] = self.data[col].str.replace(r'[$,]', '', regex=True)

                    # Convert to numeric
                    self.data[col] = pd.to_numeric(self.data[col], errors='coerce')

            # Select actual numeric columns (int/float) after conversion
            numeric_cols = self.data.select_dtypes(include=['int64', 'float64']).columns  

            for col in numeric_cols:
                self.data[col] = self.data[col].fillna(0)  # Fill NaN values with 0
                
                # Convert to int if all values are whole numbers
                if all(self.data[col] % 1 == 0):
                    self.data[col] = self.data[col].astype(int)

            logging.info(f"Final cleaned numeric columns: {list(numeric_cols)}")

    def clean_boolean_columns(self):
        """Standardizes Boolean columns to True/False without affecting non-Boolean text columns."""
        if hasattr(self, 'data') and not self.data.empty:
            
            # Identify potential Boolean-like columns
            bool_like_cols = []

            for col in self.data.select_dtypes(include=['object']).columns:
                unique_values = self.data[col].dropna().str.strip().str.lower().unique()
                
                # Check if column contains only boolean-like values
                if set(unique_values).issubset({'yes', 'no', 'true', 'false', '1', '0'}):
                    bool_like_cols.append(col)

            # Convert only Boolean-like columns
            for col in bool_like_cols:
                self.data[col] = self.data[col].str.strip().str.lower().replace({
                    'yes': True, 'no': False,
                    'true': True, 'false': False,
                    '1': True, '0': False
                })

                # Convert to actual Boolean dtype
                self.data[col] = pd.to_numeric(self.data[col], errors='coerce').astype('boolean')

            logging.info(f"Final cleaned Boolean columns: {bool_like_cols}")

    def add_last_modified(self):
        """Adds a 'last_modified' column."""
        if hasattr(self, 'data') and not self.data.empty:
            self.data['last_modified'] = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')

## class to output transformed data to a clean csv
class DataSaver(BasePipeline):
    def __init__(self, file_path):
        super().__init__(file_path)

    def save_csv(self, output_path="clean.csv"):
        """Saves transformed self.data to a CSV file."""
        if hasattr(self, 'data') and not self.data.empty:
            try:
                self.data.to_csv(output_path, index=False)
                clean_file_size = os.path.getsize(output_path) / (1024 * 1024)  # Convert size to MB
                logging.info(f"Clean CSV file '{output_path}' created successfully.")
                logging.info(f"Output File Size: {clean_file_size:.2f} MB")
                return output_path
            except Exception as e:
                logging.error(f"Error saving CSV file: {e}")
                return None
        else:
            logging.critical("Dataframe is empty, nothing to process.")
            return None

# ----------------------------------------------------------- Class to run pipeline process
class DataPipeline:
    def __init__(self, file_path):
        """Initialize the pipeline and all components."""
        self.file_path = file_path
        self.extractor = DataExtractor(file_path)
        self.transformer = DataTransformer(file_path)
        self.saver = DataSaver(file_path)
        self.start_time = time.time()

    def run_pipeline(self):
        """Execute the full self.data pipeline with time tracking."""
        logging.info("Initializing csv pipeline")
        logging.info("")

        ## Track extraction time
        with self.extractor.track_step("Extraction"):
            self.extractor.read_csv()  # Extracts data into self.extractor.data

        ## Pass extracted data to transformer
        self.transformer.data = self.extractor.data  # Pass extracted data

        ## If extracted data is empty, exit
        if self.transformer.data is None or self.transformer.data.empty:
            logging.critical("Pipeline terminated: No data extracted.")
            sys.exit(1)  # Exit process with an error code

        ## Track transformation time
        with self.transformer.track_step("Transformation"):
            self.transformer.remove_dupes()
            self.transformer.clean_text_columns()
            self.transformer.clean_numeric_columns()
            self.transformer.clean_boolean_columns()

        ## If transformed data is empty, exit
        if self.transformer.data is None or self.transformer.data.empty:
            logging.critical("Pipeline terminated: No data after transformations.")
            sys.exit(1)  # Exit process if transformations result in an empty DataFrame

        ## Pass transformed data to saver
        self.saver.data = self.transformer.data  # Pass transformed data

        ## Track saving time
        with self.saver.track_step("Saving"):
            self.saver.save_csv(f"{os.path.splitext(os.path.basename(self.file_path))[0]}-output.csv")

        ## Log total pipeline time
        total_time = time.time() - self.start_time
        logging.info(f"Pipeline execution complete!")
        logging.info(f"Total pipeline execution time: {total_time:.2f} seconds")

