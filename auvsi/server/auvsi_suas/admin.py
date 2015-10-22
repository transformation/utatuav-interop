from django.contrib import admin
from auvsi_suas.models import AerialPosition
from auvsi_suas.models import FlyZone
from auvsi_suas.models import GpsPosition
from auvsi_suas.models import MissionConfig
from auvsi_suas.models import MovingObstacle
from auvsi_suas.models import ObstacleAccessLog
from auvsi_suas.models import ServerInfo
from auvsi_suas.models import ServerInfoAccessLog
from auvsi_suas.models import StationaryObstacle
from auvsi_suas.models import TakeoffOrLandingEvent
from auvsi_suas.models import Target
from auvsi_suas.models import UasTelemetry
from auvsi_suas.models import Waypoint


# Define model admin which has better defaults for large amounts of data.
class LargeDataModelAdmin(admin.ModelAdmin):
    show_full_result_count = False

# Register models for admin page
admin.site.register(AerialPosition, LargeDataModelAdmin)
admin.site.register(FlyZone)
admin.site.register(GpsPosition, LargeDataModelAdmin)
admin.site.register(MissionConfig)
admin.site.register(MovingObstacle)
admin.site.register(ObstacleAccessLog, LargeDataModelAdmin)
admin.site.register(ServerInfo)
admin.site.register(ServerInfoAccessLog, LargeDataModelAdmin)
admin.site.register(StationaryObstacle)
admin.site.register(UasTelemetry, LargeDataModelAdmin)
admin.site.register(TakeoffOrLandingEvent)
admin.site.register(Target)
admin.site.register(Waypoint)
