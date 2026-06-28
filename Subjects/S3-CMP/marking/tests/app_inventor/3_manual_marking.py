import uuid
import time
import requests
import pandas as pd

SCHOOLOGY_KEY = "883e26c227bc0f9997e86018811aaf4b064f56abf"
SCHOOLOGY_SECRET = "cbb414f36f77ba2a7f25470a62cc2a01"

YEAR = "23-24"
SUBJECT = "CMP"


def get_authorization_header():
    """
    Authorization: OAuth realm="Schoology API",
    oauth_consumer_key="dpf43f3p2l4k3l03",
    oauth_token="",
    oauth_nonce="kllo9940pd9333jh",
    oauth_timestamp="1200376800",
    oauth_signature_method="PLAINTEXT",
    oauth_version="1.0",
    oauth_signature="kd94hf93k423kf44%26"
    """
    return 'OAuth realm="Schoology API",' \
           'oauth_consumer_key="%s",' \
           'oauth_token="%s",' \
           'oauth_nonce="%s",' \
           'oauth_timestamp="%s",' \
           'oauth_signature_method="PLAINTEXT",' \
           'oauth_version="1.0",' \
           'oauth_signature="%s%%26%s"' % (SCHOOLOGY_KEY, "", uuid.uuid4(), str(
               int(round(time.time()))), SCHOOLOGY_SECRET, "")


def get_section_enrollments(section_id, user_id=""):
    """
    GET /v1/sections/{id}/enrollments
    """
    params = "&uid=" + str(user_id) if user_id != "" else ""
    url = "https://api.schoology.com/v1/sections/%d/enrollments?limit=200%s" % (
        int(section_id), params)
    headers = {
        'Authorization': get_authorization_header()
    }
    response = requests.get(url, headers=headers)
    return response.json()['enrollment']


def get_course_sections(course_id):
    """
    GET /v1/sections
    """
    # url = "https://api.schoology.com/v1/courses/{course_id}/sections"
    url = "https://api.schoology.com/v1/courses/%s/sections" % course_id
    headers = {
        'Authorization': get_authorization_header()
    }
    response = requests.get(url, headers=headers)
    return response.json()['section']


def get_schools():
    """
    GET /v1/schools
    """
    url = "https://api.schoology.com/v1/schools"
    headers = {
        'Authorization': get_authorization_header()
    }
    response = requests.get(url, headers=headers)
    return response.json()['school'][0]


def get_school_buildings(school_id):
    """
    GET /v1/schools/{id}/buildings
    """
    url = "https://api.schoology.com/v1/schools/%d/buildings" % school_id
    headers = {
        'Authorization': get_authorization_header()
    }
    response = requests.get(url, headers=headers)
    return response.json()['building'][0]


def get_courses_per_page(page=0):
    """
    GET /v1/courses?limit=200
    """
    page_size = 200
    url = "https://api.schoology.com/v1/courses?limit=200&start=%d" % (
        page * page_size)
    headers = {
        'Authorization': get_authorization_header()
    }
    response = requests.get(url, headers=headers)
    json = response.json()
    return pd.DataFrame(json['course'])


def get_all_courses():
    page = 0
    courses_pd = pd.DataFrame()
    while True:
        page_courses = get_courses_per_page(page)
        if page_courses.empty:
            break
        courses_pd = pd.concat([courses_pd, page_courses], ignore_index=True)
        page += 1

    return courses_pd


def get_course(course_id):
    """
    GET /v1/courses/{id}
    """
    url = "https://api.schoology.com/v1/courses/%d" % course_id
    headers = {
        'Authorization': get_authorization_header()
    }
    response = requests.get(url, headers=headers)
    return response.json()


def get_section_assignments(section_id):
    """
    GET /v1/sections/{section_id}/assignments
    """
    url = "https://api.schoology.com/v1/sections/%s/assignments" % section_id
    headers = {
        'Authorization': get_authorization_header()
    }
    response = requests.get(url, headers=headers)
    return response.json()['assignment']


def get_users_by_school_uids(stuids=[]):
    """
    GET /v1/users
    """
    # chunk 50 users per request
    size = 20
    if len(stuids) > size:
        users = []
        for i in range(0, len(stuids), size):
            users += get_users_by_school_uids(stuids[i:i + size])
        return users
    else:
        params = "?school_uids=" + (",".join(map(str, stuids))) if len(stuids) > 0 else ""
        url = "https://api.schoology.com/v1/users" + params
        headers = {
            'Authorization': get_authorization_header()
        }
        response = requests.get(url, headers=headers)
        return response.json()['user']


