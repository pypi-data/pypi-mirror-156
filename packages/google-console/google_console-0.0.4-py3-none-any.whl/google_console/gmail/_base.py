import os
from typing import List, Union

import base64
import mimetypes
from email import encoders
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart


class PrivateMethods:
    
    def __init__(self):
        pass
    
    def _create_email(self, to: str, message: str, subject: str, file_attachment: Union[List[str], str], cc: str, bcc: str, message_mode: str):
        return self.__create_email(to, message, subject, file_attachment, cc, bcc, message_mode)

    # PRIVATE FUNCTION
    @staticmethod
    def __create_email(to: str, message: str, subject: str, file_attachment: Union[List[str], str], cc: str, bcc: str, message_mode: str):
        mimeMessage = MIMEMultipart()
        mimeMessage["to"] = to
        mimeMessage["subject"] = subject
        mimeMessage["cc"] = cc
        mimeMessage["bcc"] = bcc

        mimeMessage.attach(MIMEText(message, message_mode))
        if file_attachment:
            if type(file_attachment) != list: file_attachment = [file_attachment]
            for file_path in file_attachment:
                content_type, encoding = mimetypes.guess_type(file_path)
                main_type, sub_type = content_type.split("/", 1)
                filename = os.path.basename(file_path)
        
                my_file = open(file_path, "rb")
                file = MIMEBase(main_type, sub_type)
                file.set_payload(my_file.read())
                file.add_header("Content-Disposition", "attachment", filename=filename)
                encoders.encode_base64(file)
                my_file.close()
        
                mimeMessage.attach(file)

        raw_string = base64.urlsafe_b64encode(mimeMessage.as_bytes()).decode()
        return raw_string
    