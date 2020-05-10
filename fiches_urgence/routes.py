from flask import request, Response
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError
from marshmallow import ValidationError
from src import utils
from flask import current_app as app
from fiches_urgence import db, ma
from fiches_urgence.exceptions import InvalidRequestException
from fiches_urgence.models import (
    Resident,
    Person,
    EmergencyRelationship,
    ContributionRelationship,
    City,
    Contributor,
    HealthMutual
)
from fiches_urgence.schemas import (
    resident_schema, residents_schema,
    person_schema, persons_schema,
    city_schema, cities_schema,
    contributor_schema, contributors_schema,
    emergency_relationship_schema, emergencyRelationships_schema,
    contribution_relationship_schema, contribution_relationships_schema,
    health_mutual_schema, health_mutuals_schema
)
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
    payload: dict = None,
    new_id: bool = True
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

        if not payload.get("id") or new_id:
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
        return delete_item_by_id(Person, id)


@app.route("/residents", methods=["GET", "POST"])
def resident_collection() -> utils.Response:
    if request.method == "GET":
        return get_collection(Resident, residents_schema)
    if request.method == "POST":
        try:
            return create_new_item(Resident, resident_schema, None, False)
        except IntegrityError as err:
            return "id attribute should be an existing person id", 400


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
    if request.method == "DELETE":
        return delete_item_by_id(City, id)


@app.route("/contributors", methods=["GET", "POST"])
def contributor_collection() -> utils.Response:
    if request.method == "GET":
        return get_collection(Contributor, contributors_schema)
    if request.method == "POST":
        try:
            return create_new_item(Contributor, contributor_schema, None, False)
        except IntegrityError as err:
            return "id attribute should be an existing person id", 400


@app.route("/contributors/<string:id>", methods=["GET", "PUT", "PATCH", "DELETE"])
def contributor_item(id: str) -> utils.Response:
    if request.method == "GET":
        return get_item_by_id(Contributor, contributor_schema, id)
    if request.method in ["PUT", "PATCH"]:
        return update_item_by_id(Contributor, contributor_schema, id)
    if request.method == "DELETE":
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
    if request.method == "DELETE":
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
    if request.method == "DELETE":
        return delete_item_by_id(EmergencyRelationship, er_id)


@app.route('/residents/<string:id>/contribution-relationships', methods=["GET", "POST"])
def contributionRelationships_collection(id: str) -> utils.Response:
    if request.method == "GET":
        er_collection = ContributionRelationship.query.filter_by(
            residentId=id).all()
        list_result = contribution_relationships_schema.dump(er_collection)
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
    if request.method == "DELETE":
        return delete_item_by_id(ContributionRelationship, cr_id)


@app.route('/db-reset', methods=['POST'])
def reset_db() -> utils.Response:
    """ Reset database """
    db.drop_all()
    db.create_all()

    return utils.http_response(utils.HTTPStatus.NO_CONTENT, None)
