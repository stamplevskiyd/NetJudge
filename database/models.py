from sqlalchemy import *
from sqlalchemy.orm import relationship
import datetime
import tarfile
import re
import os
import hashlib

from . import *
from .translator import translate  # потом переделать


class Person(Base):
    """Class for one person."""

    __tablename__ = 'person'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)
    tasks = relationship("Task")

    def __init__(self, name, email):
        self.name = name
        self.email = email

    def __repr__(self):
        line = f"Name: {self.name}\nemail: {self.email}\n"
        line += f"Completed tasks: "
        for task in self.tasks:
            line += str(task.number) + ','
        return line

    def add_task(self, number, name=''):
        session = session_factory()
        new_task = Task(self.id, number, name)
        print(self.id)
        session.add(new_task)
        session.commit()
        session.close()


class Task(Base):
    """One task with all report files"""

    __tablename__ = 'task'

    person_id = Column(Integer, ForeignKey('person.id', ondelete='CASCADE'), nullable=False)
    id = Column(Integer, primary_key=True)
    number = Column(Integer)
    name = Column(String)
    reports = relationship("Report")

    def __init__(self, person_id, number, name=''):
        """Initialise task object."""

        self.person_id = person_id
        self.name = name
        self.number = number

    def add_report(self, file_path):
        """Add report file for this task object."""

        session = session_factory()
        new_report = Report(self.id, file_path)
        print(new_report)
        session.add(new_report)
        session.commit()
        session.close()


class Report(Base):
    """Report files and info"""

    __tablename__ = 'report'

    task_id = Column(Integer, ForeignKey('task.id', ondelete='CASCADE'), nullable=True)
    id = Column(Integer, primary_key=True)
    name = Column(String)  # report.03.base
    text = Column(Text)
    input = Column(Text)
    output = Column(Text)
    create_date = Column(Date)
    hash = Column(String)
    grade = Column(Float)  # 0, 0.25, 0.5. 1

    def __init__(self, task_id, file_path):
        print("Works")
        self.task_id = task_id
        self.name = os.path.basename(file_path)
        file = tarfile.open(file_path)
        self.text = file.extractfile('./OUT.txt').read().decode()
        text = re.sub('\r', '', self.text)  # re.split работал не совсем так, как надо
        lines = [translate(line) for line in text.split('\n') if line]
        self.input = '\n'.join([line[1] for line in lines if line[0] == 'input'])
        self.output = '\n'.join([line[1] for line in lines if line[0] == 'output'])
        self.create_date = self.get_report_date(file)
        self.get_report_date(file)
        self.hash = hashlib.md5(file.extractfile('./OUT.txt').read()).hexdigest()

    # def __repr__(self):
    #     """Строковое представление информации."""
    #
    #     session = session_factory()
    #     line = f"Name: {self.name}\nAuthor: {session.query(Person).get(self.person_id).name}\n"
    #     session.close()
    #     line += f"Creation date: {self.create_date.strftime('%d.%m.%y')}\n"
    #     line += f"Hash: {self.hash}"
    #     return line

    def get_report_date(self, file):
        """Вычислить дату начала выполнения отчета."""

        line = file.extractfile('./TIME.txt').read().decode().split('\n')[0]
        time_lines = re.findall(r'START_TIME \d{4}-\d{2}-\d{2}', line)
        if time_lines:
            create_date = re.findall(r'\d{4}-\d{2}-\d{2}', time_lines[0])[0]
            year, month, day = create_date.split('-')
            date = datetime.date(day=int(day), month=int(month), year=int(year))
            return date
        else:  # едва ли это нужно
            raise ValueError()

    def set_grade(self, deadline):
        pass
