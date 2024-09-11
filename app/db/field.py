from sqlmodel import Field


class PersonalDataField(Field):
    is_sensitive_data = True
