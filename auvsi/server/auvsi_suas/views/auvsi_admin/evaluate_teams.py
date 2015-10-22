"""Admin automatic evaluation of teams view."""

import copy
import cStringIO
import csv
from auvsi_suas.models import MissionConfig
from auvsi_suas.views import logger
from auvsi_suas.views.decorators import require_superuser
from auvsi_suas.views.missions import mission_for_request
from django.http import HttpResponse
from django.http import HttpResponseServerError
from django.utils.decorators import method_decorator
from django.views.generic import View


class EvaluateTeams(View):
    """Evaluates the teams by forming a CSV containing useful stats."""

    @method_decorator(require_superuser)
    def dispatch(self, *args, **kwargs):
        return super(EvaluateTeams, self).dispatch(*args, **kwargs)

    def get(self, request):
        logger.info('Admin downloaded team evaluation.')

        # Get the mission to evaluate a team for.
        mission, error = mission_for_request(request.GET)
        if error:
            logger.warning('Could not get mission to evaluate teams.')
            return error

        # Get the eval data for the teams
        user_eval_data = mission.evaluate_teams()
        if not user_eval_data:
            logger.warning('No data for team evaluation.')
            return HttpResponseServerError(
                'Could not get user evaluation data.')

        # Reformat to column oriented
        user_col_data = {}
        for (user, eval_data) in user_eval_data.iteritems():
            col_data = user_col_data.setdefault(user, {})
            col_data['username'] = user.username
            work_queue = [([], eval_data)]
            while len(work_queue) > 0:
                (cur_prefixes, cur_map) = work_queue.pop()
                for (key, val) in cur_map.iteritems():
                    new_prefixes = copy.copy(cur_prefixes)
                    new_prefixes.append(str(key))
                    if isinstance(val, dict):
                        work_queue.append((new_prefixes, val))
                    else:
                        column_key = '.'.join(new_prefixes)
                        col_data[column_key] = val
        # Get column headers
        col_headers = set()
        for col_data in user_col_data.values():
            for header in col_data.keys():
                col_headers.add(header)
        col_headers = sorted(col_headers)

        # Write output
        csv_output = cStringIO.StringIO()
        writer = csv.DictWriter(csv_output, fieldnames=col_headers)
        writer.writeheader()
        for col_data in user_col_data.values():
            writer.writerow(col_data)
        output = csv_output.getvalue()
        csv_output.close()
        return HttpResponse(output)
