from typing import List
from datetime import date


class Person():

    def __init__(self,
                 person_id: str = None,
                 first_name: str = None,
                 last_name: str = None,
                 address: str = None,
                 phone_number: List[str] = None):

        self.id = person_id
        self.first_name = first_name
        self.last_name = last_name
        self.address = address
        self.phone_number = phone_number


class Contributor(Person):

    def __init__(self,
                 person_id: str = None,
                 first_name: str = None,
                 last_name: str = None,
                 address: str = None,
                 phone_number: List[str] = None,
                 role: str = None):

        super().__init__(
            person_id,
            first_name,
            last_name,
            address,
            phone_number)

        self.role = role


class EmergencyContact(Person):

    def __init__(self,
                 person_id: str = None,
                 first_name: str = None,
                 last_name: str = None,
                 address: str = None,
                 phone_number: List[str] = None,
                 relationship: str = None):

        super().__init__(
            person_id,
            first_name,
            last_name,
            address,
            phone_number)

        self.relationship = relationship


class HealthMutual():

    def __init__(self,
                 health_mutual_id: str = None,
                 name: str = None,
                 address: str = None,
                 phone_number: List[str] = None):

        self.name = name
        self.address = address
        self.phone_number = phone_number


class Resident(Person):

    def __init__(self,
                 person_id: str = None,
                 first_name: str = None,
                 last_name: str = None,
                 address: str = None,
                 phone_number: list = None,
                 birth_date: date = None,
                 birthplace: str = None,
                 entrance_date: date = None,
                 emergency_bag: str = None,
                 social_welfare_id: str = None,
                 health_mutual: HealthMutual = None,
                 referring_doctor: Person = None,
                 psychiatrist: Person = None,
                 social_advisers: List[Contributor] = None,
                 contributors: List[Contributor] = None,
                 emergency_contacts: List[EmergencyContact] = None):

        super().__init__(
            person_id,
            first_name,
            last_name,
            address,
            phone_number)

        self.birth_date = birth_date
        self.birthplace = birthplace
        self.entrance_date = entrance_date
        self.emergency_bag = emergency_bag
        self.social_welfare_id = social_welfare_id
        self.health_mutual = health_mutual
        self.referring_doctor = referring_doctor
        self.psychiatrist = psychiatrist
        self.social_advisers = social_advisers
        self.contributors = contributors
        self.emergency_contacts = emergency_contacts