import datetime
import src.utils as utils
from flask import Flask, request, Response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm.exc import NoResultFound
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
def get_list_items(model: db.Model, schema: ma.SQLAlchemyAutoSchema) -> list:
    """Get a list of rows of given 'model' in the DB and then 
    serialize it with the given 'schema'.

    Args:
        model (db.Model): the type of rows expected
        schema (ma.SQLAlchemyAutoSchema): the schema to serialize your model rows with
    Returns:
        Response: HTTP status code and list of serialized rows in JSON
    """
    items = model.query.all()
    list_result = schema.dump(items)
    return utils.http_response(utils.HTTPStatus.OK, list_result)


def get_item_by_id(model: db.Model, schema: ma.SQLAlchemyAutoSchema, id: str) -> Response:
    """Get a single row with given 'id' of given 'model' in the DB and then 
    serialize it with the given 'schema'.

    Args:
        model (db.Model): the type of row expected
        schema (ma.SQLAlchemyAutoSchema): the schema to serialize your model row with
        id (str): the id of the row expected

    Returns:
        Response: HTTP status code and serialized row in JSON
    """
    try:
        item = model.query.filter_by(id=id).one()
    except NoResultFound:
        return {"message": f"{id} could not be found."}, 404
    item_result = schema.dump(item)
    return utils.http_response(utils.HTTPStatus.OK, item_result)


def update_item_by_id(model: db.Model, schema: ma.SQLAlchemyAutoSchema, id: str) -> Response:
    """Update a single row with given 'id' of given 'model' in the DB and then 
    serialize it with the given 'schema'.
    Tipycally for PUT or PATCH API methods

    Args:
        model (db.Model): the type of row expected
        schema (ma.SQLAlchemyAutoSchema): the schema to serialize your model row with
        id (str): the id of the row expected to b updated

    Returns:
        Response: HTTP status code and serialized updated row in JSON
    """
    json_data = request.get_json()

    if not json_data:
        return {"message": "No input data provided"}, 400

    try:
        item = model.query.get(id: str)
        item.update(json_data)

    except ValidationError as err:
        db.session.rollback()
        return err.messages, 422
    except InvalidRequestException as err:
        db.session.rollback()
        return err.message, err.status_code

    db.session.commit()
    item_result = schema.dump(item)
    return utils.http_response(utils.HTTPStatus.OK, item_result)


def delete_item_by_id(model: db.Model, id: str) -> Response:
    """Delete a single row with given 'id' of given 'model' in the DB

    Args:
        model (db.Model): the type of row expected
        schema (ma.SQLAlchemyAutoSchema): the schema to serialize your model row with
        id (str): the id of the row expected

    Returns:
        Response: HTTP status code
    """
    model.query.filter_by(id=id).delete()
    db.session.commit()
    return utils.http_response(utils.HTTPStatus.NO_CONTENT, None)


def create_new_item(
    model: db.Model,
    schema: ma.SQLAlchemyAutoSchema
) -> dict:
    """Creates a new row of given 'model' in the DB and then returns it
    serialized 'schema'. Generates a random id when none is passed in request.
    Tipycally for POST methods

    Args:
        model (db.Model): the type of row expected
        schema (ma.SQLAlchemyAutoSchema): the schema to serialize your model row with

    Returns:
        dict: serialized new row in JSON
    """
    json_data = request.get_json()
    if not json_data:
        return {"message": "No input data provided"}, 400

    # Validate and deserialize input
    try:
        if not json_data.get("id"):
            json_data["id"] = utils.random_id(8)
        item = schema.load(json_data)
    except ValidationError as err:
        return err.messages, 422

    db.session.add(item)
    db.session.commit()
    result = schema.dump(model.query.get(item.id))
    return utils.http_response(utils.HTTPStatus.CREATED, result)


@app.route("/persons")
def get_persons() -> utils.Response:
    return get_list_items(Person, persons_schema)


