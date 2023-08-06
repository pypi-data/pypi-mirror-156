from threading import Thread

import requests

from .utils import get_request_headers, process_endpoint, process_url
from .constants import DEFAULT_REQUEST_PROCESSOR_PORT, SUCCESS_RESPONSE, ERROR_RESPONSE, API_MAPPING_NOT_FOUND_RESPONSE
from .models import Processor, Setting

import web
import json

url_map = dict()
_settings = None

class __request_handler:

    def __process_request(self, endpoint):
        if not endpoint:
            return json.dumps(SUCCESS_RESPONSE)
        else:
            try:
                _endpoint = process_endpoint(endpoint)
                req_params = '&'.join([str(param[0]+'='+str(param[1])) for param in web.input().items()])
                service_name = url_map.get(_endpoint)
                if not service_name:
                    return None, None
                service_instances = _settings.__get_service_instances_by_name__(service_name=service_name)
                service_url = service_instances[0].__dict__.get('server_urls')
                final_url = service_url+_endpoint
                if req_params:
                    final_url = final_url + '?' + req_params
                final_url = process_url(final_url)
                headers = get_request_headers(web.ctx.env)
                return final_url, headers
            except Exception as e:
                print(f"Exception occurred while processing endpoint: {_endpoint}")
                print(e)
                return json.dumps(ERROR_RESPONSE)

    def GET(self, endpoint):
        try:
            final_url, headers = self.__process_request(endpoint=endpoint)
            if not final_url:
                return json.dumps(API_MAPPING_NOT_FOUND_RESPONSE)
            resp = requests.get(final_url, headers=headers)
            return resp.content
        except ConnectionError as e:
            print(f"Connection error occurred while making API call [{final_url}]")
        except Exception as e:
            print(f"Exception occurred for API call: [{final_url}]")
            print(e)
            return json.dumps(ERROR_RESPONSE)
        

    def POST(self, endpoint):
        try:
            final_url, headers = self.__process_request(endpoint=endpoint)
            resp = requests.post(final_url, data=json.loads(web.data()), headers=headers)
            return resp.content
        except ConnectionError as e:
            print(f"Connection error occurred while making API call [{final_url}]")
        except Exception as e:
            print(f"Exception occurred for API call: [{final_url}]")
            print(e)
            return json.dumps(ERROR_RESPONSE)

    def PATCH(self, endpoint):
        try:
            final_url, headers = self.__process_request(endpoint=endpoint)
            resp = requests.patch(final_url, data=json.loads(web.data()), headers=headers)
            return resp.content
        except ConnectionError as e:
            print(f"Connection error occurred while making API call [{final_url}]")
        except Exception as e:
            print(f"Exception occurred for API call: [{final_url}]")
            print(e)
            return json.dumps(ERROR_RESPONSE)
    
    def DELETE(self, endpoint):
        try:
            final_url, headers = self.__process_request(endpoint=endpoint)
            if not final_url:
                return json.dumps(API_MAPPING_NOT_FOUND_RESPONSE)
            resp = requests.delete(final_url, headers=headers)
            return resp.content
        except ConnectionError as e:
            print(f"Connection error occurred while making API call [{final_url}]")
        except Exception as e:
            print(f"Exception occurred for API call: [{final_url}]")
            print(e)
            return json.dumps(ERROR_RESPONSE)


class _RequestProcessor(Processor):
    """
    1. Map urls to server urls.
    2. pick an instance and forward your request there.
    3. if request fails due to server unreachable, give custom response, else forward the response from the service.
    """
    def __init__(self, request_processor_name: str, settings: Setting, *args, **kwargs) -> None:
        super().__init__(processor_name=request_processor_name, *args, **kwargs)
        self.settings = settings
        global _settings
        _settings = settings
        self.__get_url_mappings()

    def __process(self):
        """
        Steps:
        1. Get request
        2. Identify which service does the api belong to
        3. Get list of all instances of that service
        4. Sort the instances based on priority (if exists)
        5. Forward that request and return response
        """
        urls = (
            '/(.*)', '__request_handler'
        )
        try:
            app = web.application(urls, globals())        
            
            port = self.settings.meta_info.request_processor_port if self.settings.meta_info else DEFAULT_REQUEST_PROCESSOR_PORT
            print(f"Starting Request Processor at localhost:{port}")
            deamon = Thread(name='request_processor', target=web.httpserver.runsimple, args=(app.wsgifunc(), ("0.0.0.0", port)))
            deamon.setDaemon(True) # This will die when the main thread dies
            deamon.start()
            print(f"Request Processor daemon started. PID = {deamon.native_id}")
        except Exception as e:
            print("Error occurred while booting up Request Processor")
            print(e)

    def __get_url_mappings(self):
        global url_map
        url_map = {api: config.service_name for config in self.settings for api in config.get('apis')}
        
    def process(self):
        self.__process()