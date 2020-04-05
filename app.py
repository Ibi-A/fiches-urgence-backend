import json
import string
import random

from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import aliased


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'

db = SQLAlchemy(app)


class Person(db.Model):

    __tablename__ = 'persons'

    id = db.Column(db.String, primary_key=True)
    first_name = db.Column(db.String, index=True, nullable=False)
    last_name = db.Column(db.String, index=True, nullable=False)
    address = db.Column(db.String)


class PhoneNumber(db.Model):
    __tablename__ = 'phone_numbers'

    phone_number = db.Column(db.String, primary_key=True)

    person_id = db.Column(db.String, db.ForeignKey(
        'persons.id'), nullable=False)


class Contributor(db.Model):

    __tablename__ = 'contributors'

    id = db.Column(db.String, db.ForeignKey('persons.id'), primary_key=True)

    role = db.Column(db.String, nullable=True)


class HealthMutual(db.Model):

    __tablename__ = 'health_mutuals'

    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String, index=True)
    address = db.Column(db.String, index=True)
    phone_number = db.Column(db.String)


class Resident(db.Model):

    __tablename__ = 'residents'

    id = db.Column(db.String, db.ForeignKey('persons.id'), primary_key=True)

    birth_date = db.Column(db.Date)
    birthplace = db.Column(db.String)
    entrance_date = db.Column(db.Date)
    emergency_bag = db.Column(db.String)
    social_welfare_number = db.Column(db.String)

    health_mutual_id = db.Column(
        db.String, db.ForeignKey('health_mutuals.id'), nullable=True)
    referring_doctor_id = db.Column(
        db.String, db.ForeignKey('persons.id'), nullable=True)
    psychiatrist_id = db.Column(
        db.String, db.ForeignKey('persons.id'), nullable=True)

    resident = db.relationship('Person', foreign_keys=[id])
    referring_doctor = db.relationship(
        'Person', foreign_keys=[referring_doctor_id])
    psychiatrist = db.relationship('Person', foreign_keys=[psychiatrist_id])


emergency_relationships = db.Table('emergency_relationships',
                                   db.Column('resident_id', db.String, db.ForeignKey(
                                       'residents.id'), primary_key=True),
                                   db.Column('person_id', db.String, db.ForeignKey(
                                       'persons.id'), primary_key=True),
                                   db.Column('relationship',
                                             db.String, primary_key=True)
                                   )


contribution_relationships = db.Table('contribution_relationships',
                                      db.Column('resident_id', db.String, db.ForeignKey(
                                          'residents.id'), primary_key=True),
                                      db.Column('contributor_id', db.String, db.ForeignKey(
                                          'contributors.id'), primary_key=True),
                                      db.Column(
                                          'social_advising_relationship', db.Boolean, primary_key=True)
                                      )


def get_random_id(size: int) -> str:
    random.seed()
    charset = string.digits + string.ascii_letters + '_'

    generated_id = ''

    for _ in range(0, size):
        generated_id = generated_id + \
            charset[random.randint(0, len(charset) - 1)]

    return generated_id


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
        query = db.session.query(Person, Resident, PhoneNumber, HealthMutual, emergency_relationships, contribution_relationships) \
            .filter(Person.id == resident_id) \
            .join(Resident, Resident.id == Person.id) \
            .outerjoin(PhoneNumber, PhoneNumber.person_id == Person.id) \
            .outerjoin(HealthMutual, HealthMutual.id == Resident.health_mutual_id) \
            .outerjoin(emergency_relationships, emergency_relationships.resident_id == Resident.id) \
            .outerjoin(contribution_relationships, contribution_relationships.resident_id == Resident.id)

    return None