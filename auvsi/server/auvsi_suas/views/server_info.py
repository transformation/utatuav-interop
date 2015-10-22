"""Interoperability server info view."""

import datetime
import json
from auvsi_suas.models import ServerInfo
from auvsi_suas.models import ServerInfoAccessLog
from auvsi_suas.views import logger
from auvsi_suas.views.decorators import require_login
from auvsi_suas.views.missions import active_mission
from django.core.cache import cache
from django.http import HttpResponseServerError
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.generic import View


class ServerInfo(View):
    """Gets the server information as JSON with a GET request."""

    @method_decorator(require_login)
    def dispatch(self, *args, **kwargs):
        return super(ServerInfo, self).dispatch(*args, **kwargs)

    def get(self, request):
        # Log user access to server information.
        logger.info('User downloaded server info: %s.' % request.user.username)
        ServerInfoAccessLog(user=request.user).save()

        # Form response.
        try:
            # Get the server info stored in the active mission.
            server_info_key = '/ServerInfo/latest'
            info = cache.get(server_info_key)
            if info is None:
                (mission, err) = active_mission()
                if err:
                    return err
                info = mission.server_info
                if not info:
                    return HttpResponseServerError(
                        'No server info for mission.')
                cache.set(server_info_key, info)
        except ServerInfo.DoesNotExist:
            # Failed to obtain server info.
            return HttpResponseServerError('No server info available.')

        # Form JSON response.
        data = info.json()
        data['server_time'] = datetime.datetime.now().isoformat()
        return JsonResponse(data)
