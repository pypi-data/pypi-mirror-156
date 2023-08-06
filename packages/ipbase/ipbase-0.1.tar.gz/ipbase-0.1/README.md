# Ipbase Python Client #

Ipbase Python Client is the official Python Wrapper around the Ipbase [API](https://ipbase.com/).

## Installation

Install from pip:
````sh
pip install ipbase
````

Install from code:
````sh
pip install git+https://github.com/everapihq/ipbase-python.git
````

## Usage

All ipbase API requests are made using the `Client` class. This class must be initialized with your API access key string. [Where is my API access key?](https://app.ipbase.com/dashboard)

In your Python application, import `ipbase` and pass authentication information to initialize it:

````python
import ipbase
client = ipbase.Client('API_KEY')
````

### Retrieve Status

```python

print(client.status())

```

### Retrieve IP Information
[https://ipbase.com/docs/info](https://ipbase.com/docs/info)
```python

result = client.info()
# result = client.info('1.1.1.1', 'de')
print(result)

```


### Contact us
Any feedback? Please feel free to [contact our team](mailto:office@everapi.com).
