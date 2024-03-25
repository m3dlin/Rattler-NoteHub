"""
This module is used to retrieve all courses from StMU's current catalog
Used at the beginning of development.
Do NOT run again, this will lead to duplicate classes
"""

import requests
from bs4 import BeautifulSoup
import time  
import unidecode
from sqlalchemy import create_engine, MetaData
import os
from database import add_courses_to_DB

def get_course_info(url):
    response = requests.get("https://catalog.stmarytx.edu"+url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        courseId_list = []
        course_name_list = []

        #starting div
        sc_div = soup.find('div',{"class": "sc_sccoursedescs"})

        #all titles of the courses
        courses = sc_div.find_all('p', {'class':'courseblocktitle'})

        # retrieving the abbreviation + course number and the name of the class for each course title
        for course in courses:
            course_text = course.text
            
            # find index of the first period in the text
            first_period_index = course_text.find('.')

            # find index of the second period in the text
            second_period_index = course_text.find('.', first_period_index + 2)
            
            # get all text up to the desired period (excludes period)
            course_id = course_text[:first_period_index] 
            course_name = course_text[first_period_index + 2:second_period_index]

            # .strip() removes leading/trailing whitespace
            # unidecode convert all non-ASCII characters to their closest ASCII equivalent (in this case \xa0 turns to a space)
            courseId_list.append(unidecode.unidecode(course_id.strip().replace(" ","")))  
            course_name_list.append(course_name.strip())
        
        return courseId_list, course_name_list

    else:
        print('Failed to fetch the courses for ' + str(url))
    return
    

def main():
    url = 'https://catalog.stmarytx.edu/undergraduate/course-descriptions/'
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        #starting div
        atoz_div = soup.find('div', {'id': 'atozindex'})

        # ul is labeled a to z
        unordered_lists = atoz_div.find_all('ul')

        # for each letter in unordered_lists, get the departments
        for ul in unordered_lists:
            departments = ul.find_all('li')

            # for each department, go to the dept. page and retrieve all courses
            for department in departments:
                department_url = department.find('a') # a tags have hyperlinks to dept page
                course_ids = []
                course_names = []

                # as long as there is a url for the department, get course numbers
                if department_url:
                    department_url = department_url['href']
                    course_ids,course_names = get_course_info(department_url)

                    """
                    if course_ids:
                        print(f'Courses for {department.text}:')
                        for id,name in zip(course_ids,course_names):
                            print(id + ' ' + name)
                        print('---')
                    else:
                        print(f'No course numbers found for {department.text}')
                    """

                    time.sleep(3) # timer is used so that the code does not overload the website with requests

                add_courses_to_DB(course_ids, course_names)
                print('added to database')
    else:
        print('Failed to fetch the web page')
    

"""
if __name__ == "__main__":
    main()
"""

