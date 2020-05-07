import datetime
import src.utils as utils
from flask import Flask, request, Response
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import PrimaryKeyConstraint
from flask_marshmallow import Marshmallow
from marshmallow import Schema, fields, ValidationError, post_load
from exceptions import InvalidRequestException

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"
cors = CORS(app)
db = SQLAlchemy(app)
ma = Marshmallow(app)


#   __  __  ___  ____  _____ _     ____
#  |  \/  |/ _ \|  _ \| ____| |   / ___|
#  | |\/| | | | | | | |  _| | |   \___ \
#  | |  | | |_| | |_| | |___| |___ ___) |
#  |_|  |_|\___/|____/|_____|_____|____/


class ModelMixin(object):

    def update(self: db.Model, new_values: dict) -> db.Model:
        """ Updates an object with new values.

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
    firstName = db.Column(db.String, index=True, nullable=False)
    lastName = db.Column(db.String, index=True, nullable=False)
    address = db.Column(db.String)
    mainPhoneNumber = db.Column(db.String)
    alternativePhoneNumber = db.Column(db.String)

    contributors = db.relationship(
        'Contributor', backref='person', lazy=True, foreign_keys='[Contributor.id]')
    residents = db.relationship(
        'Resident', backref='person', lazy=True, foreign_keys='[Resident.id]')
    referringDoctors = db.relationship(
        'Resident', backref='doctor', lazy=True, foreign_keys='[Resident.referringDoctorId]')
    psychiatrists = db.relationship(
        'Resident', backref='psychiatrist', lazy=True, foreign_keys='[Resident.psychiatrist_id]')

    emergencyRelationships = db.relationship(
        'EmergencyRelationship', foreign_keys='[EmergencyRelationship.personId]')


class City(ModelMixin, db.Model):
    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String, index=True)
    postal_code = db.Column(db.String)
    residents = db.relationship(
        'Resident', backref='city', lazy=True, foreign_keys='[Resident.cityId]')


class Contributor(ModelMixin, db.Model):
    id = db.Column(db.String, db.ForeignKey('person.id'), primary_key=True)
    role = db.Column(db.String, nullable=True)
    contributionRelationships = db.relationship(
        'ContributionRelationship', foreign_keys='[ContributionRelationship.contributorId]')


class HealthMutual(ModelMixin, db.Model):
    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String, index=True)
    address = db.Column(db.String, index=True)
    mainPhoneNumber = db.Column(db.String)
    alternativePhoneNumber = db.Column(db.String)

    residents = db.relationship('Resident', backref='health_mutual',
                                lazy=True, foreign_keys='[Resident.healthMutualId]')


class Resident(ModelMixin, db.Model):
    id = db.Column(db.String, db.ForeignKey('person.id'), primary_key=True)

    birthDate = db.Column(db.Date)
    birthplace = db.Column(db.String)
    entranceDate = db.Column(db.Date)
    emergencyBag = db.Column(db.String)
    socialWelfareNumber = db.Column(db.String)

    cityId = db.Column(
        db.String, db.ForeignKey('city.id'), nullable=True)
    healthMutualId = db.Column(
        db.String, db.ForeignKey('health_mutual.id'), nullable=True)
    referringDoctorId = db.Column(
        db.String, db.ForeignKey('person.id'), nullable=True)
    psychiatrist_id = db.Column(
        db.String, db.ForeignKey('person.id'), nullable=True)

    emergencyRelationships = db.relationship(
        'EmergencyRelationship', foreign_keys='[EmergencyRelationship.residentId]')
    contributionRelationships = db.relationship(
        'ContributionRelationship', foreign_keys='[ContributionRelationship.residentId]')


class EmergencyRelationship(ModelMixin, db.Model):
    id = db.Column(db.String, primary_key=True)
    residentId = db.Column(db.String, db.ForeignKey('resident.id'))
    personId = db.Column(db.String, db.ForeignKey('person.id'))
    relationship = db.Column(db.String)


class ContributionRelationship(ModelMixin, db.Model):
    id = db.Column(db.String, primary_key=True)
    contributorId = db.Column(db.String, db.ForeignKey(
        'contributor.id'))
    socialAdvising = db.Column(db.Boolean)
    residentId = db.Column(db.String, db.ForeignKey(
        'resident.id'))


#   ____   ____ _   _ _____ __  __    _    ____
#  / ___| / ___| | | | ____|  \/  |  / \  / ___|
#  \___ \| |   | |_| |  _| | |\/| | / _ \ \___ \
#   ___) | |___|  _  | |___| |  | |/ ___ \ ___) |
#  |____/ \____|_| |_|_____|_|  |_/_/   \_\____/


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
    health_mutual = fields.Nested(HealthMutualSchema)
    doctor = fields.Nested(PersonSchema)
    psychiatrist = fields.Nested(PersonSchema)


class EmergencyRelationshipSchema(SchemaMixin, ma.SQLAlchemyAutoSchema):
    class Meta:
        include_fk = True
        model = EmergencyRelationship


class ContributionRelationshipSchema(SchemaMixin, ma.SQLAlchemyAutoSchema):
    class Meta:
        include_fk = True
        model = ContributionRelationship


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
emergencyRelationships_schema = EmergencyRelationshipSchema(many=True)
contribution_relationship_schema = ContributionRelationshipSchema()
contributionRelationships_schema = ContributionRelationshipSchema(many=True)


#      _    ____ ___
#     / \  |  _ \_ _|
#    / _ \ | |_) | |
#   / ___ \|  __/| |
#  /_/   \_\_|  |___|


# Generic CRUD functions

def get_collection(model: db.Model, schema: ma.SQLAlchemyAutoSchema) -> list:
    """ Gets a list of rows of given 'model' in the DB and then 
    serializes it with the given 'schema'.

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
    """ Gets a single row with given 'id' of given 'model' in the DB and then 
    serializes it with the given 'schema'.

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
    """Updates a single row with given 'id' of given 'model' in the DB and then 
    serializes it with the given 'schema'.
    Tipycally for PUT or PATCH API methods

    Args:
        model (db.Model): the type of row expected
        schema (ma.SQLAlchemyAutoSchema): the schema to serialize your model row with
        id (str): the id of the row expected to b updated

    Returns:
        Response: HTTP status code and serialized updated row in JSON
    """
    payload = request.get_json()

    if not payload:
        return {"message": "No input data provided"}, 400

    try:
        item = model.query.get(id)
        item.update(payload)

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
    """ Deletes a single row with given 'id' of given 'model' in the DB

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
    schema: ma.SQLAlchemyAutoSchema,
    payload: dict = None
) -> dict:
    """ Creates a new row of given 'model' in the DB and then returns it
    serialized 'schema'. Generates a random id when none is passed in request.
    Tipycally for POST methods

    Args:
        model (db.Model): the type of row expected
        schema (ma.SQLAlchemyAutoSchema): the schema to serialize your model row with
        payload (dict, optional): Attributes and values used to create the item
            Defaults to None, in that case the payload will be the parameters 
            passed through the request 
    Returns:
        dict: serialized new row in JSON
    """

    try:
        if not payload:
            payload = request.get_json()

            if not payload:
                return {"message": "No input data provided"}, 400

        if not payload.get("id"):
            payload["id"] = utils.random_id(8)

        # Validate and deserialize input
        item = schema.load(payload)
    except ValidationError as err:
        return err.messages, 422

    db.session.add(item)
    db.session.commit()
    result = schema.dump(model.query.get(item.id))
    return utils.http_response(utils.HTTPStatus.CREATED, result)

