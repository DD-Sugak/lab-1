from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Optional
import json
import xml.etree.ElementTree as ET
from xml.dom import minidom

class EducationException(Exception):
    ##Базовое исключение для системы образования
    pass

class UserNotFoundException(EducationException):
    ##Пользователь не найден
    pass

class CourseNotFoundException(EducationException):
    ##Курс не найден
    pass

class PaymentException(EducationException):
    ##Ошибка оплаты
    pass

class EnrollmentException(EducationException):
    ##Ошибка записи на курс
    pass

class LessonException(EducationException):
    ##Ошибка урока
    pass


#Абстрактный класс
class Person(ABC):
    def __init__(self, first_name: str, last_name :str, age: int, phone: str,
                 email: str, user_id: int, role: str):

        self._validate_person_data(first_name, last_name, email, phone, age)

        self.first_name = first_name
        self.last_name = last_name
        self.age = age
        self.phone = str(phone)
        self.email = email
        self.user_id = user_id
        self.role = role

    @abstractmethod

    def _validate_person_data(self, first_name: str, last_name: str, email: str, phone: str, age: int):

        if not first_name.replace("-", "").isalpha():
            raise EducationException("Имя должно содержать только буквы")

        if not last_name.replace("-", "").isalpha():
            raise EducationException("Фамилия должна содержать только буквы")

        if "@" not in email:
            raise EducationException("Некорректный email")

        if age < 0 or age > 100:
            raise EducationException("Некорректный возраст")


    def _validate_and_normalize_phone(self, phone: str) -> str:

        clean_phone = ''.join(c for c in phone if c.isdigit())

        if len(clean_phone) < 10:
            raise EducationException("Некорректный номер телефона")

        if len(clean_phone) > 11:
            raise EducationException("Некорректный номер телефона")

        if len(clean_phone) == 10:
            if clean_phone.startswith('9'):
                normalized_phone = '8' + clean_phone
            else:
                raise EducationException("Некорректный номер телефона")

        elif len(clean_phone) == 11:
            if clean_phone.startswith('7'):
                normalized_phone = '8' + clean_phone[1:]
            elif clean_phone.startswith('8'):
                normalized_phone = clean_phone
            else:
                raise EducationException("Некорректный номер телефона")
        else:
            raise EducationException("Некорректный номер телефона")

        return normalized_phone

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

    @classmethod
    def from_dict(cls, data: Dict) -> 'Person':
        return cls(
            first_name=data["first_name"],
            last_name=data["last_name"],
            age=data["age"],
            phone=data["phone"],
            email=data["email"],
            user_id=data["user_id"],
            role=data["role"]
        )

    def to_xml(self) -> 'ET.Element':
        person_elem = ET.Element("person")
        ET.SubElement(person_elem, "first_name").text = self.first_name
        ET.SubElement(person_elem, "last_name").text = self.last_name
        ET.SubElement(person_elem, "age").text = str(self.age)
        ET.SubElement(person_elem, "phone").text = self.phone
        ET.SubElement(person_elem, "email").text = self.email
        ET.SubElement(person_elem, "user_id").text = str(self.user_id)
        ET.SubElement(person_elem, "role").text = self.role
        return person_elem

    @classmethod
    def from_xml(cls, person_elem: ET.Element) -> 'Person':
        ##Создать человека из XML элемента
        return cls(
            first_name=person_elem.find("first_name").text,
            last_name=person_elem.find("last_name").text,
            age=int(person_elem.find("age").text),
            phone=person_elem.find("phone").text,
            email=person_elem.find("email").text,
            user_id=int(person_elem.find("user_id").text),
            role=person_elem.find("role").text
        )

    def display_info(self):
        pass



class Student(Person):
    def __init__(self, first_name: str, last_name :str, age: int, phone: str,
                 email: str, user_id: int, grade: int):

        if grade < 1 or grade > 11:
            raise EducationException("Некорректный класс")

        super().__init__(first_name, last_name, age, phone, email, user_id, "student")
        self.grade = grade
        self.enrolled_courses: List[Course] = []
        self.schedule = Schedule(student=self)

    def display_info(self):
        print(f"Студент: {self.first_name} {self.last_name}")
        print(f"Класс: {self.grade}")
        print(f"Курсов записано: {len(self.enrolled_courses)}")

    def choose_a_course(self, course:'Course'):

        if not isinstance(course, Course):
            raise EnrollmentException("Можно записываться только на существующие курсы")

        if course in self.enrolled_courses:
            raise EnrollmentException(f"Вы уже записаны на курс '{course.name}'")

        course.add_student(self)
        self.enrolled_courses.append(course)

    def get_course(self):
        return self.enrolled_courses

    def view_the_schedule(self):
        self.schedule.display_schedule()

    def to_dict(self) -> Dict:
        data = super().to_dict()
        data.update({
            "grade": self.grade,
            "enrolled_courses": [course.name for course in self.enrolled_courses]
        })
        return data

    @classmethod
    def from_dict(cls, data: Dict) -> 'Student':
        student = cls(
            first_name=data["first_name"],
            last_name=data["last_name"],
            age=data["age"],
            phone=data["phone"],
            email=data["email"],
            user_id=data["user_id"],
            grade=data["grade"]
        )

        # enrolled_courses мы восстановим позже, когда загрузим все курсы
        return student

    def to_xml(self) -> 'ET.Element':
        student_elem = super().to_xml()
        student_elem.tag = "student"  # меняем тег на student

        ET.SubElement(student_elem, "grade").text = str(self.grade)

        # Добавляем список курсов
        courses_elem = ET.SubElement(student_elem, "enrolled_courses")
        for course in self.enrolled_courses:
            ET.SubElement(courses_elem, "course").text = course.name

        return student_elem

    @classmethod
    def from_xml(cls, student_elem: ET.Element) -> 'Student':
        ##Создать студента из XML элемента
        student = cls(
            first_name=student_elem.find("first_name").text,
            last_name=student_elem.find("last_name").text,
            age=int(student_elem.find("age").text),
            phone=student_elem.find("phone").text,
            email=student_elem.find("email").text,
            user_id=int(student_elem.find("user_id").text),
            grade=int(student_elem.find("grade").text)
        )

        # enrolled_courses восстановим позже
        return student


