# What is ConfigParser
ConfigParser is parser for some format.

# How To Use
## Load files
```python
from ConfigParser import ConfigParser

# JSON file
cfg = ConfigParser("Test.json")
# YAML file
cfg = ConfigParser("Test.yaml")
```

## Add attributes

```python
from ConfigParser import ConfigParser

cfg = ConfigParser("Test.json")
cfg.hoge = 10
```


## Save as JSON or YAML files
```python
from ConfigParser import ConfigParser

cfg = ConfigParser("Test.json")
cfg.hoge = 10
cfg.write()					# Save as Test.json(will override)
cfg.write("Result.json")    # Save as a new JSON file
```

## Creawte configuration without files
```python
from ConfigParser import ConfigParser

cfg = ConfigParser()
cfg.hoge = 10
cfg.write("Result.json")	# You must specify the file name
```
