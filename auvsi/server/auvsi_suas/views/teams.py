"""Teams view."""
import json
from auvsi_suas.models import UasTelemetry
from auvsi_suas.models import TakeoffOrLandingEvent
from auvsi_suas.views import logger
from auvsi_suas.views.decorators import require_superuser
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.utils.decorators import method_decorator
from django.views.generic import View


def user_json(user):
    """Generate JSON-style dict for user."""
    return {
        'name': user.username,
        'id': user.pk,
        'in_air': TakeoffOrLandingEvent.user_in_air(user),
        'active': UasTelemetry.user_active(user),
    }


class Teams(View):
    """Gets a list of all teams."""

    @method_decorator(require_superuser)
    def dispatch(self, *args, **kwargs):
        return super(Teams, self).dispatch(*args, **kwargs)

    def get(self, request):
        users = User.objects.all()
        teams = []

        for user in users:
            # Only standard users are exported
            if not user.is_superuser:
                teams.append(user_json(user))

        return HttpResponse(json.dumps(teams), content_type="application/json")


class TeamsId(View):
    """GET/PUT specific team."""

    @method_decorator(require_superuser)
    def dispatch(self, *args, **kwargs):
        return super(TeamsId, self).dispatch(*args, **kwargs)

    def get(self, request, pk):
        try:
            user = User.objects.get(pk=int(pk))
        except User.DoesNotExist:
            return HttpResponseBadRequest('Unknown team %s' % pk)

        return HttpResponse(json.dumps(user_json(user)),
                            content_type="application/json")

    def put(self, request, pk):
        """PUT allows updating in-air status."""
        try:
            user = User.objects.get(pk=int(pk))
        except User.DoesNotExist:
            return HttpResponseBadRequest('Unknown team %s' % pk)

        try:
            data = json.loads(request.body)
        except ValueError:
            return HttpResponseBadRequest('Invalid JSON: %s' % request.body)

        # We ignore everything except 'in_air'
        if 'in_air' in data:
            in_air = data['in_air']

            if in_air is not True and in_air is not False:
                return HttpResponseBadRequest('in_air must be boolean')

            currently_in_air = TakeoffOrLandingEvent.user_in_air(user)

            # New event only necessary if changing status
            if currently_in_air != in_air:
                event = TakeoffOrLandingEvent(user=user, uas_in_air=in_air)
                event.save()

        return HttpResponse(json.dumps(user_json(user)),
                            content_type="application/json")
