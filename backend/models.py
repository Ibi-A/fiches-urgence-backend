from backend import db
from backend.exceptions import InvalidRequestException

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
            raise InvalidRequestException("Forbidden to update id............")

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