@app.route("/persons/<string:id>")
def get_person(id: str) -> utils.Response:
    return get_item_by_id(Person, person_schema, id)


@app.route("/persons", methods=["POST"])
def new_person() -> utils.Response:
    return create_new_item(Person, person_schema)


@app.route("/persons/<string:id>", methods=["PUT", "PATCH"])
def update_person(id: str) -> utils.Response:
    return update_item_by_id(Person, person_schema, id)


@app.route("/persons/<string:id>", methods=["DELETE"])
def delete_person(id: str) -> utils.Response:
    return delete_item_by_id(model, id)


@app.route("/residents")
def get_residents() -> utils.Response:
    return get_list_items(Resident, residents_schema)


@app.route("/residents", methods=["POST"])
def new_resident() -> utils.Response:
    return create_new_item(Resident, resident_schema)


@app.route("/residents/<string:id>")
def get_resident(id: str) -> utils.Response:
    return get_item_by_id(Resident, resident_schema, id)


@app.route("/residents/<string:id>", methods=["DELETE"])
def delete_resident(id: str) -> utils.Response:
    return delete_item_by_id(Resident, id)


@app.route("/residents/<string:id>", methods=["PUT", "PATCH"])
def update_resident(id: str) -> utils.Response:
    return update_item_by_id(Resident, resident_schema, id)


@app.route("/cities")
def get_cities() -> utils.Response:
    return get_list_items(City, cities_schema)


@app.route("/cities", methods=["POST"])
def new_city() -> utils.Response:
    return create_new_item(City, city_schema)


@app.route("/cities/<string:id>")
def get_city(id: str) -> utils.Response:
    return get_item_by_id(City, city_schema, id)


@app.route("/cities/<string:id>", methods=["DELETE"])
def delete_city(id: str) -> utils.Response:
    return delete_item_by_id(City, id)


@app.route("/cities/<string:id>", methods=["PUT", "PATCH"])
def update_city(id: str) -> utils.Response:
    return update_item_by_id(City, city_schema, id)


@app.route("/contributors")
def get_contributors() -> utils.Response:
    return get_list_items(Contributor, contributors_schema)


@app.route("/contributors/<string:id>")
def get_contributor(id: str) -> utils.Response:
    return get_item_by_id(Contributor, contributor_schema, id)


@app.route("/contributors", methods=["POST"])
def new_contributor() -> utils.Response:
    return create_new_item(Contributor, contributor_schema)


@app.route("/contributors/<string:id>", methods=["PUT", "PATCH"])
def update_contributor(id: str) -> utils.Response:
    return update_item_by_id(Contributor, contributor_schema, id)


@app.route("/contributors/<string:id>", methods=["DELETE"])
def delete_contributor(id: str) -> utils.Response:
    return delete_item_by_id(Contributor, id)


@app.route("/health_mutuals")
def get_health_mutuals() -> utils.Response:
    return get_list_items(HealthMutual, health_mutuals_schema)


@app.route("/health_mutuals/<string:id>")
def get_health_mutual(id: str) -> utils.Response:
    return get_item_by_id(HealthMutual, health_mutual_schema, id)


@app.route("/health_mutuals", methods=["POST"])
def new_health_mutual() -> utils.Response:
    return create_new_item(HealthMutual, health_mutual_schema)


@app.route("/health_mutuals/<string:id>", methods=["PUT", "PATCH"])
def update_health_mutual(id: str) -> utils.Response:
    return update_item_by_id(HealthMutual, health_mutual_schema, id)


@app.route("/health_mutuals/<string:id>", methods=["DELETE"])
def delete_health_mutual(id: str) -> utils.Response:
    return delete_item_by_id(HealthMutual, id)


@app.route('/db-reset', methods=['POST'])
def reset_db() -> utils.Response:
    """ Reset database """
    db.drop_all()
    db.create_all()

    return utils.http_response(utils.HTTPStatus.NO_CONTENT, None)


if __name__ == "__main__":
    db.create_all()
    app.run(debug=True, port=5000)