# API routes


@app.route("/persons", methods=["GET", "POST"])
def person_collection() -> utils.Response:
    if request.method == "GET":
        return get_collection(Person, persons_schema)
    if request.method == "POST":
        return create_new_item(Person, person_schema)


@app.route("/persons/<string:id>", methods=["GET", "PUT", "PATCH", "DELETE"])
def person_item(id: str) -> utils.Response:
    if request.method == "GET":
        return get_item_by_id(Person, person_schema, id)
    if request.method in ["PUT", "PATCH"]:
        return update_item_by_id(Person, person_schema, id)
    if request.method == "DELETE":
        return delete_item_by_id(model, id)


@app.route("/residents", methods=["GET", "POST"])
def resident_collection() -> utils.Response:
    if request.method == "GET":
        return get_collection(Resident, residents_schema)
    if request.method == "POST":
        return create_new_item(Resident, resident_schema)


@app.route("/residents/<string:id>", methods=["GET", "PUT", "PATCH", "DELETE"])
def resident_item(id: str) -> utils.Response:
    if request.method == "GET":
        return get_item_by_id(Resident, resident_schema, id)
    if request.method in ["PUT", "PATCH"]:
        return update_item_by_id(Resident, resident_schema, id)
    if request.method == "DELETE":
        return delete_item_by_id(Resident, id)


@app.route("/cities", methods=["GET", "POST"])
def cities_collection() -> utils.Response:
    if request.method == "GET":
        return get_collection(City, cities_schema)
    if request.method == "POST":
        return create_new_item(City, city_schema)