class Tutor(Person):
    def __init__(self, first_name: str, last_name :str, age: int, phone: str,
                 email: str, user_id: int, role: str, subject: str,  experience: int, bio: str):
         super().__init__(first_name, last_name, age, phone, email, user_id, "tutor")

         if not subject or not subject.strip():
             raise EducationException("Предмет не может быть пустым")

         if experience < 0:
             raise EducationException("Опыт не может быть отрицательным")

         self.subject = subject
         self.experience = experience
         self.bio = bio
         self.courses_taught: List[Course] = []
         self.schedule = Schedule(tutor=self)


    def display_info(self):
        print(f"Репетитор: {self.first_name} {self.last_name}")
        print(f"Предмет: {self.subject}")
        print(f"Опыт: {self.experience} лет")


    def create_course(self, name: str, subject: str, description: str,
                 time: str, month_price: str, status: str) -> 'Course':

        if not name or not name.strip():
            raise EducationException("Название курса не может быть пустым")

        if not subject or not subject.strip():
            raise EducationException("Предмет курса не может быть пустым")

        try:
            price = float(''.join(c for c in month_price if c.isdigit() or c in ',.').replace(',', '.'))
            if price <= 0:
                raise EducationException("Стоимость курса должна быть больше 0")
        except ValueError:
            raise EducationException("Некорректная стоимость курса")

        valid_statuses = ["active", "completed", "cancelled"]
        if status not in valid_statuses:
            raise EducationException(f"Недопустимый статус. Допустимые: {', '.join(valid_statuses)}")

        course = Course(name=name, tutor=self, subject=subject,  # передай все параметры
                        description=description, time=time, price=price, status=status)
        self.courses_taught.append(course)
        return course

    def view_the_schedule(self):
        self.schedule.display_schedule()

    def to_dict(self) -> Dict:
        data = super().to_dict()
        data.update({
            "subject": self.subject,
            "experience": self.experience,
            "bio": self.bio,
            "courses_taught": [course.name for course in self.courses_taught]
        })
        return data

    @classmethod
    def from_dict(cls, data: Dict) -> 'Tutor':
        tutor = cls(
            first_name=data["first_name"],
            last_name=data["last_name"],
            age=data["age"],
            phone=data["phone"],
            email=data["email"],
            user_id=data["user_id"],
            role="tutor",
            subject=data["subject"],
            experience=data["experience"],
            bio=data["bio"]
        )

        # courses_taught восстановим позже
        return tutor

    def to_xml(self) -> 'ET.Element':
        tutor_elem = super().to_xml()
        tutor_elem.tag = "tutor"  # меняем тег на tutor

        ET.SubElement(tutor_elem, "subject").text = self.subject
        ET.SubElement(tutor_elem, "experience").text = str(self.experience)
        ET.SubElement(tutor_elem, "bio").text = self.bio

        # Добавляем список курсов
        courses_elem = ET.SubElement(tutor_elem, "courses_taught")
        for course in self.courses_taught:
            ET.SubElement(courses_elem, "course").text = course.name

        return tutor_elem

    @classmethod
    def from_xml(cls, tutor_elem: ET.Element) -> 'Tutor':
        ##Создать репетитора из XML элемента
        tutor = cls(
            first_name=tutor_elem.find("first_name").text,
            last_name=tutor_elem.find("last_name").text,
            age=int(tutor_elem.find("age").text),
            phone=tutor_elem.find("phone").text,
            email=tutor_elem.find("email").text,
            user_id=int(tutor_elem.find("user_id").text),
            role="tutor",
            subject=tutor_elem.find("subject").text,
            experience=int(tutor_elem.find("experience").text),
            bio=tutor_elem.find("bio").text
        )

        # courses_taught восстановим позже
        return tutor


class Course():
    def __init__(self, name: str, tutor: Tutor, subject: str, description: str,
                 time: str, month_price: str, status: str):

        if not name.strip():
            raise EducationException("Название курса не может быть пустым")

        if not isinstance(tutor, Tutor):
            raise EducationException("Курс должен быть привязан к репетитору")

        if not subject or not subject.strip():
            raise EducationException("Предмет курса не может быть пустым")

        self.name = name
        self.tutor = tutor
        self.subject = subject
        self.description = description
        self.time = time
        self.month_price = month_price
        self.status = status
        self.students = []
        self.lesson = []



    def add_student(self, student: Student):
        if not isinstance(student, Student):
            raise EnrollmentException("Только студенты могут записываться на курсы")

        if student in self.students:
            raise EnrollmentException(f"Студент {student.first_name} уже записан на этот курс")

        self.students.append(student)
        print(f"Студент {student.first_name} добавлен на курс {self.name}")

    def get_lessons(self):
        return self.lesson

    def get_students(self):
        return self.students

    def change_status(self,new_status: str):
        self.status = new_status

    def add_lessons(self, new_lesson: str):

        if not isinstance(new_lesson, Lesson):
            raise LessonException("Можно добавлять только объекты Lesson")

        if new_lesson in self.lesson:
            raise LessonException(f"Урок '{new_lesson.name}' уже есть в курсе")

        self.lesson.append(new_lesson)
        print(f"Урок '{new_lesson.name}' добавлен в курс '{self.name}'")

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "tutor": self.tutor.first_name + " " + self.tutor.last_name,
            "subject": self.subject,
            "description": self.description,
            "time": self.time,
            "month_price": self.month_price,
            "status": self.status,
            "students_count": len(self.students),
            "students": [student.first_name + " " + student.last_name for student in self.students],
            "lessons_count": len(self.lesson),
            "lessons": [lesson.to_dict() for lesson in self.lesson]  # все уроки курса
        }

    @classmethod
    def from_dict(cls, data: Dict, tutors: List[Tutor]) -> 'Course':
        tutor_name = data["tutor"]
        tutor = next((t for t in tutors if f"{t.first_name} {t.last_name}" == tutor_name), None)

        if not tutor:
            raise EducationException(f"Репетитор {tutor_name} не найден при загрузке курса")

        course = cls(
            name=data["name"],
            tutor=tutor,
            subject=data["subject"],
            description=data["description"],
            time=data["time"],
            month_price=data["month_price"],
            status=data["status"]
        )
        return course

    def to_xml(self) -> 'ET.Element':

        course_elem = ET.Element("course")

        ET.SubElement(course_elem, "name").text = self.name
        ET.SubElement(course_elem, "tutor").text = f"{self.tutor.first_name} {self.tutor.last_name}"
        ET.SubElement(course_elem, "subject").text = self.subject
        ET.SubElement(course_elem, "description").text = self.description
        ET.SubElement(course_elem, "time").text = self.time
        ET.SubElement(course_elem, "month_price").text = self.month_price
        ET.SubElement(course_elem, "status").text = self.status

        # Добавляем студентов курса
        students_elem = ET.SubElement(course_elem, "students")
        for student in self.students:
            ET.SubElement(students_elem, "student").text = f"{student.first_name} {student.last_name}"

        # Добавляем уроки курса
        lessons_elem = ET.SubElement(course_elem, "lessons")
        for lesson in self.lesson:
            lesson_elem = ET.SubElement(lessons_elem, "lesson")
            ET.SubElement(lesson_elem, "name").text = lesson.name
            ET.SubElement(lesson_elem, "date").text = lesson.date
            ET.SubElement(lesson_elem, "time").text = f"{lesson.start_time}-{lesson.end_time}"

        return course_elem

    @classmethod
    def from_xml(cls, course_elem: ET.Element, tutors: List[Tutor]) -> 'Course':
        ##Создать курс из XML элемента
        tutor_name = course_elem.find("tutor").text
        tutor = next((t for t in tutors if f"{t.first_name} {t.last_name}" == tutor_name), None)

        if not tutor:
            raise EducationException(f"Репетитор {tutor_name} не найден при загрузке курса")

        course = cls(
            name=course_elem.find("name").text,
            tutor=tutor,
            subject=course_elem.find("subject").text,
            description=course_elem.find("description").text,
            time=course_elem.find("time").text,
            month_price=course_elem.find("month_price").text,
            status=course_elem.find("status").text
        )

        return course


