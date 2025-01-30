# Settings Editor

## Target assessment level

&#9314;

## Specification

### Requirements

- Python 3.10 or above.

### Functions

- Given a text settings file, gets/sets the value of settings, adds/deletes settings
- Checks the format of settings and deletes duplicated settings

### Usage

Displays script usage

```
main.py --help
```

Opens settings file `file`, use command `command` with arguments `args` to execute the command and exit, or enter commands interactively.

A settings file must be provided as the first argument to the script. If it isn't, the script exits after printing usage of the script. If the file doesn't exist, it is created. If the settings file isn't encoded in UTF-8, or there are errors opening or creating settings files, the script exits with status `2` along with an error message. Problems with settings or commands causes error messages to be printed and the status set to `1`.

```
main.py file [command] [args]
```

### Data format

Each setting takes one line and has the following format:

```
name=value
```

`name` is all the characters before the first equal sign, `value` is all the characters after the first equal sign. `value` cannot be empty.

`name` can contain characters a-z, A-Z, 0-9 and _

`value` can contain any character, can be empty

### Test case

settings.txt:

```
ScriptPath=C:\Users\yue.ouyang\main.py
Setting+Path=C:\Users\yue.ouyang\settings.txt
ScriptPath=main.py
```

```
python main.py settings.txt 

Type 'help' for a list of commands and their descriptions
Type 'help' followed by the name of a command to get its usage
> help
help: Displays help
list: Lists all settings
fix: Finds invalid settings and deletes duplicated settings
get: Gets the value of a setting
set: Sets the value of a setting
add: Adds a setting
delete: Deletes a setting
exit: Exists this script
> help get
Usage: get name
  name: The name of the setting
> get ScriptPath
C:\Users\yue.ouyang\main.py
> set ScriptPath=abc
> add NewSetting=x y z
> list
ScriptPath: abc
Invalid setting at line 2
ScriptPath: abc
NewSetting: x y z
> fix
Invalid setting at line 2
Deleted duplicated setting ScriptPath
> list
ScriptPath: abc
Invalid setting at line 2
NewSetting: x y z
> exit
```

### Checking input (level 2)

Whether the command exists is checked. If the command is not found in the dictionary, it doesn't exist. The command and arguments are first split apart with `command, args = line.split(maxsplit=1)`. `maxsplit=1` make sures that everything after the command are arguments. If there is `ValueError`, there isn't an argument. If there isn't an argument, the command's corresponding function is called directly. If there is, try to pass the arguments to the command's corresponding function with `*args.split(maxsplit=command_args_count - 1)`, so that every word is passed as an argument, and the last argument stores all the remaining words. If there is `ValueError`, then there are too few arguments.

When reading or modifying settings, try to match lines with the regular expression `^\w+=.*` to make sure the the line is a correctly formatted setting.

### Resource management (level 3)

Settings files and temporary settings files are opened with `with` statements, and will therefore be closed automatically.

Files are never entirely loaded into memory in case the file is large.
