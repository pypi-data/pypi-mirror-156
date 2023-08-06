from enum import Enum

import xmltodict
from . import database
from .database import ReturnTypes


def credentials(credentials_name: str, user: str = None, password: str = None):
    if user is not None:
        query = f'INSERT INTO config_Credentials (Username, Password, Id) VALUES (\'{user}\', \'{password}\', \'{credentials_name}\')'
        database.execute(query, returns=ReturnTypes.no_return)
    else:
        query = f'SELECT * FROM config_Credentials WHERE Id = \'{credentials_name}\''
        row = database.execute(query=query, returns=ReturnTypes.one_row)

        return Credentials(user=row[1], password=row[2])


def get(config_group, config_key):
    query = f'SELECT ConfigValue, IsXml FROM config WHERE ConfigGroup = \'{config_group}\' AND ConfigKey = \'{config_key}\''
    row = database.execute(query=query, returns=ReturnTypes.one_row)

    if len(row) == 0:
        return None
    if not row[1]:
        return row[0] if isinstance(row, tuple) else row['ConfigValue']
    data = xmltodict.parse(row[0])
    return data['Configuration']


def get_email_addresses_by_last_name(*lastnames):
    raise NotImplementedError


def email_addresses(*addresses):
    """
        Dictionary < string, Emailaddress > returnValues = new
        Dictionary < string, Emailaddress > ();

        if (_eMailAdresses is null) Load("Emailadressen");

        foreach(string address in addresses)
            Emailaddress emailAddress = new Emailaddress();
            foreach(XmlNode xmlNode in _eMailAdresses.DocumentElement.SelectSingleNode("//email_adresse[@id='" + address + "']").ChildNodes)
                emailAddress.Zuweisen(xmlNode.Name, xmlNode.InnerText);
        returnValues.Add(address, emailAddress);
    return new ReadOnlyDictionary < string, Emailaddress > (returnValues);
    """
    raise NotImplementedError


def signatures(name: str):
    """
    if (_signatures is null) Load("Signaturen");
        return _signatures.DocumentElement.SelectSingleNode("//signatur[@id='" + name + "']").InnerText;
    """
    raise NotImplementedError


def email_receivers(*searchValues):
    """
    List < string > returnValues = new List < string > ();
    if (_data is null) Load("lokal");
    foreach(XmlNode xmlNode in _data.SelectNodes("//" + string.Join("/", searchValues)))
        returnValues.Add(xmlNode.InnerText);
    return returnValues.ToArray();
    """
    raise NotImplementedError


def email_content(_data, searchValues):
    """
    if (_data is null) Load("lokal");
    EmailContent returnValue = new EmailContent();
    foreach(XmlNode xmlNode in _data.SelectSingleNode("//" + string.Join("/", searchValues)).ChildNodes)
        returnValue.Assign(xmlNode.Name, xmlNode.InnerText);
    return returnValue;
    """
    raise NotImplementedError


class ConfigTypes(Enum):
    email_addresses = 1
    signatures = 2
    credentials = 3
    key_value = 4


class ReturnTypes(Enum):
    no_return = 1
    one_row = 2
    all_rows = 3


class Credentials:
    user = ""
    password = ""

    def __init__(self, user=None, password=None):
        if user is not None:
            self.user = user
        if password is not None:
            self.password = password


class EmailAddress:
    firstname = ""
    lastname = ""
    address = ""


class EmailContent:
    subject = ""
    address = ""
    text = ""
