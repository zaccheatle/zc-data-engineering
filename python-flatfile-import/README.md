Python PostgreSQL Flatfile Import Tool
=

## Description:
Dynamic Python script that allows the user to create a custom database in a PostgreSQL RDS instance in AWS from a folder of flatfiles (.csv, .xlsx format only). 

## Features:
* Packaged as an executable with a user friendly interface to enable technical and non-technical users alike
* Saves the time of manually creating SQL tables from multiple files
* Checks if database name already exists, if not, database is created
* Processes larges files in chunks of 1000 rows
* Logs progress to the console and any errors to a log file

## Technologies:
* AWS RDS
* Python
* SQL
