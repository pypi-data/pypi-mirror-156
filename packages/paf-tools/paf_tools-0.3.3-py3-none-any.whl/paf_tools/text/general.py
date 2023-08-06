def replace_umlauts(text):
    text = text.Replace("ü", "ue")
    text = text.Replace("Ü", "Ue")
    text = text.Replace("ö", "oe")
    text = text.Replace("Ö", "Oe")
    text = text.Replace("ä", "ae")
    text = text.Replace("Ä", "Ae")
    text = text.Replace("ß", "ss")
    return text
