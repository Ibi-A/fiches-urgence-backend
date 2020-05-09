from marshmallow import Schema, fields, ValidationError, post_load
from backend import ma
from backend.models import (
    Resident,
    Person,
    EmergencyRelationship,
    ContributionRelationship,
    City,
    Contributor,
    HealthMutual
)


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
    healthMutual = fields.Nested(HealthMutualSchema)
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
contribution_relationships_schema = ContributionRelationshipSchema(many=True)
