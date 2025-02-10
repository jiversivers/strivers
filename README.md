from django.conf.global_settings import SESSION_ENGINEfrom django.conf.global_settings import SESSION_SERIALIZER

# Setting up Strivers in Django
## Setting up your environment
If you don't already have a Django project, get one setup. Django docs explains how to do this well. 
Once you have your project, run the following commands:
```shell
cd <project_directory> #if not already there
git clone --recurse-submodules https://www.github.com/jiversivers/strivers.git
pip install ./strava_swagger
pip install python-decouple
```
This will pull in the `strivers` repo and the `strava_swagger` submodule then install the `strava_swagger` package 
into your environment.  You will need to manually add the `.env` file to the `strivers` root to read configuration 
variables from.

## Adjusting your project settings
You will need to do some housekeeping in your Django project so it knows to include the Strivers app. In `setting.
py`, add `'strivers.apps.StriversConfig'` to the list of installed apps.  Add `'strivers.middleware.
EvalAccessToken'` to the list of middleware. To be safe, add this to the bottom of the list (as middleware is run in 
order). Finally, add the following lines into the file:
```python
SESSION_ENGINE = 'strivers.session.CustomSession'
SESSION_SERIALIZER = 'strivers.serializers.CustomSerializer'
```

Lastly, you will need to point the main project to the `strivers` URLs configs.
Simply add `path('strivers/', include('strivers.urls')` to the list of URLs in your project `urls.py`.

## Setting up databases
Now that `strivers` is installed, you'll need to prepare your databases for it. 
```sh
python manage.py migrate strivers
```