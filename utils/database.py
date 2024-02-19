"""
This module will contain helper functions that pertain to using the MySQL database.
The developer must create an .env file with the format stated in the README.md
which contains the credientials of the DB.
"""

from sqlalchemy import create_engine, MetaData, text
from dotenv import load_dotenv
load_dotenv()
import os
# Reads credentials from the config file
user = os.getenv('DB_USER')
password = os.getenv('DB_PASSWORD')
host = os.getenv('DB_HOST')
dbname = os.getenv('DB_NAME')

db_connection_string = f"mysql+pymysql://{user}:{password}@{host}/{dbname}?charset=utf8mb4"

engine = create_engine(
    db_connection_string,
    connect_args={
        "ssl": {
            "ssl_ca": "/etc/ssl/cert.pem"
        }
    }
)


# function for testing purposes
def test_database_connection(course_ids, course_names):
    metadata = MetaData()
    metadata.reflect(bind=engine)

    # Print the list of table names
    print("Tables in the database:")
    for table_name in metadata.tables.keys():
        print(table_name)

    with engine.connect() as conn:
        for id,name in zip(course_ids,course_names):
            query = text('insert into Course (courseId, courseName, courseNoteCount)'
                            'values (:course_id, :course_name, :course_note_count)')
            conn.execute(query,{
                'course_id': id,
                'course_name':name,
                'course_note_count': 0
            })
    

# function used in stmu_scraper.py
"""
def add_courses_to_DB(course_ids,course_names):
    with engine.connect() as conn:
        for id,name in zip(course_ids,course_names):
            query = text('insert into Course (courseId, courseName, courseNoteCount)'
                         'values (:course_id, :course_name, :course_note_count)')
            conn.execute(query,{
                'course_id': id,
                'course_name':name,
                'course_note_count': 0
            })
"""


# function to get all course numbers
def get_course_nums():
    courses=[] #list of course numbers
    with engine.connect() as conn:
        result = conn.execute(text("select courseId from Course"))
        for row in result.all():
            courses.append(row[0])
        return courses

"""
# testing
if __name__ == '__main__': 
    print('this is a test')
"""