import sys
import os

import re


# This class is based on the Exception class, the Exception class is the parent class.
# The parent class is like a template, and it needs to be initialized.
class FileReplace(Exception):
    """Used to execute os.replace() outside 'with' block."""

    def __init__(self, deleted_settings: list[str] | None = None):
        """
        Initializes a FileReplace instance.

        Args:
            deleted_settings: A list containing names of the settings that have been deleted.
              Used for printing. Defaults to None.
        """
        self.deleted_settings = deleted_settings
        super().__init__(self)  # Initializes the parent class


class CommandInfo:
    """Contains information about a command."""

    def __init__(self, func, args="", desc="", args_desc=""):
        """Initializes a CommandInfo instance.

        Args:
            func: The function that executes the command.
            args: A string containing the arguments used by the command.
              The arguments of func correspond to the arguments in this string.
            desc: A string containing the description of the command.
            args_desc: A string containing the description of the arguments of the command.
        """
        self.func = func
        self.args = args
        self.desc = desc
        self.args_desc = args_desc


class Setting:
    """Represents a setting with a name and a value.

    Attributes:
        name (str): The name of the setting.
        value (str): The value of the setting.
    """

    def __init__(self, line: str):
        """Initializes a Setting instance by extracting the name and value of a setting.

        Args:
            line: A string containing the setting.
        """
        # re.search() searches for a regular expression pattern in a string.
        # '^' means to search for the pattern at the start of the line. re.match() does this automatically.
        # '\w' means characters a-z, A-Z, and _. '.' means any character except newline.
        # The brackets create a capturing group, which allows you to capture a part of the match
        # '+' means one or more appearances of the preceding character, '*' means zero or more.

        self.name = re.search(r"^\w+", line).group()  # The entire match
        self.value = re.search("=(.*)", line).group(1)  # The first capturing group


status: int = 0


def set_status(value: int) -> None:
    # Variables defined in functions are local variables.
    # They are not accessible outside the function.
    # 'status', defined outside functions, is a global variable.
    # It can be read within any function.
    # To assign a value to a global variable, the 'global' keyword must be used.

    global status
    status = value


def clear_status() -> None:
    global status
    status = 0


def do_help(command: str | None = None) -> None:
    """List all commands or show usage of a command.

    Args:
        command (str): If not None is the name of the command to show usage of.
    """
    if command:
        print_usage(command)
        return None
    for command in commands:
        print(f"{command}: {commands[command].desc}")


def do_list() -> None:
    clear_status()

    for line_number, file_line in enumerate(file, start=1):
        setting = get_setting(file_line)
        if not setting:
            set_status(1)
            print(f"Invalid setting at line {line_number}")
            continue

        name = setting.name
        value = setting.value
        print(f"{name}: {value}")


def do_fix() -> None:
    """Finds invalid settings and deletes duplicated settings.

    A temporary settings file is created for deleting duplicated settings, since it is
    difficult to delete settings in the middle of the file.

    Raises
        FileReplace: The temporary settings file will replace the current settings file.
    """
    clear_status()

    good = True  # First assume the file has no problems
    appeared_names = []
    duplicated_names = []

    for line_number, file_line in enumerate(file, start=1):
        setting = get_setting(file_line)
        if not setting:
            good = False
            continue

        name = setting.name
        if name in appeared_names and name not in duplicated_names:
            good = False
            duplicated_names.append(name)
        else:
            appeared_names.append(name)

    if good:
        print("No problem found")
        return None

    set_status(1)
    global action
    global temp_file_path
    temp_file_path = f"{file_path}.tmp"
    action = f"creating temporary settings file '{temp_file_path}'"

    with open(temp_file_path, "w+") as file_fix:
        action = f"writing to temporary settings file '{temp_file_path}'"
        kept_names = []
        file.seek(0)
        for file_line in file:
            setting = get_setting(file_line)
            if setting:
                if setting.name in duplicated_names and setting.name not in kept_names:
                    kept_names.append(
                        setting.name
                    )  # Only keep the first setting with the name
                elif setting.name in kept_names:
                    continue  # Delete the line

            file_fix.write(file_line)

        file_fix.seek(0)
        for line_number, file_line in enumerate(file_fix, start=1):
            if not get_setting(file_line):
                print(f"Invalid setting at line {line_number}")

    action = f"writing to settings file '{file_path}'"
    raise FileReplace(duplicated_names)


