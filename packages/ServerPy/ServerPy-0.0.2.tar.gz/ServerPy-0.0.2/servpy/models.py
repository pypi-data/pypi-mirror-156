import json
from datetime import datetime as dt
from typing import Any

from .utils import __get_dict__

class Server:
    '''
    Base class for Servers.
    Each server must be assigned a server_name.
    '''
    def __init__(self, server_name: str, *args, **kwargs) -> None:
        self.server_name = server_name
        for item,value in kwargs.items():
            self.__setattr__(item, value)
        
    def run(self) -> None:
        """ Override this method for the server to run"""
        pass

class Processor:
    '''
    Base class for Processors.
    Each processor must be assigned a processor_name.
    '''
    def __init__(self, processor_name: str, *args, **kwargs):
        self.processor_name = processor_name
        for item,value in kwargs.items():
            self.__setattr__(item, value)

    def process(self):
        """ Override this method for the processor to process on some entity"""
        pass

class Configuration:
    '''
    Smallest module of the input configuration file.
    One configuration is equivalent to One service details in the input json/yaml.

    service_name -- Service Names
    '''
    def __init__(self, service_name, server_urls, poll_method, poll_endpoint, apis,
    poll_retries, poll_frequency, packet_limit, retry_delay, priority, *args, **kwargs) -> None:
        self.service_name = service_name
        self.server_urls = server_urls
        self.poll_method = poll_method
        self.poll_endpoint = poll_endpoint
        self.poll_retries = poll_retries
        self.poll_freq = poll_frequency
        self.packet_limit: int = packet_limit
        self.retry_delay = retry_delay
        self.apis = apis
        self.priority = priority
    
    def __str__(self) -> str:
        return json.dumps(self, default=__get_dict__, indent=2)

    def get(self, value):
        return self.__dict__.get(value)


class MetaInfo:
    '''
    Class to store the meta information passed within the input json/yaml.
    
    Fields:
    1. discovery_server_name -> Default = "Discovery Server"
    2. request_processor_name -> Default = "Request Processor"
    3. discovery_server_port -> Default = 8888
    '''
    def __init__(self, *args, **kwargs) -> None:
        for i,v in kwargs.items():
            self.__setattr__(i, v)

    def __str__(self) -> str:
        return json.dumps(self, default=__get_dict__, indent=2)


class Setting:
    '''
    Class to model the settings provided in the input json/yaml.
    Each setting can have it's own number of configurations.
    '''
    def __init__(self, *args, **kwargs) -> None:
        self.settings = []
        self.meta_info = None

    def add(self, config: Configuration) -> None:
        self.settings.append(config)

    def update_meta_info(self, meta_info: MetaInfo) -> None:
        if meta_info:
            self.meta_info = meta_info

    def __len__(self) -> int:
        return len(self.settings)

    def __str__(self) -> str:
        return json.dumps(self, default=__get_dict__, indent=2)

    def __iter__(self) -> iter:
        return iter(self.settings)

    def __get_service_instances_by_name__(self, service_name: str) -> list:
        if not service_name:
            return list()
        return sorted((filter(lambda x: x.__dict__.get('service_name') == service_name, self.settings)),
        key=lambda x: x.__dict__.get('priority'), reverse=True)


class StatisticsPacket:
    '''
    '''
    def __init__(self) -> None:
        self.start_time = None
        self.end_time = None
        self.final_status = None
        self.response = None

    def __str__(self) -> str:
        return json.dumps(self, default=__get_dict__, indent=2)

    def mark_start(self):
        self.start_time = dt.now()

    def mark_end(self):
        self.end_time = dt.now()

    def set_status(self, status: str):
        self.final_status = status
    
    def set_response(self, resp: str):
        self.response = resp


class ServiceStatistics:
    '''
    Statistical representation for server level.
    Each instance of a service will have it's own ServiceStatistics object.
    '''
    def __init__(self, service_config: Configuration, instance_url: str, *args, **kwargs) -> None:
        # self.service = service_config
        self.instance_url = instance_url
        self.service_name = service_config.service_name
        self.check_start_time = None
        self.last_checked_at = None
        self.last_failure = None
        self.stats_packets = []
        self.packet_limit = service_config.packet_limit
    
    def __str__(self) -> str:
        return json.dumps(self, default=__get_dict__, indent=2)

    def register_packet(self, packet: StatisticsPacket) -> None:
        if type(packet) is not StatisticsPacket:
            return
        if self.packet_limit == len(self.stats_packets):
            self.stats_packets.pop(0)
        self.stats_packets.append(packet)

    def set_check_start(self) -> None:
        self.check_start_time = dt.now()

    def set_last_checked_at(self) -> None:
        self.last_checked_at = dt.now()

    def set_last_failure(self) -> None:
        self.last_failure = dt.now()



class Statistics:
    '''
    Model class for Statistics across different servers and processors.
    '''
    def __init__(self, service_statistics: list, *args, **kwargs) -> None:
        self.service_stats = service_statistics
        self.__dict__ = {
            "service_statistics": self.service_stats
        }

    def __str__(self) -> str:
        return json.dumps(self, default=__get_dict__, indent=2)


class Watcher:
    '''
    Model class for watcher.
    A watcher is nothing but an entity which will be aware of the server location and will poll the server.
    '''
    def __init__(self, server_url, polling_method, polling_url, statistics, *args, **kwargs) -> None:
        self.server_url = server_url
        self.polling_method = polling_method
        self.polling_url = polling_url
        self.statistics = statistics

    def __str__(self) -> str:
        return json.dumps(self, default=__get_dict__, indent=2)
    

