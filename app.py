from flask import Flask, request, jsonify
from flask_restx import Api, Resource, fields
from flask_jwt_extended import JWTManager

app = Flask(__name__)
api = Api(app)
jwt = JWTManager(app)

# Define the student model
student_model = api.model('Student', {
    'id': fields.Integer(required=True, description='The student ID'),
    'name': fields.String(required=True, description='The student name'),
    'age': fields.Integer(required=True, description='The student age'),
    'email': fields.String(required=True, description='The student email')
})

# Define the data model for courses
course_model = api.model('Course', {
    'id': fields.Integer(required=True, description='The course identifier'),
    'name': fields.String(required=True, description='The name of the course'),
    'teacher': fields.String(required=True, description='The name of the course teacher'),
    'students': fields.List(fields.String, description='The list of registered students')
})

# Define the data model for grades
grade_model = api.model('Grade', {
    'student_id': fields.Integer(required=True, description='The ID of the student'),
    'course_id': fields.Integer(required=True, description='The ID of the course'),
    'grade': fields.Float(required=True, description='The grade of the student in the course')
})


# Create a list of students to simulate a database
students = [
    {'id': 1, 'name': 'John', 'age': 18, 'email': 'john@example.com'},
    {'id': 2, 'name': 'Jane', 'age': 19, 'email': 'jane@example.com'}
]

# Create a list of courses to simulate a database
courses = [
    {'id': 1, 'name': 'Soil Science', 'teacher': 'Professor Kamal M.', 'students': ['Musa, Audu, Gerrard, Lucy']},
    {'id': 2, 'name': 'Introduction to Python', 'teacher': 'Professor Caleb', 'students': ['Maryam, Joseph, Abiola']}
]

# Create a list of grades to simulate a database
grades = [
    {'student_id': 1, 'course_id': 1, 'grade': 90},
    {'student_id': 2, 'course_id': 1, 'grade': 85},
    {'student_id': 2, 'course_id': 2, 'grade': 92},
    {'student_id': 3, 'course_id': 2, 'grade': 88},
    {'student_id': 1, 'course_id': 3, 'grade': 91},
    {'student_id': 3, 'course_id': 3, 'grade': 95},
]

# Endpoint for creating a new student
@api.route('/students')
class StudentList(Resource):
    @api.marshal_with(student_model)
    def get(self):
        return students

    @api.expect(student_model)
    @api.marshal_with(student_model)
    def post(self):
        new_student = request.json
        new_student['id'] = len(students) + 1
        students.append(new_student)
        return new_student, 201

# Endpoint for reading, updating, and deleting a student by ID
@api.route('/students/<int:id>')
@api.response(404, 'Student not found')
class Student(Resource):
    @api.marshal_with(student_model)
    def get(self, id):
        for student in students:
            if student['id'] == id:
                return student
        api.abort(404, f"Student {id} not found")

    @api.expect(student_model)
    @api.marshal_with(student_model)
    def put(self, id):
        for student in students:
            if student['id'] == id:
                updated_student = request.json
                updated_student['id'] = id
                students.remove(student)
                students.append(updated_student)
                return updated_student
        api.abort(404, f"Student {id} not found")

    def delete(self, id):
        for student in students:
            if student['id'] == id:
                students.remove(student)
                return '', 204
        api.abort(404, f"Student {id} not found")

# Define the endpoint for retrieving all students, grades and calculating GPA
@api.route('/students')
class StudentList(Resource):
    def get(self):
        """Retrieve a list of all students"""
        return students
class Students(Resource):
    def get(self):
        results = []
        for student in set([s for c in courses for s in courses[c]]):
            student_courses = [c for c in courses if student in courses[c]]
            student_grades = [grades[c][student] for c in student_courses if student in grades[c]]
            gpa = sum(student_grades) / len(student_grades) if student_grades else None
            results.append({
                'student': student,
                'courses': student_courses,
                'grades': student_grades,
                'gpa': gpa
            })
        return results

# Define the endpoint for registering a new course
@api.route('/courses')
class CourseRegistration(Resource):
    @api.expect(course_model)
    def post(self):
        """Register a new course"""
        course = api.payload
        courses.append(course)
        return {'message': 'Course registered successfully'}, 201

# Define the endpoint for retrieving all courses
@api.route('/courses')
class CourseList(Resource):
    def get(self):
        """Retrieve a list of all courses"""
        return courses

# Define the endpoint for retrieving a specific course
@api.route('/courses/<int:course_id>')
class Course(Resource):
    def get(self, course_id):
        """Retrieve information about a specific course"""
        for course in courses:
            if course['id'] == course_id:
                return course
        api.abort(404, 'Course not found')

    def put(self, course_id):
        """Update information about a specific course"""
        for course in courses:
            if course['id'] == course_id:
                course.update(api.payload)
                return {'message': 'Course updated successfully'}
        api.abort(404, 'Course not found')

    def delete(self, course_id):
        """Delete a specific course"""
        for course in courses:
            if course['id'] == course_id:
                courses.remove(course)
                return {'message': 'Course deleted successfully'}
        api.abort(404, 'Course not found')

# Define the endpoint for retrieving students registered in a particular course
@api.route('/courses/<int:course_id>/students')
class CourseStudents(Resource):
    def get(self, course_id):
        """Retrieve a list of students registered in a particular course"""
        for course in courses:
            if course['id'] == course_id:
                return course['students']
        api.abort(404, 'Course not found')

# Define the endpoints for retrieving grades for each student in each course
@api.route('/grades')
class GradeList(Resource):
    @api.expect(grade_model)
    def post(self):
        """Add a new grade"""
        grade = api.payload
        grades.append(grade)
        return {'message': 'Grade added successfully'}, 201
    
    def get(self):
        """Retrieve a list of all grades"""
        return grades

@api.route('/students/<int:student_id>/grades')
class StudentGrades(Resource):
    def get(self, student_id):
        """Retrieve a list of grades for a particular student"""
        student_grades = []
        for grade in grades:
            if grade['student_id'] == student_id:
                student_grades.append(grade)
        return student_grades


if __name__ == '__main__':
    app.run(debug=True)