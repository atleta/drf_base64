import base64
import mimetypes
import uuid

from django.core.files.base import ContentFile
from rest_framework import serializers
from rest_framework.fields import SkipField


class Base64FieldMixin(object):

    def _decode(self, data):
        if isinstance(data, str):
            if data.startswith('data:'):
                # base64 encoded file - decode
                mime_type, datastr = data[5:].split(';base64,')

                data = ContentFile(
                    base64.b64decode(datastr),
                    name='{}{}'.format(uuid.uuid4(), mimetypes.guess_extension(mime_type) or '.bin')
                )
            elif data.startswith('http'):
                raise SkipField()
            
        return data

    def to_internal_value(self, data):
        data = self._decode(data)
        return super(Base64FieldMixin, self).to_internal_value(data)


class Base64ImageField(Base64FieldMixin, serializers.ImageField):
    pass


class Base64FileField(Base64FieldMixin, serializers.FileField):
    pass
