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

    emergency_relationships = db.relationship(
        'EmergencyRelationship', foreign_keys='[EmergencyRelationship.person_id]')


class PhoneNumber(db.Model):

    id = db.Column(db.String, primary_key=True)

    phone_number = db.Column(db.String, index=True)

    person_id = db.Column(db.String, db.ForeignKey(
        'person.id'), nullable=False)


class Contributor(db.Model):
    id = db.Column(db.String, db.ForeignKey('person.id'), primary_key=True)

    role = db.Column(db.String, nullable=True)

    contribution_relationships = db.relationship(
        'ContributionRelationship', foreign_keys='[ContributionRelationship.contributor_id]')


class HealthMutual(db.Model):
    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String, index=True)
    address = db.Column(db.String, index=True)
    phone_number = db.Column(db.String)

    residents = db.relationship('Resident', backref='health_mutual',
                                lazy=True, foreign_keys='[Resident.health_mutual_id]')


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

    emergency_relationships = db.relationship(
        'EmergencyRelationship', foreign_keys='[EmergencyRelationship.resident_id]')
    contribution_relationships = db.relationship(
        'ContributionRelationship', foreign_keys='[ContributionRelationship.resident_id]')


class EmergencyRelationship(db.Model):
    id = db.Column(db.String, primary_key=True)

    resident_id = db.Column(db.String, db.ForeignKey(
        'resident.id'), primary_key=True)
    person_id = db.Column(db.String, db.ForeignKey(
        'person.id'), primary_key=True)
    relationship = db.Column(db.String, primary_key=True)


class ContributionRelationship(db.Model):
    id = db.Column(db.String, primary_key=True)

    resident_id = db.Column(db.String, db.ForeignKey(
        'resident.id'), primary_key=True)
    contributor_id = db.Column(db.String, db.ForeignKey(
        'contributor.id'), primary_key=True)
    social_advising = db.Column(db.Boolean, primary_key=True)


def create_person(json_payload: dict):
    person_id=get_random_id(8)

    person=Person(
        id=person_id,
        first_name=json_payload.get('firstName'),
        last_name=json_payload.get('lastName'),
        address=json_payload.get('address')
    )

    db.session.add(person)
    db.session.commit()

    phone_numbers = json_payload.get('phoneNumbers')

    if phone_numbers is not None:
        create_phone_numbers(person_id, phone_numbers)


    return person_id


def create_resident(json_payload: dict, resident_id: str = None):
    person_id = resident_id

    if person_id is None:
        person_id = create_person(json_payload)

    resident = Resident(
        id=person_id,
        birth_date=json_payload.get('birthDate'),
        birthplace=json_payload.get('birthplace'),
        entrance_date=json_payload.get('entranceDate'),
        emergency_bag=json_payload.get('emergencyBag'),
        social_welfare_number=json_payload.get('socialWelfareNumber'),
        health_mutual_id=json_payload.get('healthMutualId'),
        referring_doctor_id=json_payload.get('referringDoctorId'),
        psychiatrist_id=json_payload.get('psychiatristId')
    )

    db.session.add(resident)
    db.session.commit()

    if json_payload.get('emergencyRelationships') is not None:
        for emergency_relationship_row in json_payload.get('emergencyRelationships'):
            create_emergency_relationship(person_id, emergency_relationship_row)


    if json_payload.get('contributionRelationships') is not None:
        for contribution_relationship_row in json_payload.get('contributionRelationships'):
            create_contribution_relationship(person_id, contribution_relationship_row)

    return person_id


def create_contributor(json_payload: dict, contributor_id: str = None):
    person_id = contributor_id

    if person_id is None:
        person_id = create_person(json_payload)


    contributor=Contributor(
        id=person_id,
        role=json_payload.get('role'),
    )

    db.session.add(contributor)
    db.session.commit()

    return person_id


def create_health_mutual(json_payload: dict):
    health_mutual_id=get_random_id(8)

    health_mutual=HealthMutual(
        id=health_mutual_id,
        address=json_payload.get('address'),
        phone_number=json_payload.get('phoneNumber'),
    )

    db.session.add(health_mutual)
    db.session.commit()

    return health_mutual_id


