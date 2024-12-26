# Settings Editor

## Target assessment level

**3**

## Specification

### Functions

1. Get the values of settings from a settings file and add settings to a settings file
2. Check the format of settings and find duplicated settings

### Data format

Each setting takes one line and it has the following format:

```
setting_name=setting_value
```

`setting_name` is all the characters before the first equal sign, `setting_value` is all the characters after the first equal sign.

`setting_name` can contain characters a-z, A-Z, 0-9 and _

`setting_value` can contain any character other than newline, since each setting takes one line

### Test case

settings.txt:

```
ScriptPath=C:\Users\yue.ouyang\main.py
Setting+Path=C:\Users\yue.ouyang\settings.txt
ScriptPath=main.py
```

Using the script

```

```

### Checking input (level 2)

A settings file must be provided as the first argument to the script. If the file doesn't exist, it is created. Exceptions when creating/opening/writing to the file are handled.

Commands and their arguments, either read interactively with a loop or provided as arguments to the script, are parsed with string methods.

When reading or modifying settings, lines are read from the file with a loop, settings are checked and parsed with regular expressions
