import datetime
import src.utils as utils
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from flask_marshmallow import Marshmallow
from marshmallow import Schema, fields, ValidationError, post_load
from exceptions import InvalidRequestException

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"
db = SQLAlchemy(app)
ma = Marshmallow(app)

##### MODELS #####


class ModelMixin(object):

    def update(self: db.Model, new_values: dict) -> db.Model:
        """Update an object with new values.

        Args:
            new_values (dict): New values to update the object with
        Returns:
            db.Model: the updated db.Model object
        Raises: 
            InvalidRequestException: If there is key 'id' in 'new_values'.
        """
        if new_values.get("id"):
            raise InvalidRequestException("Forbidden to update id")

        for attr, value in new_values.items():
            self.__setattr__(attr, value)

        return self


class Person(ModelMixin, db.Model):
    id = db.Column(db.String, primary_key=True)
    first_name = db.Column(db.String, index=True, nullable=False)
    last_name = db.Column(db.String, index=True, nullable=False)
    address = db.Column(db.String)
    main_phone_number = db.Column(db.String)
    alternative_phone_number = db.Column(db.String)

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


class City(ModelMixin, db.Model):
    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String, index=True)
    postal_code = db.Column(db.String)
    residents = db.relationship(
        'Resident', backref='city', lazy=True, foreign_keys='[Resident.city_id]')


class Contributor(ModelMixin, db.Model):
    id = db.Column(db.String, db.ForeignKey('person.id'), primary_key=True)
    role = db.Column(db.String, nullable=True)
    contribution_relationships = db.relationship(
        'ContributionRelationship', foreign_keys='[ContributionRelationship.contributor_id]')


class HealthMutual(ModelMixin, db.Model):
    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String, index=True)
    address = db.Column(db.String, index=True)
    main_phone_number = db.Column(db.String)
    alternative_phone_number = db.Column(db.String)

    residents = db.relationship('Resident', backref='health_mutual',
                                lazy=True, foreign_keys='[Resident.health_mutual_id]')


class Resident(ModelMixin, db.Model):
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


class EmergencyRelationship(ModelMixin, db.Model):
    id = db.Column(db.String, primary_key=True)

    resident_id = db.Column(db.String, db.ForeignKey(
        'resident.id'))
    person_id = db.Column(db.String, db.ForeignKey(
        'person.id'))
    relationship = db.Column(db.String)


class ContributionRelationship(ModelMixin, db.Model):
    id = db.Column(db.String, primary_key=True)

    resident_id = db.Column(db.String, db.ForeignKey(
        'resident.id'))
    contributor_id = db.Column(db.String, db.ForeignKey(
        'contributor.id'))
    social_advising = db.Column(db.Boolean)


##### SCHEMAS #####
class SchemaMixin(object):
    @post_load
    def make_object(self, data, **kwargs):

        return self.Meta.model(**data)


def must_not_be_blank(data):
    if not data:
        raise ValidationError("Data not provided.")


class PersonSchema(SchemaMixin, ma.SQLAlchemyAutoSchema):
    class Meta:
        include_fk = True
        model = Person


class CitySchema(SchemaMixin, ma.SQLAlchemyAutoSchema):
    class Meta:
        include_fk = True
        model = City


class ContributorSchema(SchemaMixin, ma.SQLAlchemyAutoSchema):
    class Meta:
        include_fk = True
        model = Contributor


class HealthMutualSchema(SchemaMixin, ma.SQLAlchemyAutoSchema):
    class Meta:
        include_fk = True
        model = HealthMutual


class ResidentSchema(SchemaMixin, ma.SQLAlchemyAutoSchema):
    class Meta:
        include_fk = True
        model = Resident
    person = fields.Nested(PersonSchema)
    city = fields.Nested(CitySchema)


class EmergencyRelationshipSchema(SchemaMixin, ma.SQLAlchemyAutoSchema):
    class Meta:
        include_fk = True
        model = EmergencyRelationship


person_schema = PersonSchema()
persons_schema = PersonSchema(many=True)
resident_schema = ResidentSchema()
residents_schema = ResidentSchema(many=True)
city_schema = CitySchema()
cities_schema = CitySchema(many=True)
contributor_schema = ContributorSchema()
contributors_schema = ContributorSchema(many=True)
health_mutual_schema = HealthMutualSchema()
health_mutuals_schema = HealthMutualSchema(many=True)
emergency_relationship_schema = EmergencyRelationshipSchema()
emergency_relationships_schema = EmergencyRelationshipSchema(many=True)


##### API #####


@app.route("/persons")
def get_persons():
    persons = Person.query.all()
    # Serialize the queryset
    result = persons_schema.dump(persons)
    return {"persons": result}