def create_phone_numbers(person_id: str, phone_numbers: list):

    for phone_number_item in phone_numbers:
        phone_number=PhoneNumber(
                    phone_number=phone_number_item, person_id=person_id)
        db.session.add(phone_number)

    db.session.commit()

    return None


def create_emergency_relationship(resident_id: str, json_payload: dict):

    emergency_relationship_id = get_random_id(8)

    emergency_relationship=EmergencyRelationship(id=emergency_relationship_id, resident_id=resident_id, person_id=json_payload.get(
        'personId'), relationship=json_payload.get('relationship'))

    db.session.add(emergency_relationship)
    db.session.commit()

    return emergency_relationship_id


def create_contribution_relationship(resident_id: str, json_payload: dict):
    contribution_relationship_id = get_random_id(8)

    contribution_relationship = ContributionRelationship(id=contribution_relationship_id, resident_id=resident_id, contributor_id=json_payload.get(
        'contributorId'), social_advising=json_payload.get('socialAdvising'))

    db.session.add(contribution_relationship)
    db.session.commit()

    return contribution_relationship_id


@app.route('/persons', methods=['GET', 'POST'])
def persons_collection():
    if request.method == 'GET':
        pass
    elif request.method == 'POST':
        # extract the information
        payload = request.json

        person_id = create_person(payload)

    return json.dumps({'id': person_id})


@app.route('/residents', methods=['GET', 'POST'])
def residents_collection():
    if request.method == 'GET':
        pass
    elif request.method == 'POST':
        # extract the information
        payload = request.json

        resident_id = create_resident(payload)

    return json.dumps({'id': resident_id})


@app.route('/contributors', methods=['GET', 'POST'])
def contributors_collection():
    if request.method == 'GET':
        pass
    elif request.method == 'POST':
        # extract the information
        payload = request.json

        contributor_id = create_contributor(payload)

    return json.dumps({'id': contributor_id})


@app.route('/health-mutuals', methods=['GET', 'POST'])
def health_mutual_collection():
    if request.method == 'GET':
        pass
    elif request.method == 'POST':
        # extract the information
        payload = request.json

        health_mutual_id = create_health_mutual(payload)

    return json.dumps({'id': health_mutual_id})


@app.route('/persons/<string:id>/phone-numbers', methods=['GET, POST'])
@app.route('/residents/<string:id>/phone-numbers', methods=['GET, POST'])
@app.route('/contributors/<string:id>/phone-numbers', methods=['GET, POST'])
def phone_numbers_collection(id: str):
    if request.method == 'POST':
        payload = request.json
        create_phone_numbers(id, payload)

    return None


@app.route('/residents/<string:id>/emergency-relationships', methods=['GET, POST'])
def emergency_relationships_collection(id):
    if request.method == 'POST':
        payload = request.json
        create_emergency_relationship(id, payload)

    return None


@app.route('/residents/<string:id>/contribution-relationships', methods=['GET, POST'])
def contribution_relationships_collection(id):
    if request.method == 'POST':
        payload = request.json
        create_contribution_relationship(id, payload)

    return None


@app.route('/residents/<string:resident_id>', methods=['GET', 'PATCH', 'PUT', 'DELETE'])
def resident_item(resident_id):
    if request.method == 'GET':
        query = db.session.query(
            Person,
            Resident,
            PhoneNumber,
            HealthMutual,
            EmergencyRelationship,
            ContributionRelationship) \
            .filter(Person.id == resident_id) \
            .join(Resident, Resident.id == Person.id) \
            .outerjoin(PhoneNumber, PhoneNumber.person_id == Person.id) \
            .outerjoin(HealthMutual, HealthMutual.id == Resident.health_mutual_id) \
            .outerjoin(EmergencyRelationship, EmergencyRelationship.resident_id == Resident.id) \
            .outerjoin(ContributionRelationship, ContributionRelationship.resident_id == Resident.id)

    return json.dumps(str(query.statement))


def get_person(person_id):
    query = db.session.query(Person).get(person_id)

    result = query.one()

    json_response = {
        'id': result.id,
        'firstName': result.first_name,
        'lastName': result.last_name
    }