from tabnanny import check
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import backref
from enum import Enum
db = SQLAlchemy()

class Roles(Enum):
    ADMINISTRATOR = "Administrator"
    USER = "User"
    OTHER = "Other"

class Gender(Enum):
    HOMBRE = "Hombre"
    MUJER = "Mujer"

class Priority(Enum):
    HIGHT = "Alta"
    MEDIUM = "Media"
    LOW = "Baja"

## --> Users <-- ##
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    project = db.relationship("Project", backref="user", uselist=True)
    profile = db.relationship("Profile", back_populates="user", uselist=False)

    def __repr__(self):
        return '<User: %r>' % self.email

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email
        }

## --> Perfil <-- ##
class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    fullname = db.Column(db.String(150), nullable=False)
    description = db.Column(db.String(250))
    photo = db.Column(db.String(250))
    gender = db.Column(db.Enum(Gender), nullable=False)
    user = db.relationship("User", back_populates="profile")
    
    def __repr__(self):
        return '<Profile: %r>' % self.fullname

    def serialize(self):
        return {
            "user_id": self.user_id,
            "fullname": self.fullname,
            "description": self.description,
            "gender": self.gender,
            "photo": self.photo,
        }

## --> Project <-- ##
class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.String(250))
    due_date = db.Column(db.Date)
    start_date = db.Column(db.Date)
    status = db.Column(db.Boolean, default=True)
    
    task = db.relationship("Task", backref="project", uselist=True)


    def __repr__(self):
        return '<Project: %r>' % self.name

    def serialize(self):
        return {
            "user_id": self.user_id,
            "name": self.name,
            "members": self.members,
            "description": self.description,
            "due_date": self.due_date,
            "start_date": self.start_date,
            "rol": self.rol,
            "status": self.status
        }

## --> Members <-- ##
class Members(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rol = db.Column(db.Enum(Roles), nullable=False)

    def __repr__(self):
        return '<Members: %r>' % self.user_id

    def serialize(self):
        return {
            "user_id": self.user_id,
            "project_id": self.project_id,
            "rol": self.rol
        }

## --> Task <-- ##
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(250))
    check_in = db.Column(db.Boolean, default=False)
    due_date = db.Column(db.Date)
    start_date = db.Column(db.Date)
    members = db.Column(db.String(250), db.ForeignKey('members.id'))
    priority = db.Column(db.Enum(Priority), nullable=False)
    subtask = db.relationship("Subtask", backref="task", uselist=True)

    def __repr__(self):
        return '<Task: %r>' % self.name

    def serialize(self):
        return {
            "user_id": self.user_id,
            "project_id": self.project_id,
            "name": self.name, 
            "description": self.description,
            "check_in": self.check_in,
            "due_date": self.due_date,
            "start_date": self.start_date,
            "members": self.members,
            "priority": self.priority,
        }

## --> Subtask <-- ##
class Subtask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    members = db.Column(db.Integer, db.ForeignKey('members.id'))
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(250))
    due_date = db.Column(db.Date)
    start_date = db.Column(db.Date)

    def __repr__(self):
        return '<Subtask: %r>' % self.name

    def serialize(self):
        return {
            "user_id": self.user_id,
            "project_id": self.project_id,
            "name": self.name
        }