@app.route("/persons/<string:id>")
def get_person(id):
    try:
        person = Person.query.filter_by(id=id).one()
    except IntegrityError:
        return {"message": "Person could not be found."}, 400
    person_result = person_schema.dump(person)
    return {"person": person_result}


@app.route("/persons", methods=["POST"])
def new_person():
    json_data = request.get_json()
    if not json_data:
        return {"message": "No input data provided"}, 400

    # Validate and deserialize input
    try:
        json_data["id"] = utils.random_id(8)
        person = person_schema.load(json_data)
    except ValidationError as err:
        return err.messages, 422

    db.session.add(person)
    db.session.commit()
    result = person_schema.dump(Person.query.get(person.id))
    return {"person": result}


@app.route("/persons/<string:id>", methods=["PUT", "PATCH"])
def update_person(id):

    json_data = request.get_json()

    if not json_data:
        return {"message": "No input data provided"}, 400

    try:
        person = Person.query.get(id)
        person.update(json_data)

    except ValidationError as err:
        db.session.rollback()
        return err.messages, 422
    except InvalidRequestException as err:
        db.session.rollback()
        return err.message, err.status_code

    db.session.commit()
    result = person_schema.dump(person)
    return {"person": result}


@app.route("/persons/<string:id>", methods=["DELETE"])
def delete_person(id):
    Person.query.filter_by(id=id).delete()
    db.session.commit()
    return {"message": "Person deleted"}, 204


@app.route("/residents")
def get_residents():
    residents = Resident.query.all()
    result = residents_schema.dump(residents)
    return {"residents": result}


@app.route("/residents", methods=["POST"])
def new_resident():
    json_data = request.get_json()
    if not json_data:
        return {"message": "No input data provided"}, 400
    try:
        resident = resident_schema.load(json_data)
    except ValidationError as err:
        return err.messages, 422

    db.session.add(resident)
    db.session.commit()
    result = resident_schema.dump(Resident.query.get(resident.id))
    return {"resident": result}


@app.route("/residents/<string:id>")
def get_resident(id):
    try:
        resident = Resident.query.filter_by(id=id).one()
    except IntegrityError:
        return {"message": "Resident could not be found."}, 400
    resident_result = resident_schema.dump(resident)
    return {"resident": resident_result}


@app.route("/residents/<string:id>", methods=["DELETE"])
def delete_resident(id):
    Resident.query.filter_by(id=id).delete()
    db.session.commit()
    return {"message": "Resident deleted"}, 204


@app.route("/residents/<string:id>", methods=["PUT", "PATCH"])
def update_resident(id):

    json_data = request.get_json()

    if not json_data:
        return {"message": "No input data provided"}, 400

    try:
        resident = Resident.query.get(id)
        resident.update(json_data)

    except ValidationError as err:
        db.session.rollback()
        return err.messages, 422
    except InvalidRequestException as err:
        db.session.rollback()
        return err.message, err.status_code

    db.session.commit()
    result = resident_schema.dump(resident)
    return {"resident": result}

@app.route("/cities")
def get_cities():
    cities = City.query.all()
    result = cities_schema.dump(cities)
    return {"cities": result}


@app.route("/cities", methods=["POST"])
def new_city():
    json_data = request.get_json()
    if not json_data:
        return {"message": "No input data provided"}, 400
    try:
        json_data["id"] = utils.random_id(8)
        city = city_schema.load(json_data)
    except ValidationError as err:
        return err.messages, 422

    db.session.add(city)
    db.session.commit()
    result = city_schema.dump(City.query.get(city.id))
    return {"city": result}


@app.route("/cities/<string:id>")
def get_city(id):
    try:
        city = City.query.filter_by(id=id).one()
    except IntegrityError:
        return {"message": "City could not be found."}, 400
    city_result = city_schema.dump(city)
    return {"city": city_result}


@app.route("/cities/<string:id>", methods=["DELETE"])
def delete_city(id):
    City.query.filter_by(id=id).delete()
    db.session.commit()
    return {"message": "City deleted"}, 204


@app.route("/cities/<string:id>", methods=["PUT", "PATCH"])
def update_city(id):

    json_data = request.get_json()

    if not json_data:
        return {"message": "No input data provided"}, 400

    try:
        city = City.query.get(id)
        city.update(json_data)

    except ValidationError as err:
        db.session.rollback()
        return err.messages, 422
    except InvalidRequestException as err:
        db.session.rollback()
        return err.message, err.status_code

    db.session.commit()
    result = city_schema.dump(city)
    return {"city": result}





@app.route('/db-reset', methods=['POST'])
def reset_db() -> utils.Response:
    db.drop_all()
    db.create_all()

    return utils.http_response(utils.HTTPStatus.NO_CONTENT, None)


if __name__ == "__main__":
    db.create_all()
    app.run(debug=True, port=5000)
