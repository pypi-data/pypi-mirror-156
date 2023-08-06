from .constants import DEFAULT_POLLING_FREQUENCY, STATS_PACKET_LIMIT
from .models import Configuration


class _ServiceInstanceConfiguration(Configuration):
    def __init__(self, *args, **kwargs):
        config = {
            "service_name": kwargs.get('service_name'),
            "server_urls": kwargs.get('server_url'),
            "poll_method": kwargs.get('method'),
            "poll_endpoint": kwargs.get('endpoint') if kwargs.get('endpoint') else None,
            "poll_retries": kwargs.get('retries') if kwargs.get('retries') else 0,
            "retry_delay": kwargs.get('retry_delay') if kwargs.get('retry_delay') else None,
            "poll_frequency": kwargs.get('frequency') if kwargs.get('frequency') else DEFAULT_POLLING_FREQUENCY,
            "packet_limit": kwargs.get('packet_limit') if kwargs.get('packet_limit') else STATS_PACKET_LIMIT,
            "apis": kwargs.get('apis'),
            "priority": kwargs.get('priority') if kwargs.get('priority') else ""
        }
        super().__init__(**config)
