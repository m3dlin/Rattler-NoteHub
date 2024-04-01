"""
This module will contain helper functions that pertain to using the MySQL database.
The developer must create an .env file with the format stated in the README.md
which contains the credientials of the DB.
"""

from sqlalchemy import create_engine, text, Column, Integer, String, TIMESTAMP, Boolean
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv
load_dotenv()
import os
import bcrypt
import datetime
# Reads credentials from the config file
user = os.getenv('DB_USER')
password = os.getenv('DB_PASSWORD')
host = os.getenv('DB_HOST')
port = os.getenv('DB_PORT')
dbname = os.getenv('DB_NAME')

db_connection_string = f"mysql://{user}:{password}@{host}:{port}/{dbname}?charset=utf8mb4"

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
session = Session()
Base = declarative_base()

# used for getting database info with reflection
# metadata = MetaData(bind=engine)
# metadata.reflect()

#########################################################################################################
# classes used to connect to database
class Student(Base):
    __tablename__ = 'Student'
    studentId = Column(Integer, primary_key=True)
    firstName = Column(String(255))
    lastName = Column(String(255))
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    
    def set_password(self, password):
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())


class Note(Base):
    __tablename__ = 'Note'
    noteId = Column(Integer, primary_key=True)
    courseId = Column(String(255))
    title = Column(String(255))
    created_at = Column(TIMESTAMP)
    description = Column(String(255))
    studentId = Column(Integer, nullable=False)
    visibility = Column(Boolean)
    upvotes = Column(Integer, nullable=True)
    downvotes = Column(Integer, nullable=True)
    file_path = Column(String(255))

    def get_student_name(self):
        return get_student_name(self.studentId) 

class Note_Tags(Base):
    __tablename__ = 'Note_Tags'
    nt_id = Column(Integer, primary_key=True)
    noteId = Column(Integer, nullable=False)
    tagId = Column(Integer, nullable=False)

class Enrolls_For(Base):
    __tablename__ = 'Enrolls_For'
    enrollId = Column(Integer, primary_key=True)
    courseId = Column(Integer, nullable=False)
    studentId = Column(Integer, nullable=False)

class Course(Base):
    __tablename__ = "Course"
    courseId = Column(String(255), primary_key=True)
    courseName = Column(String(255), nullable=False)
    courseNoteCount = Column(Integer)

#########################################################################################################

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

# gets the student and courses they are enrolled for using the email logged into the session
def get_student_info(email):
    session = Session()
    student = session.query(Student).filter_by(email=email).first() 
    courses=[] #list of courses student is enrolled in
    with engine.connect() as conn:
        result = conn.execute(text(f"SELECT C.courseId, C.courseName FROM Enrolls_For E JOIN Course C ON E.courseId = C.courseId WHERE E.studentId = {student.studentId}"))
        for row in result.all():
            course_info = {"id": row[0], "name": row[1]}
            courses.append(course_info)
    return student,courses

def get_student_name(studentId):
    with engine.connect() as conn:
        # Execute the query to fetch the student's first name and last name
        result = conn.execute(text(f"SELECT firstName, lastName FROM Student WHERE studentId = {studentId}"))    
        student_info = result.fetchone()

        first_name = student_info[0]
        last_name = student_info[1]
        full_name = first_name + " " + last_name

    return full_name


# gets the course ID and name
def get_course_details(course_id):
    with engine.connect() as conn:
        result = conn.execute(text("SELECT courseId, courseName FROM Course WHERE courseId = :course_id"), {"course_id": course_id})
        row = result.fetchone()
        if row:
            return {"id": row[0], "name": row[1]}
        else:
            return None

# hard coding adding note to database
def add_note_to_db(url):
    new_note = Note(
        courseId='EN 1311',
        title='Poem example',
        created_at=datetime.datetime.now(),
        description='testing uploading pdfs to database. This is a poem sample',
        studentId= 123456,
        visibility=True,
        file_path=url
    )
    session.add(new_note)
    session.commit()


# gets specific note based off the noteId
def get_note(noteId):
    note = session.query(Note).filter_by(noteId=noteId).first()
    return note

# gets all the notes from the user based off the email
def get_user_notes(email):
    session = Session()
    student = session.query(Student).filter_by(email=email).first() 
    notes_list=[] #list of notes that the student is linked to
    with engine.connect() as conn:
        result = conn.execute(text(f"select * from Note where studentId = {student.studentId}"))
        for row in result.all():
            # creating note object and inserting all information about the note
            note = Note()
            note.noteId = row[0]
            note.courseId = row[1] 
            note.title = row[2]
            formatted_created_at = row[3].strftime('%B %d, %Y') # formatting the date to look cleaner to the user: Month day, year
            note.created_at = formatted_created_at
            note.description = row[4]
            note.studentId = row[5]
            note.visibility = row[6]
            note.upvotes = row[7]
            note.downvotes = row[8]
            note.file_path = row[9]            
            # adding note to the list of notes
            notes_list.append(note)
    
    return notes_list

# must implement this after adding bookmarks to the DB
def get_bookmarked_notes(email):
    return None

# getting the list of tags from a note
# the variable note is a Note object
def get_note_tags(note):
    note_id = note.noteId
    tag_ids = []
    tag_names = []
    with engine.connect() as conn:
        result = conn.execute(text(f"select tagId from Note_Tags where noteId = {note_id}"))
        # for each tag found, add it to the tag_ids list
        for row in result.all():
            tag_ids.append(row[0])
        # for each tag in tag_ids get the corresponding name for the tag
        for tag in tag_ids:
            result2 = conn.execute(text(f"select tagName from Tag where tagId = {tag}"))
            tag_name = result2.fetchone()[0]
            tag_names.append(tag_name)

    return tag_names

# adding courses from the selected_course list, and adding them to the database
def add_courses_to_user(selected_courses, email):
    student = session.query(Student).filter_by(email=email).first() 
    with engine.connect() as conn:
        # deleting previously enrolled classes
        conn.execute(text(f"DELETE FROM Enrolls_For WHERE studentId = {student.studentId}"))

        # adding new course list to the enrolled classes
        for course in selected_courses:
            new_course = session.query(Course).filter_by(courseId=course).first()
            if new_course:
                enrolls_for = Enrolls_For(studentId=student.studentId, courseId=new_course.courseId)
                session.add(enrolls_for)
        session.commit()

# adding student to the database
def add_student_to_db(student):
    session.add(student)
    session.commit()

# checks to see if an account has already been made with an existing ID
def check_student_id(id):
    # if there's an account with the same id return true
    if session.query(Student).filter_by(studentId=id).first():
        return True
    return False


"""
# testing
if __name__ == '__main__': 
    print(check_student_id(123456))
"""
