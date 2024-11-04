#!/usr/bin/env python
# coding: utf-8

# # Data Pipeline Portfolio Project

# ### **Objective**: build a data engineering pipeline to regularly transform a messy database into a clean source of truth for an analytics team.
# ### **Data Source:** Cademycode customer data
# ### **Data Format**: sqlite3 Database
# #### **Author**: Zac Cheatle

# In[1]:


# import dependencies
import os
import pandas as pd
import numpy as np
import json
import sqlite3
import logging

# set pandas column width
pd.set_option('display.max_colwidth', None)


# In[2]:


# connect to sqlite3 db 

con = sqlite3.connect('cademycode.db')

curs = con.cursor()


# In[3]:


# view tables

curs.execute('''SELECT name FROM sqlite_master WHERE type='table';''').fetchall()


# In[4]:


# import tables to dataframes (could do this with a loop but since only 3 tables going to do this 1 by 1)

# students
students = pd.read_sql_query('SELECT * FROM cademycode_students', con)
students.head(5)


# In[5]:


# import tables to dataframes

# courses
courses = pd.read_sql_query('SELECT * FROM cademycode_courses', con)
courses.head(5)


# In[6]:


# import tables to dataframes

# student jobs
student_jobs = pd.read_sql_query('SELECT * FROM cademycode_student_jobs', con)
student_jobs.head(5)


# ## Data Prep

# #### Shape

# In[7]:


students.shape


# In[8]:


courses.shape


# In[9]:


student_jobs.shape


# #### Column clean up

# In[10]:


# split contact_info column into separate email and address columns
students['contact_info'] = students['contact_info'].apply(lambda x: json.loads(x) if isinstance(x, str) else x)
students['mailing_address'] = students['contact_info'].apply(lambda x: x.get('mailing_address') if isinstance(x, dict) else None)
students['email'] = students['contact_info'].apply(lambda x: x.get('email') if isinstance(x, dict) else None)

# split up mailing address into separate columns
students[['address', 'city', 'state', 'zip']] = students['mailing_address'].str.extract(r'^(.*),\s*([\w\s]+),\s*([\w\s]+),\s*(\d+)$')


# In[11]:


# drop original contact_info column
students = students.drop(columns=['mailing_address'])
students = students.drop(columns=['contact_info'])
students.head()


# #### Duplicates

# In[12]:


students.duplicated().value_counts()


# In[13]:


courses.duplicated().value_counts()


# In[14]:


student_jobs.duplicated().value_counts()


# In[15]:


student_jobs=student_jobs.drop_duplicates(keep='last')


# In[16]:


student_jobs.duplicated().value_counts()


# #### Missing Values

# In[17]:


students.isnull().sum()


# In[18]:


# drop all rows with a null value
students = students.dropna()


# In[19]:


students.shape


# In[20]:


courses.isnull().sum()


# In[21]:


student_jobs.isnull().sum()


# #### Data Types

# In[22]:


students.dtypes


# In[23]:


### set datatypes

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

students = students.astype(dtype_dict)
students.dtypes


# In[24]:


students['num_course_taken'] = students['num_course_taken'].astype(int)
students['job_id'] = students['job_id'].astype(int)
students['current_career_path_id'] = students['current_career_path_id'].astype(int)
students.head()


# In[25]:


courses.dtypes


# In[26]:


student_jobs.dtypes


# ## Export Cleaned Data

# #### Create new sqlite3 database with cleaned tables

# In[27]:


new_conn = sqlite3.connect('cleaned_cademycode.db')

students.to_sql('students', new_conn, index=False, if_exists='replace')
courses.to_sql('courses', new_conn, index=False, if_exists='replace')
student_jobs.to_sql('student_jobs', new_conn, index=False, if_exists='replace')


# #### Create csv with all tables merged together for analysts

# In[28]:


students_courses = students.merge(courses, left_on='current_career_path_id', right_on='career_path_id', how='left')
cleaned_cademycode_data = students_courses.merge(student_jobs, on='job_id', how='left')
cleaned_cademycode_data.drop(['career_path_id'], axis=1, inplace=True)
cleaned_cademycode_data.head()


# In[29]:


# create csv

cleaned_cademycode_data.to_csv('cleaned_cademycode_data', index=False)


# In[30]:


#### commit and close db connections

con.close()

new_conn.commit()
new_conn.close()


# In[ ]:



# Logging Set Up
import logging

## Change log
change_log = logging.getLogger('ChangeLog')
change_handler = logging.FileHandler('changelog.log')
change_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
change_log.addHandler(change_handler)
change_log.setLevel(logging.INFO)

## Error Log Set Up
error_log = logging.getLogger('ErrorLog')
error_handler = logging.FileHandler('errorlog.log')
error_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
error_log.addHandler(error_handler)
error_log.setLevel(logging.ERROR)


# log updates to the changelog
def log_changes(update_type, details):
    change_log.info(f"{update_type} - {details}")


# check for status updates in db
def check_for_updates(db_path, last_update_time):
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(updated_at) FROM your_table")
        latest_update = cursor.fetchone()[0]
        return latest_update > last_update_time
        

# if updates are detected, log them
if check_for_updates('your_database.db', last_update_time):
    log_changes('Database Update', 'Updates detected and processed.')

