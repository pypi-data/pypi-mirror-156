import json
from threading import Thread

from .constants import SUCCESS_RESPONSE, ERROR_RESPONSE, DEFAULT_DISCOVERY_SERVER_PORT

from .watchdog import WatchDog
from .models import Server, ServiceStatistics, Statistics

import web

statistics = None

class __health:
    def GET(self):
        return json.dumps({"status": "Discovery Server running"})

class __stats:
    def GET(self):
        global statistics
        web.header('Content-Type', 'application/json')
        return statistics

class __dump:
    def GET(self):
        print("Dumping statistics to current file")
        global statistics
        web.header('Content-Type', 'application/json')
        try:
            with open('file.dump', 'w') as file:
                json.dump(statistics, file)
            return SUCCESS_RESPONSE
        except:
            return ERROR_RESPONSE

class _DiscoveryServer(Server):
    '''
    ----------------
    Discovery Server
    ----------------
    Class which will be responsible for collecting info about the services as
    provided in the input json/yaml. This server will use the polling methods to keep a track of the 
    runtime of the services.

    Functions:
    ----------
    1. Poll each and every service at specified time interval. (If no interval is specified, then default is 10 mins)
    2. Expose endpoints to query stats for each service.
    3. Expose endpoints to manage the properties of discovery server.
    '''
    def __init__(self, server_name: str, *args, **kwargs) -> None:
        super().__init__(server_name = server_name, *args, **kwargs)

    def __initialize_components(self):
        """
        Initialize the following things:
        1. For each Configuration, create a watchdog thread
        2. For each Configuration, create a ServerStatistics object and assign it to global Statistics object
        """
        if not self.settings:
            raise Exception('Cannot start the application as no settings were found!')
        services_stats = list()
        watchdogs = list()
        for config in self.settings:
            # create watchdog here
            url = config.server_urls
            service_stats = ServiceStatistics(config, url)
            services_stats.append(service_stats)
            watchdogs.append(WatchDog(statistics=service_stats, **config.__dict__))
        self.statistics = Statistics(service_statistics=services_stats)
        global statistics
        statistics = self.statistics
        self.watchdogs = watchdogs

    def run(self):
        self.__initialize_components()
        self.__start_discovery_server()
        
    def __start_discovery_server(self):
        """
        Here we make use of web.py library to build a small server which exposes APIs to query discovery server.
        """
        self.threads = [Thread(target=watchdog.watch) for watchdog in self.watchdogs]
        print("Starting watchdogs")
        for t in self.threads:
            t.start()
        
        urls = (
            '/health', '__health',
            '/stats', '__stats',
            '/dump', '__dump'
        )

        app = web.application(urls, globals())        
        
        port = self.settings.meta_info.discovery_server_port if self.settings.meta_info else DEFAULT_DISCOVERY_SERVER_PORT
        print(f"Starting Discovery Service at localhost:{port}")
        deamon = Thread(name='discovery_server', target=web.httpserver.runsimple, args=(app.wsgifunc(), ("0.0.0.0", port)))
        deamon.setDaemon(True) # This will die when the main thread dies
        deamon.start()
        print(f"Discovery Service daemon started. PID = {deamon.native_id}")
