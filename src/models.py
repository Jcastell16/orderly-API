from tabnanny import check
from time import timezone
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import backref
from enum import Enum
from datetime import datetime

db = SQLAlchemy()

class Roles(str, Enum):
    ADMINISTRADOR: str = "Administrador"
    USUARIO: str = "Usuario"

class Gender(str, Enum):
    HOMBRE: str = "Hombre"
    MUJER: str = "Mujer"

class Priority(str, Enum):
    ALTA: str = "Alta"
    MEDIA: str = "Media"
    BAJA: str = "Baja"

class Status(str, Enum):
    ENCURSO: str = "En Curso"
    FINALIZADO: str = "Finalizado"

## --> Users <-- ##
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    members = db.relationship("Members", backref="user", uselist=True)
    profile = db.relationship("Profile", back_populates="user", uselist=False)
    project = db.relationship("Project", backref="user", uselist=True)
    task = db.relationship("Task", backref="user", uselist=True)

    def repr(self):
        return '<User: %r>' % self.id, self.email

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email
        }

## --> Perfil <-- ##
class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    lastname = db.Column(db.String(150), nullable=False)
    description = db.Column(db.String(250))
    photo = db.Column(db.String(250))
    gender = db.Column(db.Enum(Gender))
    user = db.relationship("User", back_populates="profile")
    
    def repr(self):
        return '<Profile: %r>' % self.id, self.name

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "lastname": self.lastname,            
            "description": self.description,
            "gender": self.gender,
            "photo": self.photo,
        }

## --> Members <-- ##
class Members(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    nature = db.Column(db.String(50), nullable=False)
    nature_id = db.Column(db.Integer, nullable=False)
    rol = db.Column(db.Enum(Roles))

    def repr(self):
        return '<Members: %r>' % self.id

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "nature": self.nature,
            "nature_id": self.nature_id,
            "rol": self.rol
        }

## --> Project <-- ##
class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.String(250))
    due_date = db.Column(db.String(50))
    start_date = db.Column(db.DateTime)
    status = db.Column(db.Enum(Status), nullable=False)
    columntask = db.relationship("Columntask", backref="project", uselist=True)
    task = db.relationship("Task", backref="project", uselist=True)


    def repr(self):
        return '<Project: %r>' % self.id, self.name

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "description": self.description,
            "due_date": self.due_date,
            "start_date": self.start_date,
            "status": self.status
        }

## --> Columntask <-- ##
class Columntask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    name = db.Column(db.String(50))
    task = db.relationship("Task", backref="columntask", uselist=True)

    def repr(self):
        return '<Columntask: %r>' % self.id, self.name

    def serialize(self):
        return {
            "id": self.id,
            "project_id": self.project_id,
            "name": self.name
        }

## --> Task <-- ##
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    subtask = db.relationship("Subtask", backref="task", uselist=True)

    def __repr__(self):
        return '<Task: %r>' % self.name

    def serialize(self):
        return {
            "task_id": self.id,
            "user_id": self.user_id,
            "project_id": self.project_id,
            "name": self.name
        }

## --> Subtask <-- ##
class Subtask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(250))
    check_in = db.Column(db.Boolean, default=False)
    due_date = db.Column(db.String(50))
    start_date = db.Column(db.DateTime)
    priority = db.Column(db.Enum(Priority))
    members = db.relationship("Members", backref="task", uselist=True)

    def repr(self):
        return '<Task: %r>' % self.id, self.name

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "project_id": self.project_id,
            "columntask_id": self.columntask_id,
            "members_id": self.members_id,
            "name": self.name, 
            "description": self.description,
            "check_in": self.check_in,
            "due_date": self.due_date,
            "start_date": self.start_date,
            "priority": self.priority,
        }