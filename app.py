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

# class Author(ModelMixin, db.Model):  # type: ignore
#     id = db.Column(db.Integer, primary_key=True)
#     first = db.Column(db.String(80))
#     last = db.Column(db.String(80))


# class Quote(ModelMixin, db.Model):  # type: ignore
#     id = db.Column(db.Integer, primary_key=True)
#     content = db.Column(db.String, nullable=False)
#     author_id = db.Column(db.Integer, db.ForeignKey("author.id"))
#     author = db.relationship(
#         "Author", backref=db.backref("quotes", lazy="dynamic"))
#     posted_at = db.Column(db.DateTime)


##### SCHEMAS #####
def must_not_be_blank(data):
    if not data:
        raise ValidationError("Data not provided.")


class PersonSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Person

    @post_load
    def make_person(self, data, **kwargs):
        return Person(**data)


# class CitySchema(ma.SQLAlchemyAutoSchema):
#     id = fields.Int(dump_only=True)
#     name = fields.Str(required=True, validate=must_not_be_blank)
#     postal_code = fields.Str()


# class ContributorSchema(ma.SQLAlchemyAutoSchema):
#     id = fields.Int(dump_only=True)
#     role = fields.Str()


# class HealthMutualSchema(ma.SQLAlchemyAutoSchema):
#     id = fields.Int(dump_only=True)
#     name = fields.Str(required=True, validate=must_not_be_blank)
#     address = fields.Str()
#     main_phone_number = fields.Str()
#     alternative_phone_number = fields.Str()


# class ResidentSchema(ma.SQLAlchemyAutoSchema):
#     id = fields.Nested(PersonSchema, validate=must_not_be_blank)
#     birth_date = fields.Date()
#     birthplace = fields.Str()
#     entrance_date = fields.Date()
#     emergency_bag = fields.Str()
#     social_welfare_number = fields.Str()
#     city_id = fields.Nested(CitySchema)
#     health_mutual_id = fields.Nested(HealthMutualSchema)
#     referring_doctor_id = fields.Nested(PersonSchema)
#     psychiatrist_id = fields.Nested(PersonSchema)


# class EmergencyRelationshipSchema(ma.SQLAlchemyAutoSchema):
#     id = fields.Int(dump_only=True)

#     resident_id = fields.Nested(ResidentSchema)
#     person_id = fields.Nested(PersonSchema)
#     relationship = db.Column(db.String, primary_key=True)


# class ContributionRelationshipSchema(ma.SQLAlchemyAutoSchema):
#     id = db.Column(db.String, primary_key=True)

#     resident_id = fields.Nested(ResidentSchema)
#     contributor_id = fields.Nested(ContributorSchema)
#     social_advising = fields.Bool()
# Custom validator


# class QuoteSchema(ma.SQLAlchemyAutoSchema):
#     id = fields.Int(dump_only=True)
#     author = fields.Nested(AuthorSchema, validate=must_not_be_blank)
#     content = fields.Str(required=True, validate=must_not_be_blank)
#     posted_at = fields.DateTime(dump_only=True)
#     # Allow client to pass author's full name in request body
#     # e.g. {"author': 'Tim Peters"} rather than {"first": "Tim", "last": "Peters"}
#     @pre_load
#     def process_author(self, data, **kwargs):
#         author_name = data.get("author")
#         if author_name:
#             first, last = author_name.split(" ")
#             author_dict = dict(first=first, last=last)
#         else:
#             author_dict = {}
#         data["author"] = author_dict
#         return data
person_schema = PersonSchema()
persons_schema = PersonSchema(many=True)
# resident_schema = ResidentSchema()
# residents_schema = ResidentSchema(many=True)

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

# @app.route("/quotes/", methods=["GET"])
# def get_quotes():
#     quotes = Quote.query.all()
#     result = quotes_schema.dump(quotes, many=True)
#     return {"quotes": result}


# @app.route("/quotes/<int:pk>")
# def get_quote(pk):
#     try:
#         quote = Quote.query.get(pk)
#     except IntegrityError:
#         return {"message": "Quote could not be found."}, 400
#     result = quote_schema.dump(quote)
#     return {"quote": result}


# @app.route("/quotes/", methods=["POST"])
# def new_quote():
#     json_data = request.get_json()
#     if not json_data:
#         return {"message": "No input data provided"}, 400
#     # Validate and deserialize input
#     try:
#         data = quote_schema.load(json_data)
#     except ValidationError as err:
#         return err.messages, 422
#     first, last = data["author"]["first"], data["author"]["last"]
#     author = Author.query.filter_by(first=first, last=last).first()
#     if author is None:
#         # Create a new author
#         author = Author(first=first, last=last)
#         db.session.add(author)
#     # Create new quote
#     quote = Quote(
#         content=data["content"], author=author, posted_at=datetime.datetime.utcnow()
#     )
#     db.session.add(quote)
#     db.session.commit()
#     result = quote_schema.dump(Quote.query.get(quote.id))
#     return {"message": "Created new quote.", "quote": result}


@app.route('/db-reset', methods=['POST'])
def reset_db() -> utils.Response:
    db.drop_all()
    db.create_all()

    return utils.http_response(utils.HTTPStatus.NO_CONTENT, None)


if __name__ == "__main__":
    db.create_all()
    app.run(debug=True, port=5000)
