# yb_config
This module is for managing configuration data for Python projects. 

## Web Configuration 
This is for general web applications and basic Python programs. Importing the configuration object can be 
done with the following code:

```python
from ybconfig import WebConfig

config_data = WebConfig()
```

The ```WebConfig``` class is a Singleton meaning that once the ```WebConfig``` class is initialized, it will 
not be initialized again throughout the rest of the program's lifetime. Every call to a ```WebConfig``` 
instance will point to the same memory address so the data will be consistent across all ```WebConfig```
instances. 

### Setting up environment 
The ```WebConfig``` class can load from either a YML file or environment variables. If we are going to load 
from a YML file, we need to make sure that the path to the YML file is the last argument passed into the 
Python file like so:
```bash
python some_file.py ./path/to/config.yml
```
If we want to not have a YML file but get our config variables from environment variables then the config file 
path is not needed. Instead, we need to state that the environment variable ```ENVIRONMENT_CONFIG``` to 
```TRUE```. 

### Getting variables 
Getting variables from the config data is done using the ```get``` function with the following parameters:

**param key:** ```str``` the key that the variable is stored under

**param file:** ```bool``` if set to True will force to get data from a yml file despite defaults

**param environ** ```bool``` if set to True will force to get data from the environment variables despite defaults

**param strict** ```bool``` if set to True will throw an error if the key is not present
