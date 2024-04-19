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
    
class Tag(Base):
    __tablename__ = 'Tag'
    tagId = Column(Integer, primary_key=True)
    tagName = Column(String(255))

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

class Bookmark(Base):
    __tablename__ = "Bookmark"
    bookmarkId = Column(Integer, primary_key=True)
    noteId = Column(Integer)
    studentId = Column(Integer)

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

def get_student_id(email):
    student = session.query(Student).filter_by(email=email).first() 
    return student.studentId


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
def add_note_to_db(courseId, title, description, studentId, visibility, tag, url):
    
    if visibility == 'Public':
        visibility_status = True
    else:
        visibility_status = False
    
    new_note = Note(
        courseId=courseId,
        title=title,
        created_at=datetime.datetime.now(),
        description=description,
        studentId= studentId,
        visibility= visibility_status,
        file_path=url
    )
    session.add(new_note)
    session.commit()

    new_tag = get_tag_id(tagName=tag)

    new_note_tags = Note_Tags(
        noteId=new_note.noteId,
        tagId=new_tag.tagId
    )
    session.add(new_note_tags)
    session.commit()
    return True


# gets specific note based off the noteId
def get_note(noteId):
    note = session.query(Note).filter_by(noteId=noteId).first()
    return note

# gets all the notes from the user based off the email
def get_user_notes(email):
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

# gets all bookmarked notes based on the user
def get_bookmarked_notes(email):
    student = session.query(Student).filter_by(email=email).first() 
    bookmark_list = [] #list of bookmarked notes that the student is linked to
    with engine.connect() as conn:
        result = conn.execute(text(f"select noteId from Bookmark where studentId = {student.studentId}"))
        for note_id in result.all():
            note_result = conn.execute(text(f"select * from Note where noteId = {note_id[0]}"))
            for row in note_result.all():
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
                # adding note to the bookmark list
                bookmark_list.append(note)

    return bookmark_list

# gets all the notes that are related to a specific course
def get_course_notes(courseId):
    notes_list = []
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM Note WHERE courseId = :course_id"), {'course_id': courseId})

        # collecting all the note objects and adding them to a list
        for row in result.all():

            # collecting only notes set to Public
            if(row[6] == True):
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

def get_course_notes_with_tags(courseId, tag):
    notes_list = []
    with engine.connect() as conn:
        if tag == "All Tags":
            result = conn.execute(text("SELECT * FROM Note WHERE courseId = :course_id"), {'course_id': courseId})
        else:
            tag_id = get_tag_id(tagName=tag).tagId
            result = conn.execute(text("SELECT Note.* FROM Note JOIN Note_Tags ON Note.noteId = Note_Tags.noteId WHERE Note.courseId = :course_id AND Note_Tags.tagId = :tag_id;"), 
                {'course_id': courseId, 'tag_id':tag_id})

        # collecting all the note objects and adding them to a list
        for row in result.all():

            # collecting only notes set to Public
            if(row[6] == True):
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



# get the total amount of notes for a specific course
def get_note_count(courseId):
    result = session.execute(text("select count(*) as note_count from Note where courseId = :course_id and visibility = 1"),{'course_id': courseId}).fetchone()
    note_count = result[0] 
    return note_count



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


def get_tag_id(tagName):
    tag = session.query(Tag).filter_by(tagName=tagName).first() 
    return tag


# adding courses from the selected_course list, and adding them to the database
def add_courses_to_user(selected_courses, email):
    student = session.query(Student).filter_by(email=email).first() 

    # deleting previously enrolled classes
    session.query(Enrolls_For).filter_by(studentId=student.studentId).delete()
    with session.no_autoflush:
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

# get list of all tags currently in the database
def get_list_of_tags():
    tags = []
    with engine.connect() as conn:
        result = conn.execute(text(f"select tagName from Tag"))
        for row in result.all():
            tags.append(row[0])
    return tags


# tags comes from Note_Tags
def update_selected_note(noteId, title, description, tag, visibility):
    note = session.query(Note).filter_by(noteId=noteId).first()
    
    # if the note is found
    if note:
        # update the fields with new values
        note.title = title
        
        # deleting previous tag
        session.query(Note_Tags).filter_by(noteId=noteId).delete()
        # adding new note tag
        tag = session.query(Tag).filter_by(tagName=tag).first() # get tag id by the name that was passed
        new_tag = Note_Tags(noteId=noteId, tagId=tag.tagId)
        session.add(new_tag)

        note.description = description
        if visibility == 'Public':
            note.visibility = True
        else:
            note.visibility = False
        session.commit()
        return True # return that the update was successful
    else:
        return False

def delete_selected_note(noteId):
    note = session.query(Note).filter_by(noteId=noteId).first()
    
    # if the note is found
    if note:
        # try to delete note, if it does not detect the note in the DB, then rollback query and return false
        try:
            session.query(Note).filter_by(noteId=note.noteId).delete()
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            return False
    else:
        return False


def increment_upvotes(noteId):
    note = session.query(Note).filter_by(noteId=noteId).first()
    if note.upvotes == None:
        note.upvotes = 1
    else:
        note.upvotes += 1
    session.commit()
    return note.upvotes

def increment_downvotes(noteId):
    note = session.query(Note).filter_by(noteId=noteId).first()
    if note.downvotes == None:
        note.downvotes = 1
    else:
        note.downvotes += 1
    session.commit()
    return note.downvotes

def add_bookmark(noteId, email):
    note = session.query(Note).filter_by(noteId=noteId).first()
    student = session.query(Student).filter_by(email=email).first()

    if note and student:
        existing_bookmark = session.query(Bookmark).filter_by(noteId=note.noteId, studentId=student.studentId).first()
        if existing_bookmark:
            return True  # bookmark already exists for this student and note, do not duplicate entry
        else:
            new_bookmark = Bookmark(noteId=note.noteId, studentId=student.studentId)
            session.add(new_bookmark)
            session.commit()
            return True # return true since bookmark was added
    else:
        return False # note/student not found

def delete_bookmark(noteId, email):
    note = session.query(Note).filter_by(noteId=noteId).first()
    student = session.query(Student).filter_by(email=email).first()
    
    if note and student:
        existing_bookmark = session.query(Bookmark).filter_by(noteId=note.noteId, studentId=student.studentId).first()
        if existing_bookmark:
            session.delete(existing_bookmark)
            session.commit()
            return True # return true since bookmark was deleted
        else:
            return True # return true even though the bookmark was not found, it means that there's no bookmark to begin with
    else:
        return False  # note/student not found

def check_bookmark_status(noteId, email):
    student = session.query(Student).filter_by(email=email).first()
    bookmark = session.query(Bookmark).filter_by(noteId=noteId,studentId=student.studentId).first()
    if bookmark:
        return True
    else:
        return False



"""
# testing
if __name__ == '__main__': 
    print('test')

"""




