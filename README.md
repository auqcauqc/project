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

`value` can contain any UTF-8 character

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
fix: Finds incorrectly formatted settings and deletes duplicated settings
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

A settings file must be provided as the first argument to the script. If it isn't, the script exits after printing usage of the script. If the file doesn't exist, it is created. Problems inside the settings file or with commands causes error messages to be printed and status set to 1. Exceptions that cannot be handled when creating/opening/writing to the file causes the script to exit with status 2 along with an error message.

Commands and their arguments are either read interactively in a loop or provided as arguments to the script. The command and arguments are first split apart with `command, args = line.split(maxsplit=1)`, so that everything after the command is an argument. If there is `ValueError`, it means there isn't an argument. Whether the command exists is also checked. If there isn't an argument, the command's corresponding function is called directly. If there is, try to pass the arguments to the command's corresponding function with `command_info.func(*args.split(maxsplit=(command_args_count - 1)))`, so that every word is passed as an argument, and the last argument stores all the remaining words. If there is `ValueError`, then there is an incorrect number of arguments.

When reading or modifying settings, lines are read from the settings file with a loop. Try to match each line with regular expression `^\w+=.+` to make sure the the line is a correctly formatted setting.

### Resource management (level 3)

Settings files and temporary settings files are opened with `with` statements, and will therefore be closed automatically.

Files are not never entirely loaded into memory in case the file is large.
