"""
Python Library to quickly deploy a Service Discovery Web App.
Feel free to use it when handling several microservices becomes a pain.

Created By:
===========
Divs

Mainainted By:
==============
Divs

Github Link:
============
https://github.com/Divsatwork/servpy

LinkedIn Link:
==============
https://www.linkedin.com/in/divyansh-chopra
"""
import argparse
from .constants import SERVPY_LOGO
from .discovery_server import _DiscoveryServer

from .input_processor import InputProcessor
from .request_processor import _RequestProcessor

def main():
    """
    The main driver function which will spawn all the nodes and servers based on the input file provided
    by the user.

    """
    parser = argparse.ArgumentParser(description=SERVPY_LOGO)
    parser.add_argument('-c', metavar='config_file', type=str, help='Input YML or JSON file', required=True)
    parser.add_argument('-l', metavar='logging_level', help='Logging level for the application', required=False, default='DEBUG')

    args = parser.parse_args()

    print(SERVPY_LOGO)
    print("Initializing components")
    input_processor = InputProcessor('Input Processor', args.c)
    settings, _ = input_processor.process() 
    discovery_server = _DiscoveryServer('Discovery Server', settings=settings)
    request_processor = _RequestProcessor('Request Processor', settings=settings)
    discovery_server.run()
    request_processor.process()
    
    