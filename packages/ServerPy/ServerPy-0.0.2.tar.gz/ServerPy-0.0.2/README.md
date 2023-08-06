# ServerPy

ServerPy is a Python library for resource discovery and request forwarding. User can pass in an input JSON/YAML configuration containing the details of different services and their instances and the library will take care of health check and request processing for you.

## Objective

Consider that you have 10 microservices in your ecosystem which might make certain API calls to other microservices. These microservices must be aware of all the other services and their running instances. With the use of serverpy, you just have to make request to the "Request Processor" of ServerPy and it will handle the rest of your process.

Ever heard of Eureka Server in Spring Applications? Well this is the pythonic version of that with some more extra features.

This library consists of two main modules - Discovery Server and Request Processor

Discovery Server is responsible for polling service instances and keeping a track of the service status. Request processor forwards the incoming request to the specific service instance. Both the Discovery Server and Request Processor have their own web servers which listen on the port specified in the configuration file.


## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install ServerPy.

```bash
pip install ServerPy
```

## Usage

```shell
serverpy -c <config filename>
```
For example, you can also use "test.json" provided in the repo.

```shell
serverpy -c test.json
```

## Debugging the config file
The configuration file is the driver for this library. The information contained within the input configuration file is mapped onto by different components of the library.

To start with, consider each service as a project itself. One service can have several instances. For example:
```json
{
	"service_1": {},
	"service_2": {}
}
```

Each service dictionary must contain polling information. This polling information is used by the library to make calls to the instances. Following is the model of a polling information:

```python
{
	"method": "health", 
	"endpoint": "/health",
    "frequency": 80,
	"retries": 3,
	"retry_delay": 10,
	"packet_limit": 10000,
    "priority": "high"
}
```

Description of the fields present in the polling information:
1. *method* - This specifies the method which is to be used for polling the server instance. Only two values are accepted which are "health" or "ping". **This is a mandatory field**. Health method means that the service instance exposes an API or a checkpoint to which a GET call can be made in order to verify the status of the service instance. Ping method means the library will ping the service instance url in order to verify the status of the service instance.
2. *endpoint* - In case of "health" method, the library should also be provided with the API to which the request should be made. **This is mandatory if you pass *method* as "health".
3. *frequency* - The frequency at which the library should poll the service instance. The value passed in this field indicate the number of seconds the library should wait before polling the service instance again. Default value - 60 seconds.
4. *retries* - If you wanted the library to retry polling the service instance in a given window of time, you can pass in the number of retries in this field.
5. *retry_delay* - The delay between two retries by the library. The value provided indicates the number of seconds that the library will pause for before retrying polling once again. **This is mandatory if you pass *retries*.**
6. *packet_limit* - This indicates the number of requests history you want to store in the memory. Default value is 5000.
7. *priority* - This field is only accepted when each service instance has it's own polling configuration. You can specify the priority so that when requests are being forwarded, instance with maximum availability and priority is chosen. Accepted values are "high", "med", "low".

An example of passing one polling configuration for all service instances:
```
"service2": {
	"servers": ["127.0.0.1:8080"],
	"polling": {
		"method": "health",
		"endpoint": "/health",
		"retries": 3,
		"retry_delay": 10,
		"packet_limit": 10000
	},
	"apis": [
		"/second", "/third"
	]
}
```

An example of passing different polling configuration for each service instance:
```
"service1": {
	"servers": {
		"www.google.com": {
			"method": "ping",
			"frequency": 80,
			"retries": 0,
			"packet_limit": 5000,
			"priority": "high"
		},
		"www.google.co.in": {
			"method": "ping",
			"frequency": 80,
			"retries": 0,
			"packet_limit": 5000
		}
	},
	"apis": [
		"/first", "/second/sample"
	]
}
```

Apart from the service configurations, users can also pass in Meta Information which will be used by the library.
```
"meta-info": {
		"discovery_server_name": "My Discovery Server",
		"request_processor_name": "My Request Processor",
		"discovery_server_port": 8008,
		"request_processor_port": 8081
	}
```

## APIs provided by the library

There are several APIs which the library provides in order to help the user with statistics and status of the services. All these APIs are part of the Discovery Server. These are:
1. /health - Return the status of the Discovery Server.
2. /stats - Returns the statistics of all the requests that have been made and provides the health status of all the services.
3. /dump - Dumps the statistics into a JSON format.



## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
GNU General Public License v3.0