def get_user(user_id):
    """
    GET /v1/users/{id}
    """
    url = "https://api.schoology.com/v1/users/%s" % user_id
    headers = {
        'Authorization': get_authorization_header()
    }
    response = requests.get(url, headers=headers)
    return response.json()


def get_submissions_per_page(section_id, grade_item_id, page):
    """
    GET /v1/sections/{section_id}/submissions/{grade_item_id}/
    """
    page_size = 200
    url = "https://api.schoology.com/v1/sections/%s/submissions/%s?with_attachments=1&limit=200&start=%d" % (
        section_id, grade_item_id, page * page_size)
    headers = {
        'Authorization': get_authorization_header()
    }
    response = requests.get(url, headers=headers)
    json = response.json()
    if 'revision' in json:
        return json['revision']
    else:
        return []


def get_all_submissions(section_id, grade_item_id):
    page = 0
    submissions_pd = pd.DataFrame()
    while True:
        page_submissions = get_submissions_per_page(section_id, grade_item_id, page)
        if page_submissions == []:
            break
        submissions_pd = pd.concat([submissions_pd, pd.DataFrame(page_submissions)], ignore_index=True)
        page += 1

    return submissions_pd


def get_all_assignments_from_course(course_id):
    sections = get_course_sections(course_id)
    section = sections[0]
    assignments = get_section_assignments(section['id'])
    return section, assignments


def search_courses(keywords):
    courses = get_all_courses()
    # filter courses by keywords
    for keyword in keywords:
        courses = courses[courses['title'].str.contains(keyword)]
    # reindex courses
    courses = courses.reset_index(drop=True)
    return courses


def select_courses():
    # ask for user to search for courses
    keywords = input("Enter keywords to search for courses: ").split()
    courses = search_courses(keywords)

    # show checkboxes to let user select courses
    print("Select courses for marking:")
    for index, course in courses.iterrows():
        print("%d. %s" % (index, course['title']))
    selected_courses = input(
        "Enter course numbers separated by space: ").split()
    selected_courses = [int(i) for i in selected_courses]
    return courses, selected_courses


def select_assignments(courses, selected_courses):
    # show assignments of each course
    selected_assignment_ids = []
    for course_index in selected_courses:
        course = courses.iloc[course_index]
        print("Course: %s" % course['title'])
        section, assignments = get_all_assignments_from_course(course['id'])
        # ask user to select assignment
        print("Select assignment:")
        for index, assignment in enumerate(assignments):
            print("%d. %s" % (index, assignment['title']))
        selected_assignment = int(input("Enter assignment number: "))
        assignment = assignments[selected_assignment]
        print("Assignment: %s" % assignment['title'])
        selected_assignment_ids.append(
            (section['id'], assignment['id'], assignment['title']))
    return selected_assignment_ids


def check_input_data(df):
    # assert column class, class_no, assignment_name, marks, comments exists
    error = False
    if 'class' not in df.columns:
        print("Error: column 'class' not found")
        error = True
    if 'class_no' not in df.columns:
        print("Error: column 'class_no' not found")
        error = True
    if 'assignment_name' not in df.columns:
        print("Error: column 'assignment_name' not found")
        error = True
    if 'marks' not in df.columns:
        print("Error: column 'marks' not found")
        error = True
    if 'comments' not in df.columns:
        print("Error: column 'comments' not found")
        error = True
    return not error

    # get the list of class, class_no, section_id, assignment_id, enrollment_id


def get_class_list():
    courses, selected_courses = select_courses()
    if len(selected_courses) == 0:
        print("No courses found")
        exit()
    elif len(selected_courses) > 1:
        print("Please select only one course")
        exit()
    selected_assignment_ids = select_assignments(courses, selected_courses)
    if len(selected_assignment_ids) == 0:
        print("No assignments found")
        exit()
    elif len(selected_assignment_ids) > 1:
        print("Please select only one assignment")
        exit()

    # get the list of class, class_no, enrollment_id
    class_list = []
    section_id, assignment_id = selected_assignment_ids[0][0], selected_assignment_ids[0][1]
    submissions = get_all_submissions(section_id, assignment_id)
    for index, submission in submissions.iterrows():
        print(submission)
        user = get_user(submission['uid'])
        enrollments = get_section_enrollments(section_id, submission['uid'])
        if (len(enrollments) != 1):
            print("Error: enrollments length != 1")
            return
        classno = user['name_last']
        enrollment_id = enrollments[0]['id']
        class_list.append(
            (user['name_first'], user['name_last'], classno, section_id, assignment_id, enrollment_id))
    return class_list


