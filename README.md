# Settings Editor

## Target assessment level

**3**

## Specification

### Functions

1. Given a text settings file, get/set the value of settings, add/delete settings
2. Check the format of settings and delete duplicated settings

### Data format

Each setting takes one line and has the following format:

```
name=value
```

`name` is all the characters before the first equal sign, `value` is all the characters after the first equal sign. `value` cannot be empty.

`name` can contain characters a-z, A-Z, 0-9 and _

`value` can contain any character other than newline, since each setting takes one line

### Test case

settings.txt:

```
ScriptPath=C:\Users\yue.ouyang\main.py
Setting+Path=C:\Users\yue.ouyang\settings.txt
ScriptPath=main.py
```

Using the script

```
main.py settings.txt

Type 'help' for a list of commands and their descriptions
Type 'help' followed by the name of a command to get its usage
> help
help: Displays help
list: Lists all settings
fix: Check the format of settings and delete duplicated settings
get: Gets the value of a setting
set: Sets the value of a setting
add: Adds a setting
delete: Deletes a setting
exit: Exists this script
> help get
Usage: get name
  name: The name of the setting
```

### Checking input (level 2)

A settings file must be provided as the first argument to the script. If it isn't, the script exits after printing usage of the script. If the file doesn't exist, it is created. Exceptions when creating/opening/writing to the file are handled.

Commands and their arguments, either read interactively in a loop or provided as arguments to the script, are parsed with string methods.

When reading or modifying settings, lines are read from the file with a loop, settings are checked and parsed with regular expressions

### Resource management (level 3)

The settings file and temporary settings files are opened with `with` statements, and will therefore be closed automatically.

When quickly creating a new settings file, the file is created and closed immediately.

Files are not entirely loaded into memory at once, in case the file is large.
