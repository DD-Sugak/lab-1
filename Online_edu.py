from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Optional


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
         self.enrolled_courses: List[Course] = []
         self.schedule = Schedule(student=self)

    def display_info(self):
        print(f"Студент: {self.first_name} {self.last_name}")
        print(f"Класс: {self.grade}")
        print(f"Курсов записано: {len(self.enrolled_courses)}")

    def choose_a_course(self, course:'Course'):
        course.add_student(self)
        self.enrolled_courses.append(course)
    def get_course(self):
        return self.enrolled_courses

    def view_the_schedule(self):
        self.schedule.display_schedule()

class Tutor(Person):
    def __init__(self, first_name: str, last_name :str, age: int, phone: str,
                 email: str, user_id: int, role: str, subject: str,  experience: int, bio: str):
         super().__init__(first_name, last_name, age, phone, email, user_id, role)
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
                 time: str, price: str, status: str) -> 'Course':
        course = Course(name=name, tutor=self, subject=subject,  # передай все параметры
                        description=description, time=time, price=price, status=status)
        self.courses_taught.append(course)
        return course

    def view_the_schedule(self):
        self.schedule.display_schedule()

class Course():
    def __init__(self, name: str, tutor: Tutor, subject: str, description: str,
                 time: str, month_price: str, status: str):
        self.name = name
        self.tutor = tutor
        self.subject = subject
        self.description = description
        self.time = time
        self.month_price = month_price
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
        self.lessons: List[Lesson] = []

    def add_lesson(self, lesson: 'Lesson'):
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

class Lesson():
    def __init__(self,name: str, description: str, course: Course,
                 start_time: str, end_time: str, date: str):
        self.name = name
        self.description = description
        self.course = course
        self.start_time = start_time
        self.end_time = end_time
        self.date = date
        self.homeworks : List[Homework] = []

    def add_homework(self, homework: 'Homework'):
        self.homeworks.append(homework)

class Payment():
    def __init__(self, student: Student, month: str, year: int):
        self.student = student
        self.month = month
        self.year = year
        self.courses: List[Course] = []
        self.total_amount = 0.0
        self.status = "pending"
        self.payment_date = None

    def add_course(self, course: Course):
        self.courses.append(course)
        self.total_amount += self._parse_price(course.month_price)

    def _parse_price(self, price_str: str) -> float:
        clean_price = ''.join(c for c in price_str if c.isdigit() or c in ',.')
        clean_price = clean_price.replace(',', '.')
        return float(clean_price)

    def process_payment(self):
        self.status = "paid"
        self.payment_date = datetime.now()
        print(f"Оплата за {self.month} {self.year}: {len(self.courses)} курсов на сумму {self.total_amount} руб.")

    def get_payment_info(self):
        course_names = [course.name for course in self.courses]
        return f"Платеж за {self.month}: {', '.join(course_names)} - {self.total_amount} руб."

class Homework():
    def __init__(self, title: str, description: str, lesson: Lesson,
                 deadline: str, max_score: int = 100):
        self.title = title
        self.description = description
        self.lesson = lesson
        self.deadline = deadline
        self.max_score = max_score
        self.attachments: List[str] = []
        self.student_submissions: Dict[Student, 'HomeworkSubmission'] = {}

class HomeworkSubmission():
    def __init__(self, student: Student, homework: Homework,
                 answer: str, submitted_date: str):
        self.student = student
        self.homework = homework
        self.answer = answer
        self.submitted_date = submitted_date
        self.score: Optional[int] = None  # оценка
        self.feedback: str = ""

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

class Test():
    def __init__(self, title: str, lesson: Lesson):
        self.title = title
        self.lesson = lesson
        self.questions: List['Question'] = []

    def add_question(self, question: 'Question'):
        self.questions.append(question)

    def calculate_score(self, user_answers: List[int]) -> int:
        score = 0
        for i, question in enumerate(self.questions):
            if user_answers[i] == question.correct_answer:
                score += 1
        return score

class Question:
    def __init__(self, text: str, options: List[str], correct_answer: int):
        self.text = text
        self.options = options
        self.correct_answer = correct_answer