class Schedule():
    def __init__(self, student: Student, tutor: Tutor):
        self.student = student
        self.tutor = tutor
        self.lessons: List[Lesson] = []

    def add_lesson(self, lesson: 'Lesson'):

        if not isinstance(lesson, Lesson):
            raise EducationException("Можно добавлять только объекты Lesson")

        if lesson in self.lessons:
            raise EducationException(f"Урок '{lesson.name}' уже есть в расписании")

        self.lessons.append(lesson)
        print(f"Урок '{lesson.name}' добавлен в расписание")

    def get_upcoming_lessons(self):
        return sorted(self.lessons, key=lambda x: (x.date, x.start_time))

    def cancel_lesson(self, lesson_name: str):
        for lesson in self.lessons:
            if lesson.name == lesson_name:
                self.lessons.remove(lesson)
                print(f"Урок '{lesson_name}' отменен")
                return
        print(f"Урок '{lesson_name}' не найден")

    def get_upcoming_lessons(self):
        return self.lessons

    def get_lessons_by_date(self, date: str):
        day_lessons = [lesson for lesson in self.lessons if lesson.date == date]
        return sorted(day_lessons, key=lambda x: x.start_time)

    def display_schedule(self):
        person = self.student if self.student else self.tutor
        role = "Студент" if self.student else "Репетитор"
        print(f"Расписание {role}a {person.first_name}:")

        lessons_by_date = {}
        for lesson in self.get_upcoming_lessons():
            if lesson.date not in lessons_by_date:
                lessons_by_date[lesson.date] = []
            lessons_by_date[lesson.date].append(lesson)

        for date, day_lessons in lessons_by_date.items():
            print(f"\n {date}:")
            for lesson in day_lessons:
                print(f"   {lesson.start_time}-{lesson.end_time}: {lesson.name}")

    def to_dict(self) -> Dict:
        person = self.student if self.student else self.tutor
        return {
            "person": person.first_name + " " + person.last_name,
            "role": "student" if self.student else "tutor",
            "lessons_count": len(self.lessons),
            "upcoming_lessons": [
                {
                    "name": lesson.name,
                    "date": lesson.date,
                    "time": f"{lesson.start_time}-{lesson.end_time}"
                }
                for lesson in self.get_upcoming_lessons()[:5]
            ]
        }

    @classmethod
    def from_dict(cls, data: Dict, students: List[Student], tutors: List[Tutor], lessons: List['Lesson']) -> 'Schedule':
        # Находим человека (студента или репетитора)
        person_name = data["person"]
        role = data["role"]

        if role == "student":
            person = next((s for s in students if f"{s.first_name} {s.last_name}" == person_name), None)
            schedule = cls(student=person)
        else:
            person = next((t for t in tutors if f"{t.first_name} {t.last_name}" == person_name), None)
            schedule = cls(tutor=person)

        if not person:
            raise EducationException(f"Человек '{person_name}' не найден при загрузке расписания")

        # Восстанавливаем уроки
        for lesson_data in data.get("upcoming_lessons", []):
            lesson_name = lesson_data["name"]
            lesson = next((l for l in lessons if l.name == lesson_name), None)
            if lesson:
                schedule.add_lesson(lesson)

        return schedule

    def to_xml(self) -> 'ET.Element':
        schedule_elem = ET.Element("schedule")

        # Информация о владельце расписания
        if self.student:
            owner_elem = ET.SubElement(schedule_elem, "owner")
            owner_elem.set("type", "student")
            ET.SubElement(owner_elem, "name").text = f"{self.student.first_name} {self.student.last_name}"
        elif self.tutor:
            owner_elem = ET.SubElement(schedule_elem, "owner")
            owner_elem.set("type", "tutor")
            ET.SubElement(owner_elem, "name").text = f"{self.tutor.first_name} {self.tutor.last_name}"

        # Добавляем уроки
        lessons_elem = ET.SubElement(schedule_elem, "lessons")
        for lesson in self.lessons:
            lesson_elem = ET.SubElement(lessons_elem, "scheduled_lesson")
            ET.SubElement(lesson_elem, "name").text = lesson.name
            ET.SubElement(lesson_elem, "date").text = lesson.date
            ET.SubElement(lesson_elem, "time").text = f"{lesson.start_time}-{lesson.end_time}"
            ET.SubElement(lesson_elem, "course").text = lesson.course.name

        return schedule_elem

    @classmethod
    def from_xml(cls, schedule_elem: ET.Element, students: List[Student], tutors: List[Tutor],
                 lessons: List['Lesson']) -> 'Schedule':
        owner_elem = schedule_elem.find("owner")
        owner_type = owner_elem.get("type")
        owner_name = owner_elem.find("name").text

        if owner_type == "student":
            owner = next((s for s in students if f"{s.first_name} {s.last_name}" == owner_name), None)
            schedule = cls(student=owner)
        else:
            owner = next((t for t in tutors if f"{t.first_name} {t.last_name}" == owner_name), None)
            schedule = cls(tutor=owner)

        if not owner:
            raise EducationException(f"Владелец расписания '{owner_name}' не найден")

        # Восстанавливаем уроки
        lessons_elem = schedule_elem.find("lessons")
        if lessons_elem is not None:
            for lesson_elem in lessons_elem.findall("scheduled_lesson"):
                lesson_name = lesson_elem.find("name").text
                lesson = next((l for l in lessons if l.name == lesson_name), None)
                if lesson:
                    schedule.add_lesson(lesson)

        return schedule

