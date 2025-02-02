from pipeline import DataPipeline  # Import your DataPipeline class

if __name__ == "__main__":
    input_file = "marvel_characters_info.csv"  # Ensure this file exists in your working directory
    pipeline = DataPipeline(input_file)  # Create an instance of DataPipeline
    pipeline.run_pipeline()  # Execute the pipeline