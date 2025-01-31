import uuid

from django.contrib import admin
from django.db import models

# Model to store athlete data for API access and global Strava athlete info
class Athlete(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False) # Random int to hide actual athlete ID
    athlete_id = models.BigIntegerField(unique=True) # Strava number
    username = models.CharField(max_length=120) # Strava name
    first_name = models.CharField(max_length=120)
    last_name = models.CharField(max_length=120)
    access_token = models.CharField(max_length=64, unique=True) # access token
    refresh_token = models.CharField(max_length=64, unique=True) # refresh token
    expires_at = models.DateTimeField('expiration date') # token expiry
    scope = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    def to_dict(self):
        return {
            'id': str(self.id),  # UUID needs to be converted to a string
            'athlete_id': self.athlete_id,
            'username': self.username,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'access_token': self.access_token,
            'refresh_token': self.refresh_token,
            'expires_at': self.expires_at.timestamp(),  # Store as UNIX timestamp
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=uuid.UUID(data['id']),
            athlete_id=data['athlete_id'],
            username=data['username'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            access_token=data['access_token'],
            refresh_token=data['refresh_token'],
            expires_at=models.DateTimeField().to_python(data['expires_at']),
        )

# Model to store activities overview list (averages, names, etc.)
class ActivityOverview(models.Model):
    athlete_id = models.ForeignKey(Athlete, on_delete=models.CASCADE) # Points to which athlete this activity is from
    activity_id = models.IntegerField(primary_key=True) # Unique ID for the activity
    activity_date = models.DateTimeField('activity date')   # Date activity started
    activity_name = models.CharField(max_length=120)    # User-given name of activity
    average_hr = models.FloatField(null=True)

    # TODO: Add db trigger to update below fields when fine-grained activity data is added to ActivitiesData Model
    start_lat = models.FloatField(null=True)
    start_lon = models.FloatField(null=True)


    @admin.display(ordering='date')
    def __str__(self):
        return self.activity_name

class ActivityData(models.Model):
    activity_id = models.ForeignKey(ActivityOverview, on_delete=models.CASCADE)
    timestamp = models.DateTimeField('activity timestamp')
    lat = models.FloatField('latitude')
    lon = models.FloatField('longitude')
    heart_rate = models.FloatField('heart rate')
    distance = models.FloatField('distance')
    elevation = models.FloatField('elevation')