class Lesson():
    def __init__(self,name: str, description: str, course: Course,
                 start_time: str, end_time: str, date: str):

        if not name.strip():
            raise EducationException("Название урока не может быть пустым")

        if not isinstance(course, Course):
            raise EducationException("Урок должен быть привязан к курсу")

        if start_time >= end_time:
            raise EducationException("Некорректный ввод времени")

        self.name = name
        self.description = description
        self.course = course
        self.start_time = start_time
        self.end_time = end_time
        self.date = date
        self.homeworks : List[Homework] = []

    def add_homework(self, homework: 'Homework'):
        self.homeworks.append(homework)

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "description": self.description,
            "course": self.course.name,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "date": self.date,
            "homeworks_count": len(self.homeworks)
        }

    @classmethod
    def from_dict(cls, data: Dict, courses: List[Course]) -> 'Lesson':
        """Создать урок из словаря"""
        # Находим курс
        course_name = data["course"]
        course = next((c for c in courses if c.name == course_name), None)
        if not course:
            raise EducationException(f"Курс '{course_name}' не найден при загрузке урока")

        lesson = cls(
            name=data["name"],
            description=data["description"],
            course=course,
            start_time=data["start_time"],
            end_time=data["end_time"],
            date=data["date"]
        )

        return lesson

    def to_xml(self) -> 'ET.Element':
        """Преобразовать урок в XML элемент"""
        lesson_elem = ET.Element("lesson")

        ET.SubElement(lesson_elem, "name").text = self.name
        ET.SubElement(lesson_elem, "description").text = self.description
        ET.SubElement(lesson_elem, "course").text = self.course.name
        ET.SubElement(lesson_elem, "start_time").text = self.start_time
        ET.SubElement(lesson_elem, "end_time").text = self.end_time
        ET.SubElement(lesson_elem, "date").text = self.date

        # Добавляем домашние задания
        homeworks_elem = ET.SubElement(lesson_elem, "homeworks")
        for homework in self.homeworks:
            hw_elem = ET.SubElement(homeworks_elem, "homework")
            ET.SubElement(hw_elem, "title").text = homework.title
            ET.SubElement(hw_elem, "deadline").text = homework.deadline

        return lesson_elem

    @classmethod
    def from_xml(cls, lesson_elem: ET.Element, courses: List[Course]) -> 'Lesson':
        course_name = lesson_elem.find("course").text
        course = next((c for c in courses if c.name == course_name), None)

        if not course:
            raise EducationException(f"Курс '{course_name}' не найден")

        lesson = cls(
            name=lesson_elem.find("name").text,
            description=lesson_elem.find("description").text,
            course=course,
            start_time=lesson_elem.find("start_time").text,
            end_time=lesson_elem.find("end_time").text,
            date=lesson_elem.find("date").text
        )

        return lesson

class Payment():
    def __init__(self, student: Student, month: str, year: int):

        if not isinstance(student, Student):
            raise PaymentException("Платеж должен быть привязан к студенту")

        if year < 2020 or year > 2030:
            raise PaymentException("Некорректный год")

        valid_months = ["январь", "февраль", "март", "апрель", "май", "июнь",
                        "июль", "август", "сентябрь", "октябрь", "ноябрь", "декабрь"]

        if month.lower() not in valid_months:
            raise PaymentException(f"Некорректный месяц. Допустимые: {', '.join(valid_months)}")

        self.student = student
        self.month = month
        self.year = year
        self.courses: List[Course] = []
        self.total_amount = 0.0
        self.status = "pending"
        self.payment_date = None

    def add_course(self, course: Course):

        if not isinstance(course, Course):
            raise PaymentException("Можно добавлять только объекты Course")

        if course in self.courses:
            raise PaymentException(f"Курс '{course.name}' уже добавлен в платеж")

        self.courses.append(course)
        self.total_amount += self._parse_price(course.month_price)

    def _parse_price(self, price_str: str) -> float:
        clean_price = ''.join(c for c in price_str if c.isdigit() or c in ',.')
        clean_price = clean_price.replace(',', '.')
        return float(clean_price)

    def process_payment(self):

        if not self.courses:
            raise PaymentException("Нет курсов для оплаты")

        if self.total_amount <= 0:
            raise PaymentException("Сумма оплаты должна быть больше 0")

        if self.status == "paid":
            raise PaymentException("Платеж уже обработан")

        self.status = "paid"
        self.payment_date = datetime.now()
        print(f"Оплата за {self.month} {self.year}: {len(self.courses)} курсов на сумму {self.total_amount} руб.")

    def get_payment_info(self):
        course_names = [course.name for course in self.courses]
        return f"Платеж за {self.month}: {', '.join(course_names)} - {self.total_amount} руб."

    def to_dict(self) -> Dict:
        return {
            "payment_info": {
                "month": self.month,
                "year": self.year,
                "total_amount": self.total_amount,
                "status": self.status,
                "payment_date": self.payment_date.isoformat() if self.payment_date else None
            },
            "student": self.student.first_name + " " + self.student.last_name,
            "student_id": self.student.user_id,
            "courses": [
                {
                    "name": course.name,
                    "price": course.month_price,
                    "tutor": course.tutor.first_name + " " + course.tutor.last_name
                }
                for course in self.courses
            ],
            "summary": {
                "courses_count": len(self.courses),
                "total_amount": self.total_amount,
                "is_paid": self.status == "paid"
            }
        }

    @classmethod
    def from_dict(cls, data: Dict, students: List[Student], courses: List[Course]) -> 'Payment':
        # Находим студента
        student_id = data["student_id"]
        student = next((s for s in students if s.user_id == student_id), None)
        if not student:
            raise EducationException(f"Студент с ID {student_id} не найден при загрузке платежа")

        payment = cls(
            student=student,
            month=data["payment_info"]["month"],
            year=data["payment_info"]["year"]
        )

        # Восстанавливаем статус и дату
        payment.status = data["payment_info"]["status"]
        if data["payment_info"]["payment_date"]:
            payment.payment_date = datetime.fromisoformat(data["payment_info"]["payment_date"])

        # Добавляем курсы
        for course_data in data["courses"]:
            course_name = course_data["name"]
            course = next((c for c in courses if c.name == course_name), None)
            if course:
                payment.add_course(course)

        return payment

    def to_xml(self) -> 'ET.Element':
        payment_elem = ET.Element("payment")

        # Основная информация
        info_elem = ET.SubElement(payment_elem, "payment_info")
        ET.SubElement(info_elem, "month").text = self.month
        ET.SubElement(info_elem, "year").text = str(self.year)
        ET.SubElement(info_elem, "total_amount").text = str(self.total_amount)
        ET.SubElement(info_elem, "status").text = self.status
        if self.payment_date:
            ET.SubElement(info_elem, "payment_date").text = self.payment_date.isoformat()

        # Информация о студенте
        student_elem = ET.SubElement(payment_elem, "student")
        ET.SubElement(student_elem, "name").text = f"{self.student.first_name} {self.student.last_name}"
        ET.SubElement(student_elem, "id").text = str(self.student.user_id)

        # Список курсов
        courses_elem = ET.SubElement(payment_elem, "courses")
        for course in self.courses:
            course_elem = ET.SubElement(courses_elem, "course")
            ET.SubElement(course_elem, "name").text = course.name
            ET.SubElement(course_elem, "price").text = course.month_price

        return payment_elem

    @classmethod
    def from_xml(cls, payment_elem: ET.Element, students: List[Student], courses: List[Course]) -> 'Payment':
        ##Создать платеж из XML элемента
        student_elem = payment_elem.find("student")
        student_id = int(student_elem.find("id").text)
        student = next((s for s in students if s.user_id == student_id), None)

        if not student:
            raise EducationException(f"Студент с ID {student_id} не найден")

        payment_info = payment_elem.find("payment_info")
        payment = cls(
            student=student,
            month=payment_info.find("month").text,
            year=int(payment_info.find("year").text)
        )

        payment.status = payment_info.find("status").text
        payment.total_amount = float(payment_info.find("total_amount").text)

        # Восстанавливаем дату платежа
        payment_date_elem = payment_info.find("payment_date")
        if payment_date_elem is not None and payment_date_elem.text:
            payment.payment_date = datetime.fromisoformat(payment_date_elem.text)

        # Добавляем курсы к платежу
        courses_elem = payment_elem.find("courses")
        if courses_elem is not None:
            for course_elem in courses_elem.findall("course"):
                course_name = course_elem.find("name").text
                course = next((c for c in courses if c.name == course_name), None)
                if course:
                    payment.add_course(course)

        return payment

