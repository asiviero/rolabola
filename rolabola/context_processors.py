from django.conf import settings # import the settings file

def maps_api_key(request):
    # return the value you want as a dictionnary. you may add multiple values in there.
    return {'GOOGLE_MAPS_V3_APIKEY': settings.GOOGLE_MAPS_V3_APIKEY}
