import json
import src.utils as utils

from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'

db = SQLAlchemy(app)


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


class City(db.Model):
    id = db.Column(db.String, primary_key=True)

    name = db.Column(db.String, index=True)
    postal_code = db.Column(db.String)

    residents = db.relationship(
        'Resident', backref='city', lazy=True, foreign_keys='[Resident.city_id]')


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

    city_id = db.Column(
        db.String, db.ForeignKey('city.id'), nullable=True)
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

##############


def create_person(json_payload: dict) -> dict:
    person_id = utils.random_id(8)

    person = Person(
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

    return {'id': person_id}


def create_resident(json_payload: dict, person_id: str = None) -> dict:
    resident_id = person_id

    if resident_id is None:
        resident_id = create_person(json_payload).get('id')

    resident = Resident(
        id=resident_id,
        birth_date=json_payload.get('birthDate'),
        birthplace=json_payload.get('birthplace'),
        entrance_date=json_payload.get('entranceDate'),
        emergency_bag=json_payload.get('emergencyBag'),
        social_welfare_number=json_payload.get('socialWelfareNumber'),
        health_mutual_id=json_payload.get('healthMutualId'),
        referring_doctor_id=json_payload.get('referringDoctorId'),
        psychiatrist_id=json_payload.get('psychiatristId'),
        city_id=json_payload.get('cityId'),
    )

    db.session.add(resident)
    db.session.commit()

    emergency_relationship_ids = []

    if json_payload.get('emergencyRelationships') is not None:
        for emergency_relationship_row in json_payload.get('emergencyRelationships'):
            emergency_relationship_ids.append(create_emergency_relationship(
                resident_id, emergency_relationship_row).get('id'))

    contribution_relationship_ids = []

    if json_payload.get('contributionRelationships') is not None:
        for contribution_relationship_row in json_payload.get('contributionRelationships'):
            contribution_relationship_ids.append(create_contribution_relationship(
                resident_id, contribution_relationship_row).get('id'))

    return {
        'id': resident_id,
        'emergencyRelationships': emergency_relationship_ids,
        'contributionRelationships': contribution_relationship_ids
    }


def create_contributor(json_payload: dict, person_id: str = None) -> dict:
    contributor_id = person_id

    if contributor_id is None:
        contributor_id = create_person(json_payload).get('id')
    contributor = Contributor(
        id=contributor_id,
        role=json_payload.get('role'),
    )

    db.session.add(contributor)
    db.session.commit()

    return {'id': contributor_id}


def create_health_mutual(json_payload: dict) -> dict:
    health_mutual_id = utils.random_id(8)

    health_mutual = HealthMutual(
        id=health_mutual_id,
        address=json_payload.get('address'),
        phone_number=json_payload.get('phoneNumber'),
    )

    db.session.add(health_mutual)
    db.session.commit()

    return {'id': health_mutual_id}


def create_city(json_payload: dict) -> dict:
    city_id = utils.random_id(8)

    city = City(
        id=city_id,
        name=json_payload.get('name'),
        postal_code=json_payload.get('postalCode'),
    )

    db.session.add(city)
    db.session.commit()

    return {'id': city_id}


def create_phone_numbers(person_id: str, phone_numbers: list) -> dict:

    phone_numbers_ids = []

    for phone_number_item in phone_numbers:
        phone_number_id = utils.random_id(8)

        phone_number = PhoneNumber(id=phone_number_id,
                                   phone_number=phone_number_item,
                                   person_id=person_id)

        db.session.add(phone_number)

        phone_numbers_ids.append(phone_number_id)

    db.session.commit()

    return {"id": phone_numbers_ids}


def create_emergency_relationship(resident_id: str, json_payload: dict) -> dict:

    emergency_relationship_id = utils.random_id(8)

    emergency_relationship = EmergencyRelationship(id=emergency_relationship_id, resident_id=resident_id, person_id=json_payload.get(
        'personId'), relationship=json_payload.get('relationship'))

    db.session.add(emergency_relationship)
    db.session.commit()

    return {'id': emergency_relationship_id}


def create_contribution_relationship(resident_id: str, json_payload: dict) -> dict:
    contribution_relationship_id = utils.random_id(8)

    contribution_relationship = ContributionRelationship(id=contribution_relationship_id, resident_id=resident_id, contributor_id=json_payload.get(
        'contributorId'), social_advising=json_payload.get('socialAdvising'))

    db.session.add(contribution_relationship)
    db.session.commit()

    return {'id': contribution_relationship_id}

################


def get_persons() -> list:
    """ dict or list response """
    result = db.session.query(
        Person.id, Person.first_name, Person.last_name).all()

    persons_list = []

    for row in result:
        persons_list.append({
            'id': row[0],
            'firstName': row[1],
            'lastName': row[2]
        })

    return persons_list


def get_person(person_id) -> dict:
    """ dict or list response """
    result = db.session.query(Person).get(person_id)

    json_response = {
        'id': result.id,
        'firstName': result.first_name,
        'lastName': result.last_name,
        'address': result.address,
    }

    return json_response


def get_contributor(contributor_id) -> dict:
    """ dict or list response """
    result = db.session.query(Contributor, Person).filter(Contributor.id == contributor_id).outerjoin(Person, Person.id == Contributor.id).one()

    json_response = {
        'id': result.Person.id,
        'firstName': result.Person.first_name,
        'lastName': result.Person.last_name,
        'address': result.Person.address,
        'role': result.Contributor.role
    }

    return json_response


def get_city(city_id) -> dict:
    """ dict or list response """
    result = db.session.query(City).get(city_id)

    json_response = {
        'id': result.id,
        'name': result.name,
        'postalCode': result.postal_code,
    }

    return json_response


def get_cities() -> list:
    """ dict or list response """
    result = db.session.query(
        City.id, City.name).all()

    cities_list = []

    for row in result:
        cities_list.append({
            'id': row[0],
            'name': row[1]
        })

    return persons_list


def get_residents() -> list:
    residents_list = []

    residents_info = db.session.query(Resident.id, Resident.city_id).all()

    for resident_info in residents_info:

        person_info = get_person(resident_info[0])
        city_info = get_city(resident_info[1])

        residents_list.append({
            'id': resident_info[0],
            'firstName': person_info.get('firstName'),
            'lastName': person_info.get('lastName'),
            'city': city_info
        })

    return residents_list


def get_contributors() -> list:
    contributors_list = []

    contributors_info = db.session.query(Contributor.id, Contributor.role).all()

    for contributor_info in contributors_info:

        person_info = get_person(contributor_info[0])

        contributors_list.append({
            'id': contributor_info[0],
            'firstName': person_info.get('firstName'),
            'lastName': person_info.get('lastName'),
            'role': contributor_info[1]
        })

    return contributors_list


def get_health_mutuals() -> list:
    """ dict or list response """
    result = db.session.query(HealthMutual.id, HealthMutual.name).all()

    health_mutuals_list = []

    for row in result:
        health_mutuals_list.append({
            'id': row[0],
            'name': row[1]
        })

    return health_mutuals_list

################


@app.route('/persons', methods=['GET', 'POST'])
def persons_collection() -> utils.Response:
    if request.method == 'GET':
        return utils.http_response(utils.HTTPStatus.OK, get_persons())
    elif request.method == 'POST':
        return utils.http_response(utils.HTTPStatus.CREATED, create_person(request.json))


@app.route('/persons/<string:id>', methods=['GET'])
def person_item(id: str) -> utils.Response:
    if request.method == 'GET':
        return utils.http_response(utils.HTTPStatus.OK, get_person(id))


@app.route('/residents', methods=['GET', 'POST'])
def residents_collection() -> utils.Response:
    if request.method == 'GET':
        return utils.http_response(utils.HTTPStatus.OK, get_residents())
    elif request.method == 'POST':
        return utils.http_response(utils.HTTPStatus.CREATED, create_resident(request.json))


@app.route('/residents/<string:id>/emergency-relationships', methods=['POST'])
def emergency_relationships_collection(id: str) -> utils.Response:
    if request.method == 'POST':
        return utils.http_response(utils.HTTPStatus.CREATED, create_emergency_relationship(id, request.json))


@app.route('/residents/<string:id>/contribution-relationships', methods=['POST'])
def contribution_relationships_collection(id: str) -> utils.Response:
    if request.method == 'POST':
        return utils.http_response(utils.HTTPStatus.CREATED, create_contribution_relationship(id, request.json))


@app.route('/residents/<string:resident_id>', methods=['GET'])
def resident_item(id: str) -> utils.Response:
    if request.method == 'GET':
        query = db.session.query(
            Person,
            Resident,
            PhoneNumber,
            HealthMutual,
            EmergencyRelationship,
            ContributionRelationship) \
            .filter(Person.id == id) \
            .join(Resident, Resident.id == Person.id) \
            .outerjoin(PhoneNumber, PhoneNumber.person_id == Person.id) \
            .outerjoin(HealthMutual, HealthMutual.id == Resident.health_mutual_id) \
            .outerjoin(EmergencyRelationship, EmergencyRelationship.resident_id == Resident.id) \
            .outerjoin(ContributionRelationship, ContributionRelationship.resident_id == Resident.id)

    return json.dumps(str(query.statement))


@app.route('/cities', methods=['GET', 'POST'])
def cities_collection() -> utils.Response:
    if request.method == 'GET':
        return utils.http_response(utils.HTTPStatus.OK, get_cities(request.json)) 
    if request.method == 'POST':
        return utils.http_response(utils.HTTPStatus.CREATED, create_city(request.json))


@app.route('/contributors', methods=['GET', 'POST'])
def contributors_collection() -> utils.Response:
    if request.method == 'GET':
        return utils.http_response(utils.HTTPStatus.OK, get_contributors())
    if request.method == 'POST':
        return utils.http_response(utils.HTTPStatus.CREATED, create_contributor(request.json))


@app.route('/contributors/<string:id>', methods=['GET'])
def contributor_item(id: str) -> utils.Response:
    if request.method == 'GET':
        return utils.http_response(utils.HTTPStatus.OK, get_contributor(id))


@app.route('/health-mutuals', methods=['GET', 'POST'])
def health_mutual_collection() -> utils.Response:
    if request.method == 'GET':
        return utils.http_response(utils.HTTPStatus.CREATED, get_health_mutuals())
    elif request.method == 'POST':
        return utils.http_response(utils.HTTPStatus.CREATED, create_health_mutual(request.json))


@app.route('/persons/<string:id>/phone-numbers', methods=['POST'])
@app.route('/residents/<string:id>/phone-numbers', methods=['POST'])
@app.route('/contributors/<string:id>/phone-numbers', methods=['POST'])
def phone_numbers_collection(id: str) -> utils.Response:
    if request.method == 'POST':
        return utils.http_response(utils.HTTPStatus.CREATED, create_phone_numbers(id, request.json))


@app.route('/db-reset', methods=['POST'])
def reset_db() -> utils.Response:
    db.drop_all()
    db.create_all()

    return utils.http_response(utils.HTTPStatus.NO_CONTENT, None)