def do_get(name: str) -> None:
    clear_status()

    for file_line in file:
        setting = get_setting(file_line, name=name)
        if setting:
            value = setting.value
            print(value)
            return None

    set_status(1)
    print(f"Setting '{name}' does not exist")


def do_set(line: str) -> None:
    """Sets the value of a setting.

    Args:
        line: The setting in the format 'name=new_value'

    Raises
        FileReplace: The temporary settings file will replace the current settings file.
    """
    clear_status()

    global action
    global temp_file_path
    temp_file_path = f"{file_path}.tmp"
    action = f"creating temporary settings file '{temp_file_path}'"

    if not get_setting(line):
        set_status(1)
        print(f"Invalid setting '{line}'")
        return None

    name = get_setting(line).name
    with open(temp_file_path, "w") as file_set:
        action = f"writing to temporary settings file '{temp_file_path}'"
        exist = False
        for file_line in file:
            setting = get_setting(file_line, name=name)
            if setting and setting.name == name:
                exist = True
                file_set.write(f"{line}\n")
                continue
            file_set.write(file_line)

        if not exist:
            set_status(1)
            print(f"Setting '{name}' does not exist")

        action = f"writing to settings file '{file_path}'"
        raise FileReplace


def do_add(line: str) -> None:
    clear_status()

    if not get_setting(line):
        set_status(1)
        print("'name' can be characters a-z, A-Z, 0-9, and _\n")
        print_usage("add")
        return None

    with open(file_path, "rb+") as file_add:
        # If the file is not empty (st_size is 0) and does not end with a newline, append one.
        if os.stat(file_path).st_size != 0:
            # Go to the last byte.
            # 2 means the end, -1 means minus one from the end - the last.
            file_add.seek(-1, 2)
            if file_add.read(1) != b"\n":
                file_add.seek(0, 2)
                file_add.write(b"\n")

        file_add.seek(0, 2)  # Go to the end
        file_add.write(line.encode())


def do_delete(name: str) -> None:
    """Deletes a setting.

    Args:
        name: The name of the setting.

    Raises
        FileReplace: The temporary settings file will replace the current settings file.
    """
    clear_status()

    global action
    global temp_file_path
    temp_file_path = f"{file_path}.tmp"
    action = f"creating temporary settings file '{temp_file_path}'"

    with open(temp_file_path, "w") as file_delete:
        action = f"writing to temporary settings file '{temp_file_path}'"
        exist = False
        for file_line in file:
            setting = get_setting(file_line, name=name)
            if setting and setting.name == name:
                exist = True
                continue
            file_delete.write(file_line)

        if not exist:
            set_status(1)
            print(f"Setting '{name}' does not exist")
            return None

        action = f"writing to settings file '{file_path}'"
        raise FileReplace


def do_exit():
    sys.exit(status)


commands = {
    "help": CommandInfo(
        do_help,
        args="[command]",
        desc="Displays help",
        args_desc="command: The command to display help for",
    ),
    "list": CommandInfo(do_list, desc="Lists all settings"),
    "fix": CommandInfo(
        do_fix,
        desc="Finds invalid settings and deletes duplicated settings",
    ),
    "get": CommandInfo(
        do_get,
        args="name",
        desc="Gets the value of a setting",
        args_desc="name: The name of the setting",
    ),
    "set": CommandInfo(
        do_set,
        args="line",
        desc="Sets the value of a setting",
        args_desc="line: The setting in the format 'name=new_value'",
    ),
    "add": CommandInfo(
        do_add,
        args="line",
        desc="Adds a setting",
        args_desc="line: The setting in the format 'name=value'",
    ),
    "delete": CommandInfo(
        do_delete,
        args="name",
        desc="Deletes a setting",
        args_desc="name: The name of the setting",
    ),
    "exit": CommandInfo(do_exit, desc="Exists this script"),
}


