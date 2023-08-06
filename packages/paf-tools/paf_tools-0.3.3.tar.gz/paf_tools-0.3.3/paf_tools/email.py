import smtplib

from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class Email:
    def __init__(self):
        self._attachments: list = []
        self._reply_addresses: list = []
        self._receiver: list = []
        self._sender: str = ''
        self._username: str = ''
        self._subject: str = ''
        self._password: str = ''
        self._text: str = ''

    def sender(self, sender: str = None):
        if sender is None:
            return self._sender
        self._sender = sender

    def attachments(self, *attachments):
        if len(attachments) == 0:
            return self._attachments
        for attachment in attachments:
            self._attachments.append(attachment)

    def attachment(self, attachment: str = None):
        if attachment is None:
            return self._attachments
        self._attachments.append(attachment)

    def reply_address(self, reply_address: str = None):
        if reply_address is None:
            return self._reply_addresses
        self._reply_addresses.append(reply_address)

    def reply_addresses(self, *reply_addresses):
        if len(reply_addresses) == 0:
            return self._reply_addresses
        for reply_address in reply_addresses:
            self._reply_addresses.append(reply_address)

    def receiver(self, receiver: str = None):
        if receiver is None:
            return self._receiver
        self._receiver.append(receiver)

    def receivers(self, *receivers):
        if len(receivers) == 0:
            return self._receiver
        for receiver in receivers:
            self._receiver.append(receiver)

    def content(self, subject: str = None, text: str = None):
        if subject is None and text is None:
            return self._subject, self._text
        self._subject = subject
        self._text = text

    def login_credentials(self, username: str = None, password: str = None):
        if username is None and password is None:
            return self._username, self._password
        self._username = username
        self._password = password

    def _check_preconditions(self):
        if self._username is None:
            raise ValueError("Username for sending an as-paf-paf_tools-email is not set")
        if self._password is None:
            raise ValueError("No password for the username is set")
        if self._sender is None:
            raise ValueError("No sender is set")
        if len(self._receiver) == 0:
            raise ValueError("Mail-Receivers are not set")
        if self._subject is None:
            raise ValueError("No subject for the as-paf-paf_tools-email is set")

    def send(self, username=None, password=None, sender=None, receivers=None, subject=None, text=None, reply_addresses=None,
             attachments=None):
        if username is not None:
            self._username = username
        if password is not None:
            self._password = password
        if sender is not None:
            self._sender = sender
        if receivers is not None:
            self._receiver.append(receivers)
        if subject is not None:
            self._subject = subject
        if text is not None:
            self._text = text
        if reply_addresses is not None:
            self._reply_addresses.append(reply_addresses)
        if attachments is not None:
            self._attachments.append(attachments)

        self._check_preconditions()

        # Create MIMEMultipart object
        msg = MIMEMultipart("mixed")  # mixed, empty, alternative
        msg["Subject"] = self._subject
        html = self._text

        part = MIMEText(html, "html")
        msg.attach(part)

        # Add Attachment
        if len(self._attachments) > 0:
            for file in self._attachments:  # add files to the message
                # file_path = as-paf-paf_tools-os.path.join(dir_path, f)
                attachment = MIMEApplication(open(file, "rb").read(), _subtype="txt")
                attachment.add_header('Content-Disposition', 'attachment', filename=file)
                msg.attach(attachment)

        mailserver = smtplib.SMTP('smtp.office365.com', 587)
        mailserver.ehlo()
        mailserver.starttls()
        mailserver.login(self._username, self._password)
        mailserver.sendmail(self._sender, self._receiver, msg.as_string())
        mailserver.quit()


if __name__ == "__main__":
    mail = Email()
    mail.sender("christian.koester@axelspringer.com")
    mail.content("Ein Versuch", "Hier ist der<br />Inhalt")

    mail.receivers("chris19177@gmail.com", "christian@familie-koester.eu")
    mail.attachments("C:\\AS_Programme\\DatabaseConnection.as-paf-paf_tools-json", "C:\\AS_Programme\\Db.as-paf-paf_tools-json")
    mail.send()
