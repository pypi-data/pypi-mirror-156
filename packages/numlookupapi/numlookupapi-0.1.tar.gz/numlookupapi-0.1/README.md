# NumlookAPI Python Client #

CurrencyAPI Python Client is the official Python Wrapper around the CurrencyAPI [API](https://numlookupapi.com/).

## Installation

Install from pip:
````sh
pip install numlookupapi
````

Install from code:
````sh
pip install git+https://github.com/everapihq/numlookupapi-python.git
````

## Usage

All numlookupapi API requests are made using the `Client` class. This class must be initialized with your API access key string. [Where is my API access key?](https://app.numlookupapi.com/dashboard)

In your Python application, import `numlookupapi` and pass authentication information to initialize it:

````python
import numlookupapi
client = numlookupapi.Client('API_KEY')
````

### Retrieve Status

```python

print(client.status())

```

### Retrieve Currencies
[https://numlookupapi.com/docs/validate](https://numlookupapi.com/docs/validate)
```python

result = client.validate('+14158586273')
# result = client.validate('14158586273', country_code='US')
print(result)

```


### Contact us
Any feedback? Please feel free to [contact our team](mailto:office@everapi.com).
