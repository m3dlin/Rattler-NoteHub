"""
This module will contain helper functions that pertain to using the MySQL database.
The developer must create an .env file with the format stated in the README.md
which contains the credientials of the DB.
"""

from sqlalchemy import create_engine, MetaData, text, Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv
load_dotenv()
import os
import bcrypt
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
# used for getting database info with ORM (Object-Relational Mapping)
Session = sessionmaker(bind=engine)
Base = declarative_base()

# used for getting database info with reflection
# metadata = MetaData(bind=engine)
# metadata.reflect()

# classes used to connect to database
class Student(Base):
    __tablename__ = 'Student'
    studentId = Column(Integer, primary_key=True)
    firstName = Column(String(255))
    lastName = Column(String(255))
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)

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


# function to check login info with users in the database
def check_credentials(email, password):
    # new database connection
    session = Session()
    # query on Student table, and filtering the results by email. The first means the first result that matches
    student = session.query(Student).filter_by(email=email).first() 

    # checks if the student exists and compares the student password with the password entered in the form.
    if student and bcrypt.checkpw(password.encode('utf-8'),student.password.encode('utf-8')):
        session.close()
        return True # true if credentials align with database
    else:
        session.close()
        return False

def get_student_info(email):
    session = Session()
    student = session.query(Student).filter_by(email=email).first() 
    courses=[] #list of courses student is enrolled in
    with engine.connect() as conn:
        result = conn.execute(text(f"select courseId from Enrolls_For where studentId = {student.studentId}"))
        for row in result.all():
            courses.append(row[0])
    return student,courses

"""
# testing
if __name__ == '__main__': 
    print("test")
"""
