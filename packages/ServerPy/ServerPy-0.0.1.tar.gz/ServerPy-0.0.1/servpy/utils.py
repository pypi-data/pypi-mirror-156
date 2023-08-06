from datetime import datetime
import platform    # For getting the operating system name
import subprocess  # For executing a shell command
import uuid

from requests import head

def __get_dict__(obj):
    if isinstance(obj, datetime):
        # return dict(year=obj.year, month=obj.month, day=obj.day, hour=obj.hour, minute=obj.minute, second=obj.second)
        return str(obj)
    else:
        return obj.__dict__

get_unique_id = lambda : str(uuid.uuid4())

def ping(host):
    """
    Returns True if host (str) responds to a ping request.
    Remember that a host may not respond to a ping (ICMP) request even if the host name is valid.
    """

    # Option for the number of packets as a function of
    param = '-n' if platform.system().lower()=='windows' else '-c'

    # Building the command. Ex: "ping -c 1 google.com"
    command = ['ping', param, '1', host]

    return subprocess.call(command) == 0

def check_type(variable, expected_type, errors) -> None:
    if type(variable) is not expected_type:
        errors.append(f"{variable} is not of type {expected_type}")

def check_empty(variable, errors) -> None:
    if not variable:
        errors.append(f"Illegal values passed for {variable}")

def process_endpoint(endpoint: str) -> str:
    if not endpoint:
        return ""
    if endpoint.endswith('/'):
        endpoint = endpoint[:-1]
    if not endpoint.startswith('/'):
        endpoint = '/'+endpoint
    return endpoint

def process_url(url: str) -> str:
    if not url:
        return ""
    if not url.startswith('https'):
        return "https://"+url

def adapt_header(txt: str) -> str:
  """Input: string, header name as it is in web.ctx.env
  Output: string, header name according to http protocol.
  es: "HTTP_CACHE_CONTROL" => "Cache-Control"
  """
  txt = txt.replace('HTTP_', '')
  return '-'.join((t[0] + t[1:].lower() for t in txt.split('_')))

def get_request_headers(env: dict) -> dict:
    headers = dict()
    for k, v in env.items():
            if k.startswith('HTTP') or k in ('CONTENT_TYPE', 'CONTENT_LENGTH'):
                headers[adapt_header(k)] = str(v)
    return headers