class Homework():
    def __init__(self, title: str, description: str, lesson: Lesson,
                 deadline: str, max_score: int = 100):

        if not title.strip():
            raise EducationException("Название задания не может быть пустым")

        if not isinstance(lesson, Lesson):
            raise EducationException("Задание должно быть привязано к уроку")

        if max_score <= 0:
            raise EducationException("Максимальный балл должен быть больше 0")

        self.title = title
        self.description = description
        self.lesson = lesson
        self.deadline = deadline
        self.max_score = max_score
        self.attachments: List[str] = []
        self.student_submissions: Dict[Student, 'HomeworkSubmission'] = {}

    def to_dict(self) -> Dict:
        return {
            "title": self.title,
            "description": self.description,
            "lesson": self.lesson.name,
            "deadline": self.deadline,
            "max_score": self.max_score,
            "attachments_count": len(self.attachments),
            "submissions_count": len(self.student_submissions)
        }

    @classmethod
    def from_dict(cls, data: Dict, lessons: List[Lesson]) -> 'Homework':
        # Находим урок
        lesson_name = data["lesson"]
        lesson = next((l for l in lessons if l.name == lesson_name), None)
        if not lesson:
            raise EducationException(f"Урок '{lesson_name}' не найден при загрузке задания")

        homework = cls(
            title=data["title"],
            description=data["description"],
            lesson=lesson,
            deadline=data["deadline"],
            max_score=data["max_score"]
        )

        # Восстанавливаем вложения
        homework.attachments = data.get("attachments", [])

        return homework

    def to_xml(self) -> 'ET.Element':
        """Преобразовать домашнее задание в XML элемент"""
        homework_elem = ET.Element("homework")

        ET.SubElement(homework_elem, "title").text = self.title
        ET.SubElement(homework_elem, "description").text = self.description
        ET.SubElement(homework_elem, "lesson").text = self.lesson.name
        ET.SubElement(homework_elem, "deadline").text = self.deadline
        ET.SubElement(homework_elem, "max_score").text = str(self.max_score)

        # Добавляем вложения
        attachments_elem = ET.SubElement(homework_elem, "attachments")
        for attachment in self.attachments:
            ET.SubElement(attachments_elem, "file").text = attachment

        return homework_elem

    @classmethod
    def from_xml(cls, homework_elem: ET.Element, lessons: List[Lesson]) -> 'Homework':
        lesson_name = homework_elem.find("lesson").text
        lesson = next((l for l in lessons if l.name == lesson_name), None)

        if not lesson:
            raise EducationException(f"Урок '{lesson_name}' не найден")

        homework = cls(
            title=homework_elem.find("title").text,
            description=homework_elem.find("description").text,
            lesson=lesson,
            deadline=homework_elem.find("deadline").text,
            max_score=int(homework_elem.find("max_score").text)
        )

        # Восстанавливаем вложения
        attachments_elem = homework_elem.find("attachments")
        if attachments_elem is not None:
            for file_elem in attachments_elem.findall("file"):
                homework.attachments.append(file_elem.text)

        return homework

class HomeworkSubmission():
    def __init__(self, student: Student, homework: Homework,
                 answer: str, submitted_date: str):

        if not isinstance(student, Student):
            raise EducationException("Работа должна быть привязана к студенту")

        if not isinstance(homework, Homework):
            raise EducationException("Работа должна быть привязана к заданию")

        if not answer.strip():
            raise EducationException("Ответ не может быть пустым")

        self.student = student
        self.homework = homework
        self.answer = answer
        self.submitted_date = submitted_date
        self.score: Optional[int] = None  # оценка
        self.feedback: str = ""

    def set_score(self, score: int):
        if score < 0:
            raise EducationException("Оценка не может быть отрицательной")

        if score > self.homework.max_score:
            raise EducationException(f"Оценка не может превышать {self.homework.max_score}")

        self.score = score

    def get_score_percentage(self) -> float:
        if self.score is not None:
            return (self.score / self.homework.max_score) * 100
        return 0.0

    def get_grade_letter(self) -> str:
        percentage = self.get_score_percentage()
        if percentage >= 90:
            return "5"
        elif percentage >= 70:
            return "4"
        elif percentage >= 50:
            return "3"
        else:
            return "2"

    def to_dict(self) -> Dict:
        return {
            "student": self.student.first_name + " " + self.student.last_name,
            "homework": self.homework.title,
            "answer_preview": self.answer[:50] + "..." if len(self.answer) > 50 else self.answer,  # первые 50 символов
            "submitted_date": self.submitted_date,
            "score": self.score,
            "score_percentage": self.get_score_percentage(),
            "grade_letter": self.get_grade_letter(),
            "has_feedback": bool(self.feedback.strip())
        }

    @classmethod
    def from_dict(cls, data: Dict, students: List[Student], homeworks: List[Homework]) -> 'HomeworkSubmission':
        # Находим студента
        student_name = data["student"]
        student = next((s for s in students if f"{s.first_name} {s.last_name}" == student_name), None)
        if not student:
            raise EducationException(f"Студент '{student_name}' не найден при загрузке работы")

        # Находим задание
        homework_title = data["homework"]
        homework = next((h for h in homeworks if h.title == homework_title), None)
        if not homework:
            raise EducationException(f"Задание '{homework_title}' не найден при загрузке работы")

        submission = cls(
            student=student,
            homework=homework,
            answer=data["answer"],
            submitted_date=data["submitted_date"]
        )

        # Восстанавливаем оценку и комментарий
        submission.score = data.get("score")
        submission.feedback = data.get("feedback", "")

        return submission

    def to_xml(self) -> 'ET.Element':
        """Преобразовать сданную работу в XML элемент"""
        submission_elem = ET.Element("homework_submission")

        # Информация о студенте
        student_elem = ET.SubElement(submission_elem, "student")
        ET.SubElement(student_elem, "name").text = f"{self.student.first_name} {self.student.last_name}"
        ET.SubElement(student_elem, "id").text = str(self.student.user_id)

        # Информация о задании
        homework_elem = ET.SubElement(submission_elem, "homework")
        ET.SubElement(homework_elem, "title").text = self.homework.title

        ET.SubElement(submission_elem, "answer").text = self.answer
        ET.SubElement(submission_elem, "submitted_date").text = self.submitted_date

        if self.score is not None:
            ET.SubElement(submission_elem, "score").text = str(self.score)
            ET.SubElement(submission_elem, "score_percentage").text = str(self.get_score_percentage())
            ET.SubElement(submission_elem, "grade_letter").text = self.get_grade_letter()

        if self.feedback:
            ET.SubElement(submission_elem, "feedback").text = self.feedback

        return submission_elem

    @classmethod
    def from_xml(cls, submission_elem: ET.Element, students: List[Student],
                 homeworks: List[Homework]) -> 'HomeworkSubmission':
        student_elem = submission_elem.find("student")
        student_name = student_elem.find("name").text
        student = next((s for s in students if f"{s.first_name} {s.last_name}" == student_name), None)

        homework_elem = submission_elem.find("homework")
        homework_title = homework_elem.find("title").text
        homework = next((h for h in homeworks if h.title == homework_title), None)

        if not student or not homework:
            raise EducationException("Студент или задание не найдены")

        submission = cls(
            student=student,
            homework=homework,
            answer=submission_elem.find("answer").text,
            submitted_date=submission_elem.find("submitted_date").text
        )

        # Восстанавливаем оценку и комментарий
        score_elem = submission_elem.find("score")
        if score_elem is not None:
            submission.score = int(score_elem.text)

        feedback_elem = submission_elem.find("feedback")
        if feedback_elem is not None:
            submission.feedback = feedback_elem.text

        return submission

