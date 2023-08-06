SERVPY_LOGO = """                      
  ___  ___ _ ____   ___ __  _   _ 
 / __|/ _ \ '__\ \ / / '_ \| | | |
 \__ \  __/ |   \ V /| |_) | |_| |
 |___/\___|_|    \_/ | .__/ \__, |
                     |_|    |___/ 
"""


DEFAULT_DISCOVERY_SERVER_NAME = "Discovery Server"
DEFAULT_REQUEST_PROCESSOR_NAME = "Request Processor"


POLLING_PING = 'ping'
POLLING_HEALTH = 'health'

ACTIVE_STATUS = 'active'
INACTIVE_STATUS = 'inactive'
SERVER_ERROR_STATUS = 'discovery server error'
SERVER_UNREACHABLE_STATUS = 'service unreachable'

POLLING_METHOD_CHOICES = (
    'ping', 'health'
)

STATS_PACKET_LIMIT = 5000
DEFAULT_DISCOVERY_SERVER_PORT = 8008
DEFAULT_REQUEST_PROCESSOR_PORT = 8001
DEFAULT_POLLING_FREQUENCY = 60

DEFAULT_META_INFO = {
  "discovery_server_name":DEFAULT_DISCOVERY_SERVER_NAME,
  "request_processor_name":DEFAULT_REQUEST_PROCESSOR_NAME,
  "discovery_server_port":DEFAULT_DISCOVERY_SERVER_PORT,
  "request_processor_port":DEFAULT_REQUEST_PROCESSOR_PORT
}

ERROR_RESPONSE = {"status": "An error occurred while processing your request"}
SUCCESS_RESPONSE = {"status": "Success"}
API_MAPPING_NOT_FOUND_RESPONSE = {"status": "No API found with provided endpoint"}
