import os
import smtplib
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart


class EmailSender:
    def __init__(self, address):
        self._address = address

    def send_email(self, title, image_pairs, delete=True):
        from_address = 'monkey@luckyserver.com'
        to_address = self._address
        msg = MIMEMultipart('related')
        msg['Subject'] = title
        msg['From'] = from_address
        msg['To'] = to_address
        msg_alt = MIMEMultipart('alternative')
        msg.attach(msg_alt)

        i = 0
        text = ''
        for symbol in image_pairs:
            text += '<img src="cid:image' + str(i) + '"><br>'

            image_file = open(image_pairs[symbol], 'rb').read()
            image = MIMEImage(image_file, name=symbol)
            image.add_header('Content-ID', '<image' + str(i) + '>')
            msg.attach(image)

            i += 1

        text = MIMEText(text, 'html')
        msg_alt.attach(text)

        s = smtplib.SMTP('localhost')
        s.sendmail(from_address, to_address, msg.as_string())
        s.quit()

        if delete:
            for symbol in image_pairs:
                os.remove(image_pairs[symbol])
