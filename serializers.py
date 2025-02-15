import json
import zlib
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.sessions.serializers import JSONSerializer
from django.db import models
from django.apps import apps


class CustomJSONEncoder(DjangoJSONEncoder):
    """Custom JSON Encoder that converts Django models into a serializable format."""
    def default(self, obj):
        print('defualt obj', obj)
        if isinstance(obj, models.Model):
            print('default as model', obj._meta.label)
            model_data = {}
            for field in obj._meta.fields:
                value = getattr(obj, field.name)
                if isinstance(field, models.ForeignKey):  # Store ForeignKey as ID
                    model_data[field.name] = value.pk if value else None
                else:
                    model_data[field.name] = value

            return {
                "__model__": obj._meta.label,  # e.g., 'myapp.MyModel'
                "data": model_data,
            }
        return super().default(obj)


class CustomJSONDecoder(json.JSONDecoder):
    """Custom JSON Decoder that reconstructs Django models from session data."""

    def __init__(self, *args, **kwargs):
        super().__init__(object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, obj):
        if "__model__" in obj:
            try:
                model_class = apps.get_model(obj["__model__"])  # Get model class
                model_data = obj["data"]

                # Convert ForeignKey IDs back to model instances
                for field in model_class._meta.fields:
                    if isinstance(field, models.ForeignKey) and field.name in model_data:
                        related_model = field.related_model
                        model_data[field.name] = related_model.objects.get(pk=model_data[field.name]) if model_data[
                            field.name] else None
                print('model class = ', model_class)
                return model_class(**model_data)  # Return model instance
            except LookupError:
                raise ValueError(f"Error reconstructing object: {obj['__model__']} not found.")
            except model_class.DoesNotExist:
                raise ValueError(f"ForeignKey reference not found for {obj['__model__']}.")
        return obj


class CustomSessionSerializer(JSONSerializer):
    """Custom session serializer that automatically handles Django models."""

    def dumps(self, obj):
        """Serialize session data using CustomJSONEncoder and return bytes."""
        serialized_str = json.dumps(obj, cls=CustomJSONEncoder)
        return serialized_str.encode("utf-8")  # Ensure it returns bytes

    def loads(self, data):
        """Deserialize session data using CustomJSONDecoder."""
        if isinstance(data, bytes):  # Ensure data is a string before decoding
            data = data.decode("utf-8")
        return json.loads(data, cls=CustomJSONDecoder)
