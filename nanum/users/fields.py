from django.db import models


class EmailNullField(models.EmailField):
    """
    Subclass of the EmailField that allows empty strings to be stored as NULL.
    """

    description = "EmailField that stores NULL but returns ''."

    def from_db_value(self, value, expression, connection, contex):
        """
        Gets value right out of the db and changes it if its ``None``.
        """
        if value is None:
            return ''
        else:
            return value

    def get_prep_value(self, value):
        """
        Catches value right before sending to db.
        """
        if value == '':
            # If Django tries to save an empty string, send the db None (NULL).
            return None
        else:
            # Otherwise, just pass the value.
            return value


class CharNullField(models.CharField):
    """
    Subclass of the CharField that allows empty strings to be stored as NULL.
    """

    description = "CharField that stores NULL but returns ''."

    def from_db_value(self, value, expression, connection, contex):
        """
        Gets value right out of the db and changes it if its ``None``.
        """
        if value is None:
            return ''
        else:
            return value

    def get_prep_value(self, value):
        """
        Catches value right before sending to db.
        """
        if value == '':
            # If Django tries to save an empty string, send the db None (NULL).
            return None
        else:
            # Otherwise, just pass the value.
            return value
