from abc import ABC, abstractmethod
from typing import Dict, List

#Абстрактный класс
class Person(ABC):
    def __init__(self, first_name: str, last_name :str, age: int, phone: str,
                 email: str, user_id: int, role: str):
        self.first_name = first_name
        self.last_name = last_name
        self.age = age
        self.phone = str(phone)
        self.email = email
        self.user_id = user_id
        self.role = role
    @abstractmethod
    def to_dict(self) -> Dict:
        return {
            "first_name": self.first_name,
            "last_name": self.last_name,
            "age": self.age,
            "phone": self.phone,
            "email": self.email,
            "user_id": self.user_id,
            "role": self.role
        }

    def display_info(self):
        pass



class Student(Person):
    def __init__(self, first_name: str, last_name :str, age: int, phone: str,
                 email: str, user_id: int, role: str, grade: int):
         super().__init__(first_name, last_name, age, phone, email, user_id, role)
         self.grade = grade
         self.enrolled_courses: List[str] = []

    def display_info(self):
        print(f"Студент: {self.first_name} {self.last_name}")
        print(f"Класс: {self.grade}")
        print(f"Курсов записано: {len(self.enrolled_courses)}")

    def choose_a_course(self, course:'Course'):
        course.add_student(self)
        self.enrolled_courses.append(course)
    def get_course(self):
        return self.enrolled_courses

    def view_the_schedule(self, schedule: 'Schedule'):
        return schedule

class Tutor(Person):
    def __init__(self, first_name: str, last_name :str, age: int, phone: str,
                 email: str, user_id: int, role: str, subject: str,  experience: int, bio: str):
         super().__init__(first_name, last_name, age, phone, email, user_id, role)
         self.subject = subject
         self.experience = experience
         self.bio = bio
         self.courses_taught: List[str] = []

    def display_info(self):
        print(f"Репетитор: {self.first_name} {self.last_name}")
        print(f"Предмет: {self.subject}")
        print(f"Опыт: {self.experience} лет")


    def create_course(self, name: str, subject: str, description: str,
                 time: str, price: str, status: str) -> 'Course':
        course = Course(name=name, tutor=self, subject=subject,  # передай все параметры
                        description=description, time=time, price=price, status=status)
        self.courses_taught.append(course)
        return course

    def view_the_schedule(self, schedule: 'Schedule'):
        return schedule

class Course():
    def __init__(self, name: str, tutor: Tutor, subject: str, description: str,
                 time: str, price: str, status: str):
        self.name = name
        self.tutor = tutor
        self.subject = subject
        self.description = description
        self.time = time
        self.price = price
        self.status = status
        self.students = []
        self.lesson = []

    def add_student(self,student: Student):
        self.students.append(student)
    def get_lessons(self):
        return self.lesson
    def get_students(self):
        return self.students
    def change_status(self,new_status: str):
        self.status = new_status
    def add_lessons(self, new_lesson: str):
        self.lesson.append(new_lesson)

class Schedule():
    def __init__(self, student: Student, tutor: Tutor):
        self.student = student
        self.tutor = tutor
        self.lessons = []

    def add_lesson(self, new_lesson: str):
        self.lessons.append(new_lesson)

    def cancel_lesson(self, name_lesson):
        self.lessons.remove(name_lesson)




