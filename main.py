import sys
import os

import re


class FileReplace(Exception):
    """Used to execute os.replace() outside 'with' block."""

    def __init__(self, deleted_settings: list[str] = None):
        """
        Initializes a FileReplace instance.

        Args:
            deleted_settings: A list containing names of the settings that have been deleted.
              Used for printing. Defaults to None.
        """
        self.deleted_settings = deleted_settings
        super().__init__(self)


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

    def __init__(self, setting: re.Match):
        """Initializes a Setting instance by extracting the name and value
        from a re.Match instance.

        Args:
            setting: A re.Match instance containing a setting.
        """
        setting = setting.group()
        self.name = re.search(r"^\w+", setting).group()
        self.value = re.search("=(.+)", setting).group(1)


status: int = 0


def set_status(value: int) -> None:
    global status
    status = value


def clear_status() -> None:
    global status
    status = 0


def do_help(command=None) -> None:
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
            if setting and setting.name:
                if setting.name in duplicated_names and setting.name not in kept_names:
                    file_fix.write(file_line)
                    # Only keep the first setting with the name
                    kept_names.append(setting.name)
                    continue
                if setting.name in kept_names:
                    continue  # Delete the line

            file_fix.write(file_line)

        file_fix.seek(0)
        for line_number, file_line in enumerate(file_fix, start=1):
            if not get_setting(file_line):
                print(f"Invalid setting at line {line_number}")

    action = f"writing to settings file '{file_path}'"
    raise FileReplace(duplicated_names)


def do_get(name) -> None:
    clear_status()

    for file_line in file:
        setting = get_setting(file_line, name=name)
        if setting:
            value = setting.value
            print(value)
            return None

    set_status(1)
    print(f"Setting '{name}' does not exist")


def do_set(line) -> None:
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


def do_add(line) -> None:
    clear_status()

    if not get_setting(line):
        set_status(1)
        print("'name' can be characters a-z, A-Z, 0-9, and _")
        return None

    with open(file_path, "rb+") as file_add:
        if os.stat(file_path).st_size != 0:
            file_add.seek(-1, 2)
            # If the file doesn't end with newline, append one
            if file_add.read(1) != b"\n":
                file_add.seek(0, 2)
                file_add.write(b"\n")
        file_add.seek(0, 2)
        file_add.write(line.encode())


def do_delete(name) -> None:
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
                continue  # Delete the line
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
        desc="Finds incorrectly formatted settings and deletes duplicated settings",
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


def process_input(line: str = None) -> None:
    """Passes the command's arguments to the function that executes the command.

    Args:
        line: If None lets the user enter the command and arguments,
          otherwise is a string containing the command and arguments.
    """
    clear_status()

    if not line:
        line = input("> ")
    if line == "":
        return None
    # Only the first word is in command, the reset is in args
    try:
        command, args = line.split(maxsplit=1)
    except ValueError:  # No argument
        command = line
        args = None
    command_info = get_command_info(command)
    if not command_info:
        return None

    file.seek(0)
    if not args:
        command_info.func()
        return None
    # Get the right number of arguments of the command
    command_args_count = len(command_info.args.split())
    try:
        # Every word is passed as an argument, the last argument stores the remaining words
        command_info.func(*args.split(maxsplit=(command_args_count - 1)))
        return None
    except TypeError:
        print("Incorrect number of arguments")
        print_usage(command)


def get_command_info(command: str) -> CommandInfo:
    """Retrieves the CommandInfo instance for the given command.

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


def get_setting(line: str, name: str = None) -> Setting | None:
    """Attempts to find a setting in the given line and create a Setting instance.

    Args:
        line: A string containing the setting.
        name: The name of the setting to find in the line. Defaults to None.

    Returns:
        Setting or None: A Setting instance if the setting is found; otherwise, None.
    """
    setting = re.search(r"^\w+=.+", line)
    if not setting:
        return None
    if name:
        setting = re.search(f"^{name}=.+", line)
        if not setting:
            return None
    return Setting(setting)


def print_usage(command: str = None) -> None:
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
while True:
    try:
        if create_file:
            mode = "w+"
        else:
            mode = "r+"

        # At least two arguments, in which the second is the file to be opened
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
        do_exit()

    set_status(2)
    do_exit()
