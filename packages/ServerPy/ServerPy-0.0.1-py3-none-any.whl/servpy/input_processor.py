from tabnanny import check

from .service_configuration import _ServiceInstanceConfiguration
from .utils import check_empty, check_type
from .models import Configuration, MetaInfo, Processor, Setting
from .constants import DEFAULT_META_INFO, POLLING_METHOD_CHOICES as polling_method_choices
import logging
import json
import yaml

log = logging.getLogger()
# TODO: Implement constants here
class InputProcessor(Processor):
    '''
    ---------------
    Input Processor
    ---------------

    Processes the input JSON/YAML file and maps all the details accordingly.

    In the input file, each service will have it's own listing. For example:
    {
        "service 1": { service 1 details }
    }\\
    The details for each service contain the following things:
    1. Service instance url (host)
    2. Polling coinfugration for that service instance.
    3. List of APIs that the instances of the service listen to.

    The service instance urls can be passed in two ways:
    1. Using dictionary style to seperate out all the instances and provide different polling
    configuration for each instance.
    2. Using list to provide all the instance, the same polling configuration.

    For more examples see:
    1. https://github.com/Divsatwork/servpy/blob/main/test.json
    2. https://github.com/Divsatwork/servpy/blob/main/test.yaml

    Workflow of the Input Processor:
    Iterate for each service ->
        if service is "meta-info" -> Assign meta-info object to the settings class.
        Check if instances in dictionary or list ->
            if list -> create same polling configuration for all instances.
            else if dictionary -> create custom polling configurations as specified.

    Prior to this, we will verify that all the neccessary information is passed from the input file.
    Some fields are optional such as priority of the instance, the packet limit per instance etc. Hence, we set
    the default values for them. More details about the mandatory fields can be found on the main github page.

    '''
    def __init__(self, processor_name: str, filename: str, *args, **kwargs):
        super().__init__(processor_name=processor_name, *args, **kwargs)
        self.config_file = filename
        self.__open_input_file()

    def __open_input_file(self):
        try:
            f = open(self.config_file)
            f.close()
        except:
            log.error(f'Error occurred while attempting to open config file. {self.config_file}')
            raise Exception(f'Error occurred while opening file: {self.config_file}. Please make sure the path is correct.')

    def parse_input_file(self, input_file: dict):
        return self.__parse_input_file(input_file)

    def process(self):
        return self.__process()

    def __process(self):
        '''
        The main config file processing method.
        Here we are considering two cases of input files - json and yaml.

        Returns:
        --------
        config = the configuration after processing

        '''
        try:
            if(self.config_file.endswith('json')):
                with open(self.config_file) as f:
                    config = json.load(f)
            elif(self.config_file.endswith('yaml')):
                with open(self.config_file) as f:
                    config = yaml.safe_load(f)
        except Exception as e:
            log.error(f'Error occured while reading file: {self.config_file}')
            raise Exception(f'Error occured while reading file: {self.config_file}')

        self.setting, errors = self.parse_input_file(config)
        
        if errors:
            raise Exception(f'Errors: {errors}')
        log.info(f"Settings loaded, {self.setting}")
        return self.setting, errors 

    def __check_input_file(self, input_file: dict) -> list:
        """
        Method to check the parsed input file.
        """
        errors = list()
        for k, v in input_file.items():
            if k == "meta-info":
                continue
            # Here k means the service name and v means it's details
            check_type(k, str, errors)
            check_type(v, dict, errors)
            check_empty(k, errors)
            check_empty(v, errors)
            check_empty(v.get('servers'), errors)
            check_type(v.get('apis'), list, errors)
            check_empty(v.get('apis'), errors)

            if v.get('servers') and type(v.get('servers')) is list:
                check_type(v.get('polling'), dict, errors)
                check_empty(v.get('polling'), errors)
                if v.get('polling'):
                    # Meaning polling section was specified. However, we will check the specifics again
                    polling = v.get('polling')
                    if polling.get('method') not in polling_method_choices:
                        errors.append(f"Incorrect polling method specified for service: {k}")
                    method = polling.get('method')
                    if (method == "health" and polling.get('endpoint') is None) or (method == "health" and type(polling.get('endpoint')) is not str):
                        errors.append(f"Please specify health endpoint for service: {k}")
            if v.get('servers') and type(v.get('servers')) is dict:
                # Iterate here for each instance detail provided.
                for _k, _v in v.get('servers').items():
                    polling = _v
                    if polling.get('method') not in polling_method_choices:
                        errors.append(f"Incorrect polling method specified for service instance: {k}|{_k}")
                    method = polling.get('method')
                    if (method == "health" and polling.get('endpoint') is None) or (method == "health" and type(polling.get('endpoint')) is not str):
                        errors.append(f"Please specify health endpoint for service instance: {k}|{_k}")
        return errors
                
    def __create_meta_info(self, input_file: dict) -> MetaInfo:
        """
        Method to create meta info which will be used by other components going forward.

        Returns: MetaInfo object
        """
        if input_file.get('meta-info'):
            meta = DEFAULT_META_INFO.copy()
            for k,v in input_file.get('meta-info').items():
                meta[k] = v
            input_file.pop('meta-info')
            return MetaInfo(**meta)
        else:
            # Use default values here
            return MetaInfo(**DEFAULT_META_INFO)

    def __import_settings_from_input(self, input_file: dict):
        setting = Setting()
        for k, v in input_file.items():
            if type(v.get('servers')) is list:
                # This means all the server instances will have the same polling information
                for instance in v.get('servers'):
                    config = {"service_name": k, "server_url": instance, **v, **v.get('polling') }
                    service_instance_config = _ServiceInstanceConfiguration(**config)
                    setting.add(service_instance_config)
            elif type(v.get('servers')) is dict:
                # This means that all the server instances have different polling information
                for _k, _v in v.get('servers').items():
                    config = {"service_name": k, "server_url": _k, **_v, **v}
                    service_instance_config = _ServiceInstanceConfiguration(**config)
                    setting.add(service_instance_config)
        return setting

    def __parse_input_file(self, input_file: dict):
        if not input_file:
            # To check if the input file does have some dataa
            return dict(), None
        
        errors = self.__check_input_file(input_file)
        if errors:
            # If errors exists, throw them for the user
            # TODO: Throw errors
            log.error(errors)
            return dict(), errors

        meta = self.__create_meta_info(input_file)

        # Creating a global settings variable to be accessed by all the other components
        setting = self.__import_settings_from_input(input_file)
        # Since we reached here, the settings are updated. Default values have been loaded and
        # we are good to go.
        setting.update_meta_info(meta)
        return setting, None

    
