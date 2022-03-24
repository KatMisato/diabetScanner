import os
from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import ssl


class DiabetHtmlReportSender:
    def __init__(self, now_time, config_suffix=''):
        self.header_html = """<!DOCTYPE html>
          <html lang="ru"> 
          <head>
          <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
          </head>"""

        self.diabetes_send_email = "diabet.scanner@gmail.com"

        self.email_login = "Diabet.Scanner"

        self.email_password = "Diabet.Scanner1"

        self.full_report_name_template = "report_full_{0}.html"

        self.new_report_name_template = "report_new_{0}.html"

        self.css_style_base = """<style> table {
                  font-family: Arial, Helvetica, sans-serif;
                  border-collapse: collapse;
                  width: 100%;
                }

                td, th {
                  border: 1px solid #ddd;
                  padding: 8px;
                }

                #district {background-color: #f2f2f2;}

                tr:hover {background-color: #ddd;}

                th {
                  padding-top: 12px;
                  padding-bottom: 12px;
                  text-align: left;
                  background-color: bg_color;
                  color: white;
                }
                </style>
                <meta charset="utf-8">"""

        self.css_style_full = self.css_style_base.replace("bg_color", "#04AA6D")

        self.css_style_new = self.css_style_base.replace("bg_color", "#FF8C00")

        self.now_time = now_time

        self.reports_dir = "../reports"

        self.config_suffix = config_suffix

    def get_reports_dir(self):
        if not self.config_suffix:
            return self.reports_dir
        return "{0}_{1}".format(self.reports_dir, self.config_suffix)

    def write_report(self, is_full_report, time_now, html_table):
        if not html_table:
            return None, None

        try:
            if not os.path.isdir(self.get_reports_dir()):
                os.makedirs(self.get_reports_dir())
        except OSError as os_error:
            print(os_error)
            return None, None

        if is_full_report:
            file_name_template = self.full_report_name_template
        else:
            file_name_template = self.new_report_name_template

        filename = file_name_template.format(self.now_time.strftime("%Y_%m_%d_%H_%M_%S"))
        filepath = os.path.join(self.get_reports_dir(), filename)

        try:
            with open(filepath, "w", encoding="utf-8") as hs:
                hs.write(self.header_html)
                if is_full_report:
                    hs.write(self.css_style_full)
                else:
                    hs.write(self.css_style_new)
                hs.writelines(html_table)
                hs.close()
        except IOError as e:
            print(e.__dict__)
        return filename, filepath

    def send_email(self, receiver_email, html_text, send_full):
        if not receiver_email:
            return
        if (not html_text or not receiver_email) and (send_full is False):
            return

        print("send e-mail to {0}".format(receiver_email))

        sender_email = self.diabetes_send_email

        formatted_time_str = self.now_time.strftime("%d.%m.%Y %H:%M:%S")
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = receiver_email
        message["Subject"] = "Наличие препаратов в аптеках на {0}".format(formatted_time_str)

        if html_text:
            message.attach(MIMEText("Изменения на {0}".format(formatted_time_str), "plain"))
            message.attach(MIMEText(html_text, "html"))
            part_new = self.add_file_to_html(self.new_report_name_template, self.now_time)
            message.attach(part_new)
        else:
            message.attach(
                MIMEText("Изменений на {0} нет, к письму приложен полный отчет"
                         .format(self.now_time.strftime("%d.%m.%Y %H:%M:%S")), "plain"))

        if send_full is True:
            part_full = self.add_file_to_html(self.full_report_name_template, self.now_time)
            message.attach(part_full)

        text = message.as_string()

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(self.email_login, self.email_password)
            server.sendmail(sender_email, receiver_email, text)

    def add_file_to_html(self, name_template, now_time):
        filename = name_template.format(now_time.strftime("%Y_%m_%d_%H_%M_%S"))
        filepath = os.path.join(self.get_reports_dir(), filename)

        with open(filepath, "rb") as attachment:
            part = MIMEText(attachment.read(), "html", "utf-8")
        encoders.encode_base64(part)

        part.add_header(
            "Content-Disposition",
            f"attachment; filename= {filename}",
        )
        return part
