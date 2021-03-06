import base64
import magic
import mimetypes
import uuid

from django.core.files.base import ContentFile
from rest_framework import serializers
from rest_framework.fields import SkipField


class MimeContentFile(ContentFile):
    def __init__(self, content, name=None, mime_type=None):
        super(MimeContentFile, self).__init__(content, name)
        self.mime_type = mime_type

class Base64FieldMixin(object):

    def __init__(self, guess_type=False, default_type=None, mime_types=mimetypes.MimeTypes(), *args, **kwargs):
        self.guess_type = guess_type
        self.default_type = default_type
        self.mime_types = mime_types

        super().__init__(*args, **kwargs)

    def _decode(self, data):
        if isinstance(data, str):
            if data.startswith('data:'):
                # base64 encoded file - decode
                mime_type, datastr = data[5:].split(';base64,')
                data = base64.b64decode(datastr)

                if self.guess_type:
                    mime_type = magic.from_buffer(data, mime=True)

                    if not data and self.default_type:
                        mime_type = self.default_type

                data = MimeContentFile(
                    data,
                    name='{}{}'.format(uuid.uuid4(), self.mime_types.guess_extension(mime_type) or '.bin'),
                    mime_type=mime_type
                )
            elif data.startswith('http'):
                raise SkipField()

        return data

# TODO: default value?
    def to_internal_value(self, data):
        data = self._decode(data)
        return super(Base64FieldMixin, self).to_internal_value(data)


class Base64ImageField(Base64FieldMixin, serializers.ImageField):
    pass


class Base64FileField(Base64FieldMixin, serializers.FileField):
    pass
