"""Server information model."""

from django.db import models


class ServerInfo(models.Model):
    """Static information stored on the server that teams must retrieve."""
    # Time information was stored
    timestamp = models.DateTimeField(auto_now_add=True)
    # Message for teams
    team_msg = models.CharField(max_length=100)

    def __unicode__(self):
        """Descriptive text for use in displays."""
        return unicode("ServerInfo (pk:%s, msg:%s, timestamp:%s)" %
                       (str(self.pk), str(self.team_msg), str(self.timestamp)))

    def json(self):
        """Obtain a JSON style representation of object."""
        data = {
            'message': self.team_msg,
            'message_timestamp': self.timestamp.isoformat()
        }
        return data
