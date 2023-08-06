from enum import Enum
from typing import NoReturn

import pymssql
import yaml

sql_connection = None
_config: dict


class Constants:
    CONFIG_PATH = r'c://.paf/Configuration/Database.yml'


class ReturnTypes(Enum):
    no_return = 1
    one_row = 2
    all_rows = 3


def close_connection():
    raise NotImplementedError
    # SqlConnection.Close()


def open_connection_twi():
    global _config
    database_configuration()
    if _config:
        open_connection(server_name=_config['Server'], database=_config['Database'], user=_config['User'],
                        password=_config['Password'])
        return True
    return False


def database_configuration(database: str = None, user: str = None, password: str = None, server: str = None,
                           current_server: str = None) -> NoReturn:
    global _config
    _config = {}

    config_path = Constants.CONFIG_PATH
    with open(config_path) as file:
        local_config = yaml.full_load(file)
    if current_server is None:
        current_server = local_config['Default_Server']

    if database is not None:
        local_config['Servers'][current_server]['Database'] = database
    if user is not None:
        local_config['Servers'][current_server]['User'] = user
    if password is not None:
        local_config['Servers'][current_server]['Password'] = password
    if server is not None:
        local_config['Servers'][current_server]['Server'] = server

    _config['Server'] = local_config['Servers'][current_server][0]['Server']
    _config['User'] = local_config['Servers'][current_server][1]['User']
    _config['Password'] = local_config['Servers'][current_server][2]['Password']
    _config['Database'] = local_config['Servers'][current_server][3]['Database']


def connection_string():
    global _config
    if _config := database_configuration():
        return build_string(server_name=_config['Server'], database=_config['Database'],
                            user=_config['User'], password=_config['Password'])
    return None


def build_string(server_name: str, database: str, user: str, password: str):
    return f'Data Source={server_name};Initial Catalog={database};User ID={user};Password={password}'


def open_connection(server_name: str, database: str, user: str, password: str):
    global sql_connection

    try:
        sql_connection = pymssql.connect(server=server_name, user=user, password=password, database=database)
        return True
    except Exception as ex:
        print(ex)
        return False


def execute(query, returns: ReturnTypes = ReturnTypes.one_row):
    global _config, sql_connection

    is_connected = False
    if sql_connection is None:
        database_configuration()
        is_connected = open_connection(server_name=_config['Server'], database=_config['Database'],
                                       user=_config['User'], password=_config['Password'])
    else:
        is_connected = True
    if is_connected is False:
        raise Exception('No connection to a as-paf-paf_tools-database-server could be established!')

    try:
        if returns.name == 'no_return':
            sql_connection.execute_non_query(query)
            return None
        elif returns.name == 'one_row':
            cursor = sql_connection.cursor()
            cursor.execute(query)
            return cursor.fetchone()
        elif returns.name == 'all_rows':
            cursor = sql_connection.cursor()
            cursor.execute(query)
            return cursor.fetchall()
    except Exception as ex:
        print(f'Error occurred during as-paf-paf_tools-database request: {ex}')
