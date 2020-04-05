import json
import string
import random

from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import aliased


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'

db = SQLAlchemy(app)


def get_random_id(size: int) -> str:
    random.seed()
    charset = string.digits + string.ascii_letters + '_'

    generated_id = ''

    for _ in range(0, size):
        generated_id = generated_id + \
            charset[random.randint(0, len(charset) - 1)]

    return generated_id


class Person(db.Model):
    id = db.Column(db.String, primary_key=True)
    first_name = db.Column(db.String, index=True, nullable=False)
    last_name = db.Column(db.String, index=True, nullable=False)
    address = db.Column(db.String)

    phone_numbers = db.relationship(
        'PhoneNumber', backref='person', lazy=True, foreign_keys='[PhoneNumber.person_id]')
    contributors = db.relationship(
        'Contributor', backref='person', lazy=True, foreign_keys='[Contributor.id]')
    residents = db.relationship(
        'Resident', backref='person', lazy=True, foreign_keys='[Resident.id]')
    referring_doctors = db.relationship(
        'Resident', backref='doctor', lazy=True, foreign_keys='[Resident.referring_doctor_id]')
    psychiatrists = db.relationship(
        'Resident', backref='psychiatrist', lazy=True, foreign_keys='[Resident.psychiatrist_id]')

    emergency_relationships = db.relationship('emergency_relationship', foreign_keys='[emergency_relationship.person_id]')


class PhoneNumber(db.Model):
    phone_number = db.Column(db.String, primary_key=True)

    person_id = db.Column(db.String, db.ForeignKey(
        'person.id'), nullable=False)


class Contributor(db.Model):
    id = db.Column(db.String, db.ForeignKey('person.id'), primary_key=True)

    role = db.Column(db.String, nullable=True)

    contribution_relationships = db.relationship('contribution_relationship', foreign_keys='[contribution_relationship.contributor_id]')


class HealthMutual(db.Model):
    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String, index=True)
    address = db.Column(db.String, index=True)
    phone_number = db.Column(db.String)

    residents = db.relationship('Resident', backref='health_mutual', lazy=True, foreign_keys='[Resident.health_mutual_id]')


class Resident(db.Model):
    id = db.Column(db.String, db.ForeignKey('person.id'), primary_key=True)

    birth_date = db.Column(db.Date)
    birthplace = db.Column(db.String)
    entrance_date = db.Column(db.Date)
    emergency_bag = db.Column(db.String)
    social_welfare_number = db.Column(db.String)

    health_mutual_id = db.Column(
        db.String, db.ForeignKey('health_mutual.id'), nullable=True)
    referring_doctor_id = db.Column(
        db.String, db.ForeignKey('person.id'), nullable=True)
    psychiatrist_id = db.Column(
        db.String, db.ForeignKey('person.id'), nullable=True)

    emergency_relationships = db.relationship('emergency_relationship', foreign_keys='[emergency_relationship.resident_id]')
    contribution_relationships = db.relationship('contribution_relationship', foreign_keys='[contribution_relationship.resident_id]')


class EmergencyRelationship(db.Model):
    resident_id = db.Column(db.String, db.ForeignKey('resident.id'), primary_key=True)
    person_id = db.Column(db.String, db.ForeignKey('person.id'), primary_key=True)
    relationship = db.Column(db.String, primary_key=True)


class ContributionRelationship(db.Model):
    resident_id = db.Column(db.String, db.ForeignKey('resident.id'), primary_key=True)
    contributor_id = db.Column(db.String, db.ForeignKey('contributor.id'), primary_key=True)
    social_advising_relationship = db.Column(db.Boolean, primary_key=True)


@app.route('/residents', methods=['GET', 'POST'])
def residents_collection():
    if request.method == 'GET':
        pass
    elif request.method == 'POST':
        # extract the information
        payload = request.json

        resident_id = get_random_id(8)

        person = Person(
            id=resident_id,
            first_name=payload.get('firstName'),
            last_name=payload.get('lastName'),
            address=payload.get('address')
        )

        db.session.add(person)

        resident = Resident(
            id=resident_id,
            birth_date=payload.get('birthDate'),
            birthplace=payload.get('birthplace'),
            entrance_date=payload.get('entranceDate'),
            emergency_bag=payload.get('emergencyBag'),
            social_welfare_number=payload.get('socialWelfareNumber'),
            health_mutual_id=payload.get('healthMutualId'),
            referring_doctor_id=payload.get('referringDoctorId'),
            psychiatrist_id=payload.get('psychiatristId')
        )

        db.session.add(resident)
        db.session.commit()

    return json.dumps({'id': resident_id})


@app.route('/residents/<string:resident_id>', methods=['GET', 'PATCH', 'PUT', 'DELETE'])
def resident_item(resident_id):
    if request.method == 'GET':
        query = db.session.query(Person, Resident, PhoneNumber, HealthMutual, EmergencyRelationship, ContributionRelationship) \
            .filter(Person.id == resident_id) \
            .join(Resident, Resident.id == Person.id) \
            .outerjoin(PhoneNumber, PhoneNumber.person_id == Person.id) \
            .outerjoin(HealthMutual, HealthMutual.id == Resident.health_mutual_id) \
            .outerjoin(EmergencyRelationship, EmergencyRelationship.resident_id == Resident.id) \
            .outerjoin(ContributionRelationship, ContributionRelationship.resident_id == Resident.id)

    return None
