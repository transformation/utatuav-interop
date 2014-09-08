import datetime
import json
import time
from auvsi_suas.models import ServerInfo
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.http import HttpResponseServerError
from django.shortcuts import render


def index(request):
    """Main view for users connecting via web browsers.

    This view downloads and displays a JS view. This view first logs in the
    user. If the user is a superuser, it shows the Judging view which is used
    to manage the competition and evaluate teams.
    """
    return render(request, 'auvsi_suas/index.html') 


def loginUser(request):
    """Logs the user in with a POST request using the given parameters.

    This view performs the login process for the user. The POST paramters must
    include 'username' and 'password'. Users can programatically send a login
    request to this view which will return a cookie containing the session ID.
    Users then send this cookie with each request to make requests as an
    authenticated user.
    """
    try:
        # Obtain username and password from POST parameters
        username = request.POST['username']
        password = request.POST['password']
    except KeyError:
        # Failed to get POST parameters, invalid request
        return HttpResponseBadRequest('Login must be POST request with ' 
                '"username" and "password" parameters.')
    else:
        # Use credentials to authenticate
        user = authenticate(username=username, password=password)
        if user is not None and user.is_active:
            # Successful authentication with active user, login
            login(request, user)
            return HttpResponse('Login Successful.')
        else:
            # Invalid user credentials, invalid request
            return HttpResponseBadRequest('Invalid Credentials.')


def getServerInfo(request):
    """Gets the server information with a GET request."""
    # Validate user is logged in to make request
    if not request.user.is_authenticated():
        return HttpResponseBadRequest('User not logged in. Login required.')
    # Validate user made a GET request
    if request.method != 'GET':
        return HttpResponseBadRequest('Server info request must be GET request.')

    try:
        # Get the latest published server info
        server_info = ServerInfo.objects.latest('timestamp') 
    except ServerInfo.DoesNotExist:
        # Failed to obtain server info 
        return HttpResponseServerError('No server information available.')
    else:
        # Form JSON response
        data = dict()
        data['server_time'] = str(datetime.datetime.now()) 
        data['message'] = server_info.team_msg
        data['message_timestamp'] = str(server_info.timestamp)
        return HttpResponse(json.dumps(data),
                            content_type="application/json")


def getObstacles(request):
    """Gets the obstacle information with a GET request."""
    # Validate user is logged in to make request
    if not request.user.is_authenticated():
        return HttpResponseBadRequest('User not logged in. Login required.')

    # TODO


def updateUasPosition(request):
    """Posts the UAS position with a POST request containing JSON data."""
    # Validate user is logged in to make request
    if not request.user.is_authenticated():
        return HttpResponseBadRequest('User not logged in. Login required.')

    # TODO


# login_required()
# @user_passes_test(lambda u: u.is_superuser)