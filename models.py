from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import UniqueConstraint

db = SQLAlchemy()

class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    prenom = db.Column(db.String(100), nullable=False)
    nom = db.Column(db.String(100), nullable=False)
    filiere = db.Column(db.String(50), nullable=False)
    annee = db.Column(db.String(50), nullable=False)
    groupe = db.Column(db.String(20), nullable=False)
    __table_args__ = (UniqueConstraint('prenom', 'nom', 'filiere', 'annee', 'groupe', name='uix_student_unique'),)

class Admin(db.Model):
    __tablename__ = 'admins'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
