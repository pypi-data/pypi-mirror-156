# Dtalarm


## Installation


```shell
$ pip install dtalarm
```


## Dependencies


Dtalarm supports CPython 3.6.8+, PyPy, and PyPy3.6.8+.

You can install all dependencies automatically with the following command:


```shell
$ pip install dtalarm['Pillow==8.4.0', 'requests==2.27.1', 'kaleido==0.2.1', 'plotly==5.9.0', 'numpy==1.19.5', 'pandas==1.1.5']
```


## Usage

Register a new service on the DRIVE server and get a unique secret_key.


The `DTAlarmConfig` module records the configuration information required to send alarms. Here, you need to configure a server address.

```python
from dtalarm import DTAlarmConfig

DTAlarmConfig.SERVER = ""
```


Import the `TeamsChannelAlarm` class or the `TeamsPersonalAlarm` class from the package and configure the secret_key property.

After you initialize an object, you can assign a value to the alarm object. If the alarm content is a dataframe, please use the to_json method and assign it to the table property.
```python
from dtalarm import TeamsChannelAlarm

alarm = TeamsChannelAlarm(secret_key="", channel_address="", template="message_only_v1")

alarm.title = "Title"
alarm.text = "Content"
alarm.table = df.to_json()
```


Finally, use the send function to send the alarm, it will return the response, timeout property: (optional) how many seconds to wait for the server to send data
        before giving up, as a float or tuple.

```python
response = alarm.send()
```



## Documentation

