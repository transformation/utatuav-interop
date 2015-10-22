from auvsi_suas.views.clear_cache import ClearCache
from auvsi_suas.views.login import Login
from auvsi_suas.views.missions import Missions
from auvsi_suas.views.obstacles import Obstacles
from auvsi_suas.views.server_info import ServerInfo
from auvsi_suas.views.targets import Targets, TargetsId, TargetsIdImage
from auvsi_suas.views.teams import Teams, TeamsId
from auvsi_suas.views.telemetry import Telemetry
from auvsi_suas.views.auvsi_admin.evaluate_teams import EvaluateTeams
from auvsi_suas.views.auvsi_admin.export_kml import ExportKml
from auvsi_suas.views.auvsi_admin.index import Index
from auvsi_suas.views.auvsi_admin.live_kml import LiveKml, LiveKmlUpdate
from django.conf.urls import patterns, url
from django.conf import settings
from django.conf.urls.static import static


# yapf: disable
urlpatterns = patterns(
    '',
    # Team interoperability
    url(r'^api/login$', Login.as_view(), name='login'),
    url(r'^api/server_info$', ServerInfo.as_view(), name='server_info'),
    url(r'^api/obstacles$', Obstacles.as_view(), name='obstacles'),
    url(r'^api/telemetry$', Telemetry.as_view(), name='telemetry'),
    url(r'^api/targets$', Targets.as_view(), name='targets'),
    url(r'^api/targets/(?P<pk>\d+)$', TargetsId.as_view(), name='targets_id'),
    url(r'^api/targets/(?P<pk>\d+)/image$', TargetsIdImage.as_view(),
        name='targets_id_image'),
    # Admin API
    url(r'^api/missions$', Missions.as_view(), name='missions'),
    url(r'^api/teams$', Teams.as_view(), name='teams'),
    url(r'^api/teams/(?P<pk>\d+)$', TeamsId.as_view(), name='teams_id'),
    url(r'^api/clear_cache$', ClearCache.as_view(), name='clear_cache'),
    # Admin access views
    url(r'^$', Index.as_view(), name='index'),
    url(r'^auvsi_admin/evaluate_teams.csv$', EvaluateTeams.as_view(),
        name='evaluate_teams'),
    url(r'^auvsi_admin/export_data.kml$', ExportKml.as_view(),
        name='export_data'),
    url(r'^auvsi_admin/live.kml$', LiveKml.as_view(), name='live_kml'),
    url(r'^auvsi_admin/update.kml$', LiveKmlUpdate.as_view(),
        name='update_kml'),
) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
# yapf: enable
