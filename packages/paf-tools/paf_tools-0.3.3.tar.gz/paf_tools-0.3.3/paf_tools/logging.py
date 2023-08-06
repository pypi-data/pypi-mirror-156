from enum import Enum

_session_name = None
_app_name = None
_available_targets = []


class Targets(Enum):
    MAIL = "Mail",
    JSON_FILE = "Json_File",
    CONSOLE = "Console",
    TEXT_FILE = "Text_File",
    DATABASE = "Database",


def app_name(name: str = None) -> str:
    global _app_name
    if name is None:
        return _app_name
    _app_name = name


def session_name(name: str = None) -> str:
    global _session_name
    if name is None:
        return _session_name
    _session_name = name


def targets(*the_targets: Targets) -> list:
    global _available_targets
    if not the_targets:
        return _available_targets

    _available_targets = list(the_targets)


def target(the_target: Targets):
    _available_targets.append(the_target)


def get_call_stack():
    raise NotImplementedError


def init(the_session_name:str=None, the_app_name:str=None, *the_targets:Targets):
    global _available_targets, _session_name, _app_name
    _session_name = the_session_name
    _app_name = the_app_name
    if the_targets:
        for the_target in the_targets:
            _available_targets.append(the_target)
    # appData = get_call_stack()


def target_mail():
    # write to temp
    raise NotImplementedError


def target_console():
    raise NotImplementedError


def target_database():
    raise NotImplementedError


def target_csv_file():
    raise NotImplementedError


def target_text_file():
    raise NotImplementedError


def trace(message):
    write(message, LogLevel.Trace)


def debug(message):
    Write(message, LogLevel.Debug)


def info(message):
    Write(message, LogLevel.Info)


def warn(message):
    Write(message, LogLevel.Warn)


def error(message):
    Write(message, LogLevel.error)


def fatal(message):
    Write(message, LogLevel.Fatal)


def write(message, logLevel):
    if (logLevel == LogLevel.Trace):
        Logger.Trace(message)
    if (logLevel == LogLevel.Debug):
        Logger.Debug(message)
    if (logLevel == LogLevel.Info):
        Logger.Info(message)
    if (logLevel == LogLevel.Warn):
        Logger.Warn(message)
    if (logLevel == LogLevel.error):
        Logger.error(message)
    if (logLevel == LogLevel.Fatal):
        Logger.Fatal(message)


class available_targets:
    mail = False
    colored_console = False
    json_file = False
    console = True
    text_file = False
    database = False
    csv_file = False

    def clear():
        available_targets.mail = False
        available_targets.colored_console = False
        available_targets.json_file = False
        available_targets.console = False
        available_targets.text_file = False
        available_targets.database = False
        available_targets.csv_file = False