class Test():
    def __init__(self, title: str, lesson: Lesson):

        if not title.strip():
            raise EducationException("Название теста не может быть пустым")

        self.title = title
        self.lesson = lesson
        self.questions: List['Question'] = []

    def add_question(self, question: 'Question'):
        if not isinstance(question, Question):
            raise EducationException("Можно добавлять только объекты Question")
        self.questions.append(question)

    def calculate_score(self, user_answers: List[int]) -> int:

        if len(user_answers) != len(self.questions):
            raise EducationException("Количество ответов не совпадает с количеством вопросов")

        score = 0
        for i, question in enumerate(self.questions):
            if user_answers[i] == question.correct_answer:
                score += 1
        return score

    def to_dict(self) -> Dict:
        return {
            "title": self.title,
            "lesson": self.lesson.name,
            "questions_count": len(self.questions),
            "total_points": sum(1 for _ in self.questions)
        }

    @classmethod
    def from_dict(cls, data: Dict, lessons: List[Lesson]) -> 'Test':
        # Находим урок
        lesson_name = data["lesson"]
        lesson = next((l for l in lessons if l.name == lesson_name), None)
        if not lesson:
            raise EducationException(f"Урок '{lesson_name}' не найден при загрузке теста")

        test = cls(
            title=data["title"],
            lesson=lesson
        )

        return test

    def to_xml(self) -> 'ET.Element':
        """Преобразовать тест в XML элемент"""
        test_elem = ET.Element("test")

        ET.SubElement(test_elem, "title").text = self.title
        ET.SubElement(test_elem, "lesson").text = self.lesson.name

        # Добавляем вопросы
        questions_elem = ET.SubElement(test_elem, "questions")
        for question in self.questions:
            questions_elem.append(question.to_xml())

        return test_elem

    @classmethod
    def from_xml(cls, test_elem: ET.Element, lessons: List[Lesson]) -> 'Test':
        lesson_name = test_elem.find("lesson").text
        lesson = next((l for l in lessons if l.name == lesson_name), None)

        if not lesson:
            raise EducationException(f"Урок '{lesson_name}' не найден")

        test = cls(
            title=test_elem.find("title").text,
            lesson=lesson
        )

        # Загружаем вопросы
        questions_elem = test_elem.find("questions")
        if questions_elem is not None:
            for question_elem in questions_elem.findall("question"):
                question = Question.from_xml(question_elem)
                test.add_question(question)

        return test

