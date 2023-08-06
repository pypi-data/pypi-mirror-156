def print_object_number_to_name(number):
    if number == 53:
        return "AVFotobild"
    if number == 967:
        return "COBI DVD"
    if number == 968:
        return "CBS/DVD"
    if number == 974:
        return "AUTO BILD"
    if number == 977:
        return "SPORT BILD"
    if number == 980:
        return "COBI"
    if number == 981:
        return "COBI SP."
    if number == 983:
        return "COBI m.CD"
    if number == 1138:
        return "AB KLASSIK"
    if number == 1971:
        return "CBS"
    if number == 2000:
        return "WK"
    if number == 2010:
        return "WELTplus"
    if number == 2040:
        return "E-WK"
    if number == 2050:
        return "e-WK/WSK"
    if number == 2100:
        return "DW"
    if number == 2110:
        return "Wplus Prem"
    if number == 2120:
        return "WELT HD/MO"
    if number == 2140:
        return "E-DW"
    if number == 2150:
        return "e-DW/WS"
    if number == 2200:
        return "WAMS"
    if number == 2240:
        return "E-WamS"
    if number == 2320:
        return "BZ"
    if number == 2360:
        return "E-BZtg"
    if number == 2500:
        return "EamS"
    if number == 2540:
        return "Epaper WSK"
    if number == 2550:
        return "WSK"
    if number == 2600:
        return "BamS"
    if number == 2700:
        return "BILD"
    if number == 2710:
        return "BILDplus"
    if number == 2750:
        return "e-Bi/BamS"
    if number == 2760:
        return "FUSSB.BILD"
    if number == 2770:
        return "BIT"
    if number == 2800:
        return "B.Z."
    if number == 9075:
        return "E-CBS"
    if number == 9082:
        return "E-BamS"
    if number == 9083:
        return "E-ABK"
    if number == 9087:
        return "E-BILD"
    if number == 9088:
        return "BILD Recht"
    if number == 9741:
        return "ABMS"
    if number == "000R2200":
        return "WamS"
    if number == "00BD0002":
        return "BILD.de"
    if number == "00D00003":
        return "BILD.de"
    if number == "00D00004":
        return "BILD.de"
    if number == "00D00005":
        return "BILDPLUS Z"
    if number == "00D00006":
        return "BQ BILD"
    if number == "00D00008":
        return "AuBi Famil"


def print_object_name_to_number(name):
    raise NotImplementedError


def print_object_type_to_text(print_object_type: str) -> str:
    if print_object_type == "01":
        return "Pr.Zeitschr. wö"
    if print_object_type == "02":
        return "Pr.Zeitschr. 14"
    if print_object_type == "03":
        return "Pr.Zeitschr. mo"
    if print_object_type == "04":
        return "Fr.Zeitschr. wö"
    if print_object_type == "05":
        return "Fr.Zeitschr. 14"
    if print_object_type == "06":
        return "Fr.Zeitschr. mo"
    if print_object_type == "07":
        return "Autozeitschr."
    if print_object_type == "08":
        return "Sportzeitschr."
    if print_object_type == "09":
        return "Fam.Zeitschr."
    if print_object_type == "10":
        return "Kochzeitschr."
    if print_object_type == "11":
        return "Jugendzeitschr."
    if print_object_type == "12":
        return "Musikzeitschr."
    if print_object_type == "13":
        return "Roman"
    if print_object_type == "14":
        return "Comp.Zeitschr."
    if print_object_type == "15":
        return "Tierzeitschr."
    if print_object_type == "16":
        return "AudioVideoFoto"
    if print_object_type == "17":
        return "Gesundheitszs."
    if print_object_type == "18":
        return "Wissensmagazin"
    if print_object_type == "49":
        return "ZS Merch."
    if print_object_type == "50":
        return "DIGITALE MEDIEN"
    if print_object_type == "57":
        return "e-Paper ZS"
    if print_object_type == "90":
        return "Paid Content ZT"
    if print_object_type == "95":
        return "BILD RECHT Serv"
    if print_object_type == "97":
        return "e-Paper ZT"
    if print_object_type == "98":
        return "Sonntagszeitung"
    if print_object_type == "99":
        return "Tageszeitung"
