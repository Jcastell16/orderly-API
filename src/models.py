from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import backref

db = SQLAlchemy()

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
    name = db.Column(db.String(50), nullable=False)
    lastname = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(250))
    departamento = db.Column(db.String(50))
    photo = db.Column(db.String(200))
    user = db.relationship("User", back_populates="profile")
    
    def __repr__(self):
        return '<Profile: %r>' % self.name

    def serialize(self):
        return {
            "user_id": self.user_id,
            "name": self.name,
            "lastname": self.lastname,
            "description": self.description,
            "email": self.email,
            "rol": self.rol,
            "departamento": self.departamento,
            "photo": self.photo,
        }

## --> Project <-- ##
class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    members = db.Column(db.String(50))
    description = db.Column(db.String(250))
    finish_date = db.Column(db.Date)
    status = db.Column(db.Boolean, default=True)
    rol = db.Column(db.String(50)) 
    goals = db.Column(db.String(50))
    task = db.relationship("Task", backref="project", uselist=True)


    def __repr__(self):
        return '<Project: %r>' % self.name

    def serialize(self):
        return {
            "user_id": self.user_id,
            "name": self.name,
            "members": self.members,
            "description": self.description,
            "finish_date": self.finish_date,
            "status": self.status,
            "goals": self.goals
        }

## --> Task <-- ##
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    subtask = db.relationship("Subtask", backref="task", uselist=True)

    def __repr__(self):
        return '<Task: %r>' % self.name

    def serialize(self):
        return {
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
    finish_date = db.Column(db.Date)

    def __repr__(self):
        return '<Subtask: %r>' % self.name

    def serialize(self):
        return {
            "user_id": self.user_id,
            "project_id": self.project_id,
            "name": self.name
        }