class Question:
    def __init__(self, text: str, options: List[str], correct_answer: int):

        if not text.strip():
            raise EducationException("Текст вопроса не может быть пустым")

        if len(options) < 2:
            raise EducationException("Должно быть至少 2 варианта ответа")

        if correct_answer < 0 or correct_answer >= len(options):
            raise EducationException("Некорректный индекс правильного ответа")

        self.text = text
        self.options = options
        self.correct_answer = correct_answer

    def to_dict(self) -> Dict:
        return {
            "text": self.text,
            "options": self.options,
            "correct_answer_index": self.correct_answer,
            "correct_answer_text": self.options[self.correct_answer]
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Question':
        question = cls(
            text=data["text"],
            options=data["options"],
            correct_answer=data["correct_answer_index"]
        )

        return question

    def to_xml(self) -> 'ET.Element':
        question_elem = ET.Element("question")

        ET.SubElement(question_elem, "text").text = self.text

        # Добавляем варианты ответов
        options_elem = ET.SubElement(question_elem, "options")
        for i, option in enumerate(self.options):
            option_elem = ET.SubElement(options_elem, "option")
            option_elem.set("index", str(i))
            option_elem.text = option

        ET.SubElement(question_elem, "correct_answer").text = str(self.correct_answer)

        return question_elem

    @classmethod
    def from_xml(cls, question_elem: ET.Element) -> 'Question':
        options = []
        options_elem = question_elem.find("options")
        if options_elem is not None:
            for option_elem in options_elem.findall("option"):
                options.append(option_elem.text)

        return cls(
            text=question_elem.find("text").text,
            options=options,
            correct_answer=int(question_elem.find("correct_answer").text)
        )


class EducationSystem:
    def __init__(self):
        self.students: List[Student] = []
        self.tutors: List[Tutor] = []
        self.courses: List[Course] = []
        self.lessons: List[Lesson] = []
        self.homeworks: List[Homework] = []
        self.tests: List[Test] = []
        self.submissions: List[HomeworkSubmission] = []
        self.payments: List[Payment] = []
        self.schedules: List[Schedule] = []
        self.created_date = datetime.now()

    def add_student(self, student: Student):
        # Добавить студента в систему
        self.students.append(student)

    def add_tutor(self, tutor: Tutor):
        # Добавить репетитора в систему
        self.tutors.append(tutor)

    def add_course(self, course: Course):
        # Добавить курс в систему
        self.courses.append(course)

    def add_lesson(self, lesson: Lesson):
        # Добавить урок в систему
        self.lessons.append(lesson)

    def add_homework(self, homework: Homework):
        # Добавить домашнее задание в систему
        self.homeworks.append(homework)

    def add_test(self, test: Test):
        # Добавить тест в систему
        self.tests.append(test)

    def add_submission(self, submission: HomeworkSubmission):
        # Добавить сданную работу в систему
        self.submissions.append(submission)

    def add_payment(self, payment: Payment):
        # Добавить платеж в систему
        self.payments.append(payment)

    def add_schedule(self, schedule: Schedule):
        # Добавить расписание в систему
        self.schedules.append(schedule)

    def to_dict(self) -> Dict:
        # Преобразовать всю систему в словарь
        return {
            "system_info": {
                "created_date": self.created_date.isoformat(),
                "total_students": len(self.students),
                "total_tutors": len(self.tutors),
                "total_courses": len(self.courses),
                "total_lessons": len(self.lessons),
                "total_homeworks": len(self.homeworks),
                "total_tests": len(self.tests),
                "total_submissions": len(self.submissions),
                "total_payments": len(self.payments),
                "total_schedules": len(self.schedules)
            },
            "students": [student.to_dict() for student in self.students],
            "tutors": [tutor.to_dict() for tutor in self.tutors],
            "courses": [course.to_dict() for course in self.courses],
            "lessons": [lesson.to_dict() for lesson in self.lessons],
            "homeworks": [homework.to_dict() for homework in self.homeworks],
            "tests": [test.to_dict() for test in self.tests],
            "submissions": [submission.to_dict() for submission in self.submissions],
            "payments": [payment.to_dict() for payment in self.payments],
            "schedules": [schedule.to_dict() for schedule in self.schedules]
        }

    def save_to_json(self, filename: str):
       # Сохранить всю систему в JSON файл
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
            print(f"Данные сохранены в JSON файл: {filename}")
        except Exception as e:
            print(f"Ошибка сохранения JSON: {e}")

    def load_from_json(self, filename: str):
        # Загрузить систему из JSON файла
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)

            print(f"Загружаем данные из {filename}...")

            # Очищаем текущие данные
            self._clear_data()

            # Загружаем в правильном порядке зависимостей
            self.tutors = [Tutor.from_dict(tutor_data) for tutor_data in data.get("tutors", [])]
            self.students = [Student.from_dict(student_data) for student_data in data.get("students", [])]
            self.courses = [Course.from_dict(course_data, self.tutors) for course_data in data.get("courses", [])]
            self.lessons = [Lesson.from_dict(lesson_data, self.courses) for lesson_data in data.get("lessons", [])]
            self.homeworks = [Homework.from_dict(hw_data, self.lessons) for hw_data in data.get("homeworks", [])]
            self.tests = [Test.from_dict(test_data, self.lessons) for test_data in data.get("tests", [])]
            self.submissions = [HomeworkSubmission.from_dict(sub_data, self.students, self.homeworks)
                                for sub_data in data.get("submissions", [])]
            self.payments = [Payment.from_dict(payment_data, self.students, self.courses)
                             for payment_data in data.get("payments", [])]
            self.schedules = [Schedule.from_dict(schedule_data, self.students, self.tutors, self.lessons)
                              for schedule_data in data.get("schedules", [])]

            # Восстанавливаем связи
            self._restore_all_relationships(data)

            print("Все данные успешно загружены из JSON!")

        except Exception as e:
            print(f"Ошибка при загрузке JSON: {e}")

    def save_to_xml(self, filename: str):
        # Сохранить всю систему в XML файл
        try:
            # Создаем корневой элемент
            root = ET.Element("education_system")

            # Добавляем информацию о системе
            system_info = ET.SubElement(root, "system_info")
            ET.SubElement(system_info, "created_date").text = self.created_date.isoformat()
            ET.SubElement(system_info, "total_students").text = str(len(self.students))
            ET.SubElement(system_info, "total_tutors").text = str(len(self.tutors))
            ET.SubElement(system_info, "total_courses").text = str(len(self.courses))
            ET.SubElement(system_info, "total_lessons").text = str(len(self.lessons))
            ET.SubElement(system_info, "total_homeworks").text = str(len(self.homeworks))
            ET.SubElement(system_info, "total_tests").text = str(len(self.tests))
            ET.SubElement(system_info, "total_submissions").text = str(len(self.submissions))
            ET.SubElement(system_info, "total_payments").text = str(len(self.payments))
            ET.SubElement(system_info, "total_schedules").text = str(len(self.schedules))

            # Добавляем все данные
            students_elem = ET.SubElement(root, "students")
            for student in self.students:
                students_elem.append(student.to_xml())

            tutors_elem = ET.SubElement(root, "tutors")
            for tutor in self.tutors:
                tutors_elem.append(tutor.to_xml())

            courses_elem = ET.SubElement(root, "courses")
            for course in self.courses:
                courses_elem.append(course.to_xml())

            lessons_elem = ET.SubElement(root, "lessons")
            for lesson in self.lessons:
                lessons_elem.append(lesson.to_xml())

            homeworks_elem = ET.SubElement(root, "homeworks")
            for homework in self.homeworks:
                homeworks_elem.append(homework.to_xml())

            tests_elem = ET.SubElement(root, "tests")
            for test in self.tests:
                tests_elem.append(test.to_xml())

            submissions_elem = ET.SubElement(root, "submissions")
            for submission in self.submissions:
                submissions_elem.append(submission.to_xml())

            payments_elem = ET.SubElement(root, "payments")
            for payment in self.payments:
                payments_elem.append(payment.to_xml())

            schedules_elem = ET.SubElement(root, "schedules")
            for schedule in self.schedules:
                schedules_elem.append(schedule.to_xml())

            # Красивое форматирование XML
            xml_str = ET.tostring(root, encoding='utf-8')
            parsed_xml = minidom.parseString(xml_str)
            pretty_xml = parsed_xml.toprettyxml(indent="  ", encoding='utf-8')

            with open(filename, 'wb') as f:
                f.write(pretty_xml)

            print(f"Данные сохранены в XML файл: {filename}")

        except Exception as e:
            print(f"Ошибка сохранения XML: {e}")

    def load_from_xml(self, filename: str):
        # Загрузить систему из XML файла
        try:
            tree = ET.parse(filename)
            root = tree.getroot()

            print(f"Загружаем данные из XML файла {filename}...")

            # Очищаем текущие данные
            self._clear_data()

            # Загружаем в правильном порядке зависимостей
            self._load_tutors_from_xml(root)
            self._load_students_from_xml(root)
            self._load_courses_from_xml(root)
            self._load_lessons_from_xml(root)
            self._load_homeworks_from_xml(root)
            self._load_tests_from_xml(root)
            self._load_submissions_from_xml(root)
            self._load_payments_from_xml(root)
            self._load_schedules_from_xml(root)

            # Восстанавливаем связи
            self._restore_all_relationships_from_xml(root)

            print("Все XML данные успешно загружены!")

        except Exception as e:
            print(f"Ошибка загрузки XML: {e}")

    def _clear_data(self):
        # Очистить все данные системы
        self.students.clear()
        self.tutors.clear()
        self.courses.clear()
        self.lessons.clear()
        self.homeworks.clear()
        self.tests.clear()
        self.submissions.clear()
        self.payments.clear()
        self.schedules.clear()

    def _load_tutors_from_xml(self, root: ET.Element):
        # Загрузить репетиторов из XML
        tutors_elem = root.find("tutors")
        if tutors_elem is not None:
            for tutor_elem in tutors_elem.findall("tutor"):
                tutor = Tutor.from_xml(tutor_elem)
                self.tutors.append(tutor)
            print(f"Загружено репетиторов: {len(self.tutors)}")

    def _load_students_from_xml(self, root: ET.Element):
        # Загрузить студентов из XML
        students_elem = root.find("students")
        if students_elem is not None:
            for student_elem in students_elem.findall("student"):
                student = Student.from_xml(student_elem)
                self.students.append(student)
            print(f"Загружено студентов: {len(self.students)}")

    def _load_courses_from_xml(self, root: ET.Element):
        # Загрузить курсы из XML
        courses_elem = root.find("courses")
        if courses_elem is not None:
            for course_elem in courses_elem.findall("course"):
                course = Course.from_xml(course_elem, self.tutors)
                self.courses.append(course)
            print(f"Загружено курсов: {len(self.courses)}")

    def _load_lessons_from_xml(self, root: ET.Element):
        # Загрузить уроки из XML
        lessons_elem = root.find("lessons")
        if lessons_elem is not None:
            for lesson_elem in lessons_elem.findall("lesson"):
                lesson = Lesson.from_xml(lesson_elem, self.courses)
                self.lessons.append(lesson)
            print(f"Загружено уроков: {len(self.lessons)}")

    def _load_homeworks_from_xml(self, root: ET.Element):
        # Загрузить домашние задания из XML
        homeworks_elem = root.find("homeworks")
        if homeworks_elem is not None:
            for homework_elem in homeworks_elem.findall("homework"):
                homework = Homework.from_xml(homework_elem, self.lessons)
                self.homeworks.append(homework)
            print(f"Загружено домашних заданий: {len(self.homeworks)}")

    def _load_tests_from_xml(self, root: ET.Element):
        # Загрузить тесты из XML
        tests_elem = root.find("tests")
        if tests_elem is not None:
            for test_elem in tests_elem.findall("test"):
                test = Test.from_xml(test_elem, self.lessons)
                self.tests.append(test)
            print(f"Загружено тестов: {len(self.tests)}")

    def _load_submissions_from_xml(self, root: ET.Element):
        # Загрузить сданные работы из XML
        submissions_elem = root.find("submissions")
        if submissions_elem is not None:
            for submission_elem in submissions_elem.findall("homework_submission"):
                submission = HomeworkSubmission.from_xml(submission_elem, self.students, self.homeworks)
                self.submissions.append(submission)
            print(f"Загружено сданных работ: {len(self.submissions)}")

    def _load_payments_from_xml(self, root: ET.Element):
        # Загрузить платежи из XML
        payments_elem = root.find("payments")
        if payments_elem is not None:
            for payment_elem in payments_elem.findall("payment"):
                payment = Payment.from_xml(payment_elem, self.students, self.courses)
                self.payments.append(payment)
            print(f"Загружено платежей: {len(self.payments)}")

    def _load_schedules_from_xml(self, root: ET.Element):
        # Загрузить расписания из XML
        schedules_elem = root.find("schedules")
        if schedules_elem is not None:
            for schedule_elem in schedules_elem.findall("schedule"):
                schedule = Schedule.from_xml(schedule_elem, self.students, self.tutors, self.lessons)
                self.schedules.append(schedule)
            print(f"Загружено расписаний: {len(self.schedules)}")

    def _restore_all_relationships(self, data: Dict):
        # Восстановить все связи между объектами
        # Восстанавливаем enrolled_courses для студентов
        for student_data, student_obj in zip(data.get("students", []), self.students):
            course_names = student_data.get("enrolled_courses", [])
            for course_name in course_names:
                course = next((c for c in self.courses if c.name == course_name), None)
                if course and course not in student_obj.enrolled_courses:
                    student_obj.enrolled_courses.append(course)
                    if student_obj not in course.students:
                        course.students.append(student_obj)

        # Восстанавливаем courses_taught для репетиторов
        for tutor_data, tutor_obj in zip(data.get("tutors", []), self.tutors):
            course_names = tutor_data.get("courses_taught", [])
            for course_name in course_names:
                course = next((c for c in self.courses if c.name == course_name), None)
                if course and course not in tutor_obj.courses_taught:
                    tutor_obj.courses_taught.append(course)

        # Восстанавливаем уроки для курсов
        for course_data, course_obj in zip(data.get("courses", []), self.courses):
            lesson_names = [lesson["name"] for lesson in course_data.get("lessons", [])]
            for lesson_name in lesson_names:
                lesson = next((l for l in self.lessons if l.name == lesson_name), None)
                if lesson and lesson not in course_obj.lesson:
                    course_obj.lesson.append(lesson)

        print("Все связи между объектами восстановлены")

    def _restore_all_relationships_from_xml(self, root: ET.Element):
        """Восстановить все связи из XML"""
        self._restore_student_courses_from_xml(root)
        self._restore_tutor_courses_from_xml(root)
        self._restore_course_lessons_from_xml(root)
        self._restore_lesson_homeworks_from_xml(root)

        print("Все связи из XML восстановлены")

    def _restore_student_courses_from_xml(self, root: ET.Element):
        # Восстановить связи студентов с курсами
        students_elem = root.find("students")
        if students_elem is not None:
            for student_elem, student_obj in zip(students_elem.findall("student"), self.students):
                courses_elem = student_elem.find("enrolled_courses")
                if courses_elem is not None:
                    for course_elem in courses_elem.findall("course"):
                        course_name = course_elem.text
                        course = next((c for c in self.courses if c.name == course_name), None)
                        if course and course not in student_obj.enrolled_courses:
                            student_obj.enrolled_courses.append(course)
                            if student_obj not in course.students:
                                course.students.append(student_obj)

    def _restore_tutor_courses_from_xml(self, root: ET.Element):
        # Восстановить связи репетиторов с курсами
        tutors_elem = root.find("tutors")
        if tutors_elem is not None:
            for tutor_elem, tutor_obj in zip(tutors_elem.findall("tutor"), self.tutors):
                courses_elem = tutor_elem.find("courses_taught")
                if courses_elem is not None:
                    for course_elem in courses_elem.findall("course"):
                        course_name = course_elem.text
                        course = next((c for c in self.courses if c.name == course_name), None)
                        if course and course not in tutor_obj.courses_taught:
                            tutor_obj.courses_taught.append(course)

    def _restore_course_lessons_from_xml(self, root: ET.Element):
        # Восстановить связи курсов с уроками
        courses_elem = root.find("courses")
        if courses_elem is not None:
            for course_elem, course_obj in zip(courses_elem.findall("course"), self.courses):
                lessons_elem = course_elem.find("lessons")
                if lessons_elem is not None:
                    for lesson_elem in lessons_elem.findall("lesson"):
                        lesson_name = lesson_elem.find("name").text
                        lesson = next((l for l in self.lessons if l.name == lesson_name), None)
                        if lesson and lesson not in course_obj.lesson:
                            course_obj.lesson.append(lesson)

    def _restore_lesson_homeworks_from_xml(self, root: ET.Element):
        # Восстановить связи уроков с домашними заданиями
        lessons_elem = root.find("lessons")
        if lessons_elem is not None:
            for lesson_elem, lesson_obj in zip(lessons_elem.findall("lesson"), self.lessons):
                homeworks_elem = lesson_elem.find("homeworks")
                if homeworks_elem is not None:
                    for homework_elem in homeworks_elem.findall("homework"):
                        homework_title = homework_elem.find("title").text
                        homework = next((h for h in self.homeworks if h.title == homework_title), None)
                        if homework and homework not in lesson_obj.homeworks:
                            lesson_obj.homeworks.append(homework)