def process_input(line: str | None = None) -> None:
    """Processes the input command and executes it.

    Args:
        line: If None lets the user enter the command and arguments,
          otherwise is a string containing the command and arguments
          passed to this script.
    """
    clear_status()

    if not line:
        line = input("> ")
    line = line.lstrip()
    if not line:
        return None
    try:
        command, args = line.split(
            maxsplit=1
        )  # The first word is in command, the reset is in args
    except ValueError:  # No argument
        command = line
        args = None
    command_info = get_command_info(command)
    if not command_info:
        return None

    file.seek(0)  # Go to the start of the file before every command.

    if not args:
        command_info.func()
        return None
    command_args_count = len(
        command_info.args.split()
    )  # Get the right number of arguments of the command
    if command_args_count == 1:
        command_info.func(args)
        return None
    try:
        # Every word is passed as an argument, the last argument stores the remaining words.
        # str.split() splits the string, the asterisk assigns the split strings to each argument.
        command_info.func(*args.split(maxsplit=(command_args_count - 1)))
        return None
    except TypeError:
        print("Incorrect number of arguments")
        print_usage(command)


def get_command_info(command: str) -> CommandInfo | None:
    """Retrieves the CommandInfo object for the given command.

    Args:
        command: The name of the command for which to retrieve the CommandInfo instance.

    Returns:
        CommandInfo or None: The CommandInfo instance if the command exists; otherwise, None.
    """
    clear_status()

    try:
        return commands[command]
    except ValueError:
        set_status(1)
        print(f"Command '{command}' does not exist")


def get_setting(line: str, name: str | None = None) -> Setting | None:
    """Attempts to find a setting in the given line and create a Setting instance.

    Args:
        line: A string containing the setting.
        name: The name of the setting to find in the line. Defaults to None.

    Returns:
        Setting or None: A Setting instance if the setting is found; otherwise, None.
    """
    match = re.search(r"^\w+=.*", line)
    if not match:  # Not a valid setting
        return None
    if name:
        match = re.search(f"^{name}=.*", line)
        if not match:
            return None

    return Setting(match.group())


def print_usage(command: str | None = None) -> None:
    """Prints the usage information of the script or the given command.

    Args:
        command: The name of the command to display usage for.
            If None prints usage information of the script. Defaults to None.
    """
    if not command:
        command = os.path.basename(__file__)
        print(f"Usage:")
        print(f"  {command} --help")
        print(f"  {command} file [command] [args]")
        return None

    command_info = get_command_info(command)
    args = command_info.args
    print(f"Usage: {command} {args}")
    if args:
        for line in command_info.args_desc.splitlines():
            print(f"  {line}")


create_file = False
no_help = False
file = None
action = ""
file_path = ""
temp_file_path = ""

while True:
    try:
        if create_file:
            mode = "w+"
        else:
            mode = "r+"

        # sys.argv[1:] contains the arguments to this script.
        # At least two arguments, in which the second is the file to be opened.
        if len(sys.argv) < 2:
            set_status(1)
            print("Settings file required")
            print_usage()
            do_exit()
        if len(sys.argv) == 2 and sys.argv[1] == "--help":
            print_usage()
            do_exit()

        file_path = sys.argv[1]
        action = f"opening settings file '{file_path}'"
        with open(file_path, mode) as file:
            action = f"writing to settings file '{file_path}'"
            if len(sys.argv) > 2:
                # Execute command and exit
                process_input(" ".join(sys.argv[2:]))
                do_exit()
            if not no_help:
                print("\nType 'help' for a list of commands and their descriptions")
                print("Type 'help' followed by the name of a command to get its usage")
            while True:
                process_input()
    except FileReplace as e:
        os.replace(temp_file_path, file_path)
        if e.deleted_settings:
            for deleted_setting in e.deleted_settings:
                print(f"Deleted duplicated setting {deleted_setting}")
        no_help = True
        continue  # Restart
    except FileNotFoundError:
        print(f"Settings file '{file_path}' not found")
        print("Creating it...")
        create_file = True
        continue
    except IsADirectoryError:
        print("Cannot open a directory")
    except PermissionError:
        print(f"Permission error when {action}")
    except UnicodeDecodeError:
        print("Settings file must be a text file")
    except OSError:
        print(f"Error when {action}")
    except KeyboardInterrupt:
        print("exit")
        try:
            with open(temp_file_path, "r") as check_exist:
                pass
            os.remove(temp_file_path)
        except FileNotFoundError:
            pass
        do_exit()

    set_status(2)
    do_exit()
