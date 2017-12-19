from django.conf import settings
from django.db.models.fields.files import ImageFieldFile, ImageField
from rest_framework import serializers
from rest_framework.reverse import reverse

__all__ = (
    'ParameterisedHyperlinkedIdentityField',
)


class DefaultStaticImageFieldFile(ImageFieldFile):
    @property
    def url(self):
        try:
            self._require_file()
            return super().url
        # ImageFieldFile에 파일이 존재하지 않을 경우, DefaultStaticImageField에서 인자로 받은
        # static_image_path를 name으로 가지는 staticfilestorage url을 돌려준다
        except ValueError:
            from django.contrib.staticfiles.storage import staticfiles_storage
            return staticfiles_storage.url(self.field.static_image_path)


class DefaultStaticImageField(ImageField):
    attr_class = DefaultStaticImageFieldFile

    def __init__(self, *args, **kwargs):
        self.static_image_path = kwargs.pop(
            'default_image_path',
            getattr(settings, 'DEFAULT_IMAGE_PATH', 'images/default_image.png'))
        super().__init__(*args, **kwargs)


class ParameterisedHyperlinkedIdentityField(serializers.HyperlinkedIdentityField):
    """
    Represents the instance, or a property on the instance, using hyperlinking.

    lookup_fields is a tuple of tuples of the form:
        ('model_field', 'url_parameter')
    """
    lookup_fields = (('pk', 'pk'),)

    def __init__(self, *args, **kwargs):
        self.lookup_fields = kwargs.pop('lookup_fields', self.lookup_fields)
        super().__init__(*args, **kwargs)

    def get_url(self, obj, view_name, request, format):
        """
        Given an object, return the URL that hyperlinks to the object.

        May raise a `NoReverseMatch` if the `view_name` and `lookup_field`
        attributes are not configured to correctly match the URL conf.
        """
        kwargs = {}
        for model_field, url_param in self.lookup_fields:
            attr = obj
            for field in model_field.split('.'):
                attr = getattr(attr, field)
            kwargs[url_param] = attr

        return reverse(view_name, kwargs=kwargs, request=request, format=format)
