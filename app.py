import json

from flask import Flask
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'

db = SQLAlchemy(app)


class Person(db.Model):
    id = db.Column(db.String, primary_key=True)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    address = db.Column(db.String)

    phone_numbers = db.relationship('PhoneNumber', backref='person', lazy=True)
    residents = db.relationship('Resident', backref='person', lazy=True)
    contributors = db.relationship('Contributor', backref='person', lazy=True)


class PhoneNumber(db.Model):
    phone_number = db.Column(db.String, primary_key=True) 

    person_id = db.Column(db.String, db.ForeignKey('person.id'), nullable=False)


class Resident(db.Model):
    id = db.Column(db.String, db.ForeignKey('person.id'), primary_key=True)

    birth_date = db.Column(db.Date)
    birthplace = db.Column(db.String)
    entrance_date = db.Column(db.Date)
    emergency_bag = db.Column(db.String)
    social_welfare_number = db.Column(db.String)

    health_mutual_id = db.Column(db.String, db.ForeignKey('health_mutual.id'), nullable=True)
    referring_doctor_person_id = db.Column(db.String, db.ForeignKey('person.id'), nullable=True)
    psychiatrist_person_id = db.Column(db.String, db.ForeignKey('person.id'), nullable=True)
    

class Contributor(db.Model):
    id = db.Column(db.String, db.ForeignKey('person.id'), primary_key=True)

    role = db.Column(db.String, nullable=True)


class HealthMutual(db.Model):
    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String)
    address = db.Column(db.String)
    phone_number = db.Column(db.String)

    residents = db.relationship('Resident', backref='health_mutual', lazy=True)


emergency_relationships = db.Table('emergency_relationships',
    db.Column('resident_id', db.String, db.ForeignKey('resident.id'), primary_key=True),
    db.Column('person_id', db.String, db.ForeignKey('person.id'), primary_key=True),
    db.Column('relationship', db.String, primary_key=True)
)


contribution_relationships = db.Table('contribution_relationships',
    db.Column('resident_id', db.String, db.ForeignKey('resident.id'), primary_key=True),
    db.Column('contributor_id', db.String, db.ForeignKey('contributor.id'), primary_key=True),
    db.Column('social_advising_relationship', db.Boolean, primary_key=True)
)



@app.route('/residents', methods=['GET', 'POST'])
def residents_collection():
    return None

@app.route('/residents/<string:resident_id>', methods=['GET', 'PATCH', 'PUT', 'DELETE'])
def resident_item(resident_id):
    return None


@app.route('/health-mutuals', methods=['GET', 'POST'])
def health_mutuals_collection():
    return None

@app.route('/health-mutuals/<string:health_mutual_id>', methods=['GET', 'PATCH', 'PUT', 'DELETE'])
def health_mutual_item(health_mutual_id):
    return None