def check_class_list(class_list):
    courses = search_courses([YEAR, SUBJECT])
    # check each class in class_list are exist in courses
    error = False
    for c in class_list:
        if not courses['title'].str.contains(c).any():
            print("Error: class %s not found" % c)
            error = True
    return not error


def get_course_ids_by_class_list(class_list):
    courses = search_courses([YEAR, SUBJECT])
    # check each class in class_list are exist in courses
    course_ids = []
    for c in class_list:
        course = courses[courses['title'].str.contains(c)].iloc[0]
        course_ids.append(course['id'])
    return course_ids


def get_section_id_and_assignment_id(course_id, assignment_name):
    section, assignments = get_all_assignments_from_course(course_id)
    if (len([a for a in assignments if a['title'] == assignment_name]) == 0):
        print("Error: assignment %s not found! But found:" % assignment_name)
        for a in assignments:
            print(a['title'])
        return "", ""
        # exit()
    assignment = [a for a in assignments if a['title'] == assignment_name][0]
    return section['id'], assignment['id']


def manual_mark():
    # import data from csv file
    df = pd.read_csv('manual_marking/data.csv')
    if (not check_input_data(df)):
        exit()

    # get student_id from student_data.csv
    print("Getting stuid...")
    student_data = pd.read_csv('student_data/student_data.csv')
    # change column name from 'number' to 'class_no'
    student_data = student_data.rename(columns={'number': 'class_no'})
    student_data = student_data[['stuid', 'class', 'class_no']]
    student_data['stuid'] = student_data['stuid'].astype(str)
    df = pd.merge(df, student_data, on=['class', 'class_no'], how='left')

    # get unique class list
    print("Getting course_id...")
    class_list = df[['class']].drop_duplicates()
    cl = class_list['class'].to_list()
    if (not check_class_list(cl)):
        exit()
    course_ids = get_course_ids_by_class_list(cl)
    class_list['course_id'] = course_ids
    df = pd.merge(df, class_list, on=['class'], how='left')

    # get section_id, assignment_id for each class
    print("Getting section_id and assignment_id...")
    class_assignment_list = df[['course_id', 'assignment_name']].drop_duplicates()
    class_assignment_list = class_assignment_list.reset_index(drop=True)
    class_assignment_list['section_id'] = ""
    class_assignment_list['assignment_id'] = ""
    for index, row in class_assignment_list.iterrows():
        print("--> %d/%d" % (index, len(class_assignment_list)))
        course_id = row['course_id']
        assignment_name = row['assignment_name']
        section_id, assignment_id = get_section_id_and_assignment_id(course_id, assignment_name)
        if section_id == "" or assignment_id == "":
            # delete row if section_id or assignment_id not found
            class_assignment_list.drop(index, inplace=True)
            continue
        class_assignment_list.at[index, 'section_id'] = section_id
        class_assignment_list.at[index, 'assignment_id'] = assignment_id
    df = pd.merge(df, class_assignment_list, on=['course_id', 'assignment_name'], how='left')
    print(df)

    # get enrollment_id for each class
    print("Getting enrollment_id...")
    all_enrollments = pd.DataFrame()
    for index, row in class_assignment_list.iterrows():
        print("--> %d/%d" % (index, len(class_assignment_list)))
        section_id = row['section_id']
        assignment_id = row['assignment_id']
        enrollments = get_section_enrollments(section_id)
        enrollments = pd.DataFrame(enrollments)
        enrollments = enrollments[['school_uid', 'id']]
        enrollments = enrollments.rename(columns={'school_uid': 'stuid'})
        enrollments = enrollments.rename(columns={'id': 'enrollment_id'})
        enrollments['section_id'] = section_id
        enrollments['assignment_id'] = assignment_id
        all_enrollments = pd.concat([all_enrollments, enrollments], ignore_index=True)
    df = pd.merge(df, all_enrollments, on=['stuid', 'section_id', 'assignment_id'], how='left')
    df.to_csv('marksheet.csv', index=False)
    print(df)


manual_mark()
