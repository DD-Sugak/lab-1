from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Optional
import json

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

        if new_lesson in self.lessons:
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


class EducationSystem:
    def load_from_json(self, filename: str):
        """Загрузить всю систему из JSON файла"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)

            print(f"📂 Загружаем данные из {filename}...")

            # 1. Загружаем базовые объекты
            self.tutors = [Tutor.from_dict(tutor_data) for tutor_data in data.get("tutors", [])]
            self.students = [Student.from_dict(student_data) for student_data in data.get("students", [])]
            self.courses = [Course.from_dict(course_data, self.tutors) for course_data in data.get("courses", [])]

            # 2. Загружаем уроки (нужны курсы)
            self.lessons = [Lesson.from_dict(lesson_data, self.courses)
                            for lesson_data in data.get("lessons", [])]

            # 3. Загружаем домашние задания (нужны уроки)
            self.homeworks = [Homework.from_dict(hw_data, self.lessons)
                              for hw_data in data.get("homeworks", [])]

            # 4. Загружаем тесты (нужны уроки)
            self.tests = [Test.from_dict(test_data, self.lessons)
                          for test_data in data.get("tests", [])]

            # 5. Загружаем сданные работы (нужны студенты и задания)
            self.submissions = [HomeworkSubmission.from_dict(sub_data, self.students, self.homeworks)
                                for sub_data in data.get("submissions", [])]

            # 6. Загружаем платежи (нужны студенты и курсы)
            self.payments = [Payment.from_dict(payment_data, self.students, self.courses)
                             for payment_data in data.get("payments", [])]

            # 7. Загружаем расписания (нужны студенты, репетиторы и уроки)
            self.schedules = [Schedule.from_dict(schedule_data, self.students, self.tutors, self.lessons)
                              for schedule_data in data.get("schedules", [])]

            # 8. Восстанавливаем все связи
            self._restore_all_relationships(data)

            print("Все данные успешно загружены!")

        except Exception as e:
            print(f"Ошибка при загрузке: {e}")

    def _restore_all_relationships(self, data: Dict):
        # Восстанавливаем связи курсов
        for course_data, course_obj in zip(data.get("courses", []), self.courses):
            # Уроки курса
            lesson_names = [lesson["name"] for lesson in course_data.get("lessons", [])]
            for lesson_name in lesson_names:
                lesson = next((l for l in self.lessons if l.name == lesson_name), None)
                if lesson:
                    course_obj.add_lessons(lesson)

            # Студенты курса
            student_names = course_data.get("students", [])
            for student_name in student_names:
                student = next((s for s in self.students
                                if f"{s.first_name} {s.last_name}" == student_name), None)
                if student:
                    course_obj.add_student(student)

        for lesson_data, lesson_obj in zip(data.get("lessons", []), self.lessons):
            homework_titles = [hw["title"] for hw in lesson_data.get("homeworks", [])]
            for hw_title in homework_titles:
                homework = next((h for h in self.homeworks if h.title == hw_title), None)
                if homework:
                    lesson_obj.add_homework(homework)

        print("Все связи между объектами восстановлены")