### Read Config
This is a python library inspired in the [configparser](https://docs.python.org/2/library/configparser.html) library, but this library is designed to be used in the Sublime Text plugin, [Deviot](https://github.com/gepd/Deviot).

What are the differences with *configparser*

* It's simpler library, there are some methods not supported here (see list below)
* Designed to work only with `.ini` files
* This library doesn't wipe the comments in your `.ini` file
* It's intended to work with non ascii characters
* It's not use any raise exception, instead it return `None`, `False`, `True`
* It don't support default values

#### Examples:

**Create New File**

```python
config = ReadConfig()
config.add_section('mysection')
config.set('mysection', 'myoption', 'myvalue')

# save in file
filepath = "config.ini"
with open(filepath, 'w+') as configfile:
    config.write(configfile)
```

**Read File**

```python
filepath = "config.ini"

config = ReadConfig()
config.read(filepath)
```

**Check Section and Add New Option**

```python
# check 'mysection'
if(config.has_section('mysection')):
    print("section found!")
    # add 'newoption'
    config.set('mysection', 'newoption', 'newvalue')
```

**Check Option**

```python
if(config.has_option('mysection', 'newoption')):
    print('option found!')
```

**Write File**

```python
filepath = "config.ini"
with open(filepath, 'w+') as configfile:
    config.write(configfile)
```

#### List of Methods

| Method | Description |
|--------|-------------|
| add_section(section) | Add a section named section to the instance. If a section by the given name already exists, will return false|
|set(section, option, value)|If the given section exists, set the given option to the specified value; otherwise will return false|
|get(section, option)|Get an option value for the named section|
|has_section(section)|Checks if the named section is present or not|
|has_option(section, option)|Checks if the named option is present  or not|
|sections()|Return a list of the sections available|
|Return a list of the sections available|Returns a list of options available in the specified section|
|remove_section(section)|Remove the specified section from the configuration. If the section in fact existed, return True. Otherwise return False.|
|remove_option(section, option)|Remove the specified option from the specified section. If the section does not exist, it will return None. Otherwise will return false if the option do not exist and True if it's removed|
|write(fileobject)|Write a representation of the configuration to the specified file object|

#### Contributions

If you have a problem or a feature request you can open a new [issue](https://github.com/gepd/ReadConfig/issues) or send a [pull request](https://github.com/gepd/ReadConfig/pulls)

#### Changelog

* 30/08/2017 0.0.1 Project started 

#### Licence

[MIT License](https://github.com/gepd/ReadConfig/blob/master/LICENCE)