@app.route("/cities/<string:id>", methods=["GET", "PUT", "PATCH", "DELETE"])
def city_item(id: str) -> utils.Response:
    if request.method == "GET":
        return get_item_by_id(City, city_schema, id)
    if request.method in ["PUT", "PATCH"]:
        return update_item_by_id(City, city_schema, id)
    if request.method == ["DELETE"]:
        return delete_item_by_id(City, id)


@app.route("/contributors", methods=["GET", "POST"])
def contributor_collection() -> utils.Response:
    if request.method == "GET":
        return get_collection(Contributor, contributors_schema)
    if request.method == "POST":
        return create_new_item(Contributor, contributor_schema)


@app.route("/contributors/<string:id>", methods=["GET", "PUT", "PATCH", "DELETE"])
def contributor_item(id: str) -> utils.Response:
    if request.method == "GET":
        return get_item_by_id(Contributor, contributor_schema, id)
    if request.method in ["PUT", "PATCH"]:
        return update_item_by_id(Contributor, contributor_schema, id)
    if request.method == ["DELETE"]:
        return delete_item_by_id(Contributor, id)


@app.route("/health-mutuals", methods=["GET", "POST"])
def health_mutual_collection() -> utils.Response:
    if request.method == "GET":
        return get_collection(HealthMutual, health_mutuals_schema)
    if request.method == "POST":
        return create_new_item(HealthMutual, health_mutual_schema)


@app.route("/health-mutuals/<string:id>", methods=["GET", "PUT", "PATCH", "DELETE"])
def health_mutual_item(id: str) -> utils.Response:
    if request.method == "GET":
        return get_item_by_id(HealthMutual, health_mutual_schema, id)
    if request.method in ["PUT", "PATCH"]:
        return update_item_by_id(HealthMutual, health_mutual_schema, id)
    if request.method == ["DELETE"]:
        return delete_item_by_id(HealthMutual, id)


@app.route('/residents/<string:id>/emergency-relationships', methods=["GET", "POST"])
def emergency_relationship(id: str) -> utils.Response:
    if request.method == "POST":
        payload = request.get_json()
        payload["residentId"] = id
        return create_new_item(
            EmergencyRelationship,
            emergency_relationship_schema,
            payload
        )

    if request.method == "GET":
        er_collection = EmergencyRelationship.query.filter_by(
            residentId=id).all()
        list_result = emergencyRelationships_schema.dump(er_collection)
        return utils.http_response(utils.HTTPStatus.OK, list_result)


@app.route('/residents/<string:id>/emergency-relationships/<string:er_id>', methods=["GET", "PUT", "PATCH", "DELETE"])
def emergency_relationship_item(id: str, er_id: str) -> utils.Response:
    if request.method == "GET":
        return get_item_by_id(EmergencyRelationship, emergency_relationship_schema, er_id)
    if request.method in ["PUT", "PATCH"]:
        return update_item_by_id(
            EmergencyRelationship,
            emergency_relationship_schema,
            er_id
        )
    if request.method == ["DELETE"]:
        return delete_item_by_id(EmergencyRelationship, er_id)


@app.route('/residents/<string:id>/contribution-relationships', methods=["GET", "POST"])
def contributionRelationships_collection(id: str) -> utils.Response:
    if request.method == "GET":
        er_collection = ContributionRelationship.query.filter_by(
            residentId=id).all()
        list_result = contributionRelationships_schema.dump(er_collection)
        return utils.http_response(utils.HTTPStatus.OK, list_result)

    if request.method == "POST":
        payload = request.get_json()
        payload["residentId"] = id
        return create_new_item(ContributionRelationship, contribution_relationship_schema, payload)


@app.route('/residents/<string:id>/contribution-relationships/<string:cr_id>', methods=["GET", "PUT", "PATCH", "DELETE"])
def contribution_relationship_item(_, cr_id: str) -> utils.Response:
    if request.method == "GET":
        return get_item_by_id(ContributionRelationship, contribution_relationship_schema, er_id)
    if request.method in ["PUT", "PATCH"]:
        return update_item_by_id(
            ContributionRelationship,
            contribution_relationship_schema,
            cr_id
        )
    if request.method == ["DELETE"]:
        return delete_item_by_id(ContributionRelationship, cr_id)


@app.route('/db-reset', methods=['POST'])
def reset_db() -> utils.Response:
    """ Reset database """
    db.drop_all()
    db.create_all()

    return utils.http_response(utils.HTTPStatus.NO_CONTENT, None)


if __name__ == "__main__":
    db.create_all()
    app.run(debug=True, port=5000)
