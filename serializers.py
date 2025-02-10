import json
from django.contrib.sessions.serializers import JSONSerializer

from strivers.models import Athlete


class CustomModelSerializer(JSONSerializer):
    def dumps(self, obj):
        print('serial: ', obj)
        """Convert the object into a JSON string."""
        if isinstance(obj, dict) and 'athlete' in obj and isinstance(obj['athlete'], Athlete):
            obj['athlete'] = obj['athlete'].to_dict()
        return super().dumps(obj)

    def loads(self, data):
        """Handles deserialization, reconstructing Athlete objects from stored session data."""
        print('deserial: ', obj)
        obj = super().loads(data)
        if isinstance(obj, dict) and 'athlete' in obj and isinstance(obj['athlete'], dict):
            obj['athlete'] = Athlete.from_dict(obj['athlete'])
        return obj

