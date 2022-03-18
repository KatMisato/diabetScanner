import email
import json
import smtplib
import ssl
from configparser import ConfigParser
from datetime import datetime
from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from os import path
from urllib import request, error

BASE_URL = "https://eservice.gu.spb.ru/portalFront/proxy/async?filter={}&operation=getMedicament&ost1=true&ost2=true"

TIMEOUT = 30

COUNT_TRIES = 10

HEADERS = ["Название", "Адрес", "Федеральная льгота", "Региональная льгота"]

HEADERS_DIFF = ["Название", "Адрес", "Что изменилось"]

DEFAULT_POSITIONS = ["Апидра", "Новорапид", "Туджео", "Левемир", "Хумалог", "Ринфаст", "Ринлиз", "Тресиба",
                     "Росинсулин", "Фиасп", "Лантус"]

DEFAULT_DISTRICTS = ["Адмиралтейский район", "Василеостровский район", "Выборгский район", "Калининский район",
                     "Кировский район", "Колпинский район", "Красногвардейский район", "Красносельский район",
                     "Кронштадтcкий район", "Курортный район", "Московский район", "Невский район",
                     "Петроградский район", "Петродворцовый район", "Приморский район", "Пушкинский район",
                     "Фрунзенский район", "Центральный район"]

CONFIG_FILE_NAME = "config.ini"

NOTHING_FOUND = "Ничего не найдено"

DIABETES_SEND_EMAIL = "diabet.scanner@gmail.com"

DIABETES_SEND_EMAIL_LOGIN = "Diabet.Scanner"

DIABETES_SEND_EMAIL_PASSWORD = "Diabet.Scanner1"

FULL_REPORT_NAME_TEMPLATE = "report_full_{0}.html"
NEW_REPORT_NAME_TEMPLATE = "report_new_{0}.html"

HEADER_HTML = """<!DOCTYPE html>
          <html lang="ru"> 
          <head>
          <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
          </head>"""

CSS_STYLE_BASE = """<style> table {
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

CSS_STYLE_FULL = CSS_STYLE_BASE.replace("bg_color", "#04AA6D")

CSS_STYLE_NEW = CSS_STYLE_BASE.replace("bg_color", "#FF8C00")


def init_config_with_default_values():
    config_object = ConfigParser()
    config_positions = DEFAULT_POSITIONS
    config_districts = DEFAULT_DISTRICTS
    config_object["MAIN_CONFIG"] = {
        "POSITIONS": ", ".join([str(elem) for elem in config_positions]),
        "DISTRICTS": ", ".join([str(elem) for elem in config_districts]),
        "E-MAIL": "",
        "SEND-FULL-REPORT": "1"
    }
    with open('config.ini', 'w') as conf:
        config_object.write(conf)
        conf.close()


def get_values_from_config():
    config_positions = DEFAULT_POSITIONS
    config_districts = DEFAULT_DISTRICTS
    config_emails = ""
    config_send_full_report = True
    if path.exists(CONFIG_FILE_NAME):
        config_object = ConfigParser()
        config_object.read("config.ini")
        try:
            config_positions = config_object["MAIN_CONFIG"]["POSITIONS"].replace(", ", ",").split(",")
            config_districts = config_object["MAIN_CONFIG"]["DISTRICTS"].replace(", ", ",").split(",")
            if "E-MAIL" in config_object["MAIN_CONFIG"]:
                config_emails = config_object["MAIN_CONFIG"]["E-MAIL"].replace(", ", ",").split(",")
            if "SEND-FULL-REPORT" in config_object["MAIN_CONFIG"]:
                config_send_full_report = config_object.getboolean("MAIN_CONFIG", "SEND-FULL-REPORT")
        except KeyError:
            init_config_with_default_values()
    else:
        init_config_with_default_values()

    return config_positions, config_districts, config_emails, config_send_full_report


def clear_address(address):
    return address.split('*')[0].replace(", ,", ", ").replace("  ", " ")


def add_district_to_table(district):
    district_table = "  <tr id=\"district\"><td>{0}</td></tr>\n  <tr>\n".format(district["name"].strip())
    for pharmacy in district["apothecaries"]:
        district_table += add_pharmacy_to_table(pharmacy)
    return district_table


def add_new_district_to_table(district):
    district_table = "  <tr id=\"district\"><td>{0}</td></tr>\n  <tr>\n".format(district["name"].strip())
    for pharmacy in district["apothecaries"]:
        district_table += add_new_pharmacy_to_table(pharmacy)
    return district_table


def add_pharmacy_to_table(pharmacy):
    district_table = "  <tr>\n"
    for pharmacy_column in [pharmacy["name"], clear_address(pharmacy["address"]),
                            pharmacy["ost1"], pharmacy["ost2"]]:
        district_table += "    <td>{0}</td>\n".format(pharmacy_column.strip())
    district_table += "  </tr>\n"
    return district_table


def add_new_pharmacy_to_table(new_pharmacy):
    ost1_new = float(new_pharmacy["ost1"].replace(",", "."))
    ost2_new = float(new_pharmacy["ost2"].replace(",", "."))

    district_table = "  <tr>\n"
    for pharmacy_column in [new_pharmacy["name"], clear_address(new_pharmacy["address"])]:
        district_table += "    <td>{0}</td>\n".format(pharmacy_column.strip())

    district_table += "    <td>"
    if ost1_new != 0:
        district_table += "Федеральная льгота: {0} ({1}) ".format(ost1_new, new_pharmacy["date"])

    if ost2_new != 0:
        district_table += "Региональная льгота: {0} ({1})".format(ost2_new, new_pharmacy["date"])

    district_table += "</td>\n  </tr>\n"

    return district_table


def add_diff_pharmacy_to_table(old_pharmacy, new_pharmacy):
    ost1_new = float(new_pharmacy["ost1"].replace(",", "."))
    ost2_new = float(new_pharmacy["ost2"].replace(",", "."))
    ost1_old = float(old_pharmacy["ost1"].replace(",", "."))
    ost2_old = float(old_pharmacy["ost2"].replace(",", "."))

    district_table = ""
    if (ost1_old == 0 or ost2_old == 0) and (ost1_new != ost1_old or ost2_new != ost2_old):
        district_table += "  <tr>\n"
        for pharmacy_column in [new_pharmacy["name"], clear_address(new_pharmacy["address"])]:
            district_table += "    <td>{0}</td>\n".format(pharmacy_column.strip())

        district_table += "    <td>"
        if ost1_new != ost1_old:
            district_table += "Федеральная льгота: не было {0} -> {1} ({2}) ".format(old_pharmacy["date"],
                                                                                     ost1_new, new_pharmacy["date"])

        if ost2_new != ost2_old:
            district_table += "Региональная льгота: не было {0} -> {1} ({2})".format(old_pharmacy["date"],
                                                                                     ost2_new, new_pharmacy["date"])

        district_table += "</td>\n  </tr>\n"

    return district_table


def find_district_in_result(district_id, result_for_check):
    if "districts" not in result_for_check:
        return None

    for district in result_for_check["districts"]:
        if district["id"] == district_id:
            return district
    return None


def find_pharmacy_in_district(checking_name, district_for_check):
    for pharmacy in district_for_check["apothecaries"]:
        if pharmacy["name"] == checking_name:
            return pharmacy
    return None


def print_table_headers(h1_name, headers):
    html_headers = "<h1>{0}</h1><table>\n  <tr>\n".format(h1_name)
    for column in headers:
        html_headers += "    <th>{0}</th>\n".format(column.strip())
    html_headers += "  </tr>\n"
    return html_headers


def check_district_name(district_name, filter_data):
    return district_name in filter_data


def get_table_for_one_position(name, districts_data):
    url = BASE_URL.format(request.quote(name)).strip()
    print("get data for {0} ...".format(name))

    res_table = ""
    data_diff = ""
    for count_tries in range(1, COUNT_TRIES):
        try:
            contents = request.urlopen(url, timeout=TIMEOUT).read()
            json_res = json.loads(contents.decode("utf-8"))

            if json_res["status"] == "FAILED":
                res_table += "<h1>{0}</h1>".format(name)
                res_table += "<h2>{0}</h2>".format(NOTHING_FOUND)
            else:
                result = json_res["model"]["result"][0]

                data_file_name = 'json_data_{0}.json'.format(name)

                try:
                    with open(data_file_name) as json_file:
                        previous_result = json.load(json_file)
                except FileNotFoundError:
                    previous_result = {}

                with open(data_file_name, 'w') as outfile:
                    json.dump(result, outfile, indent=4)

                res_table += print_table_headers(result["name"], HEADERS)

                table_diff = ""
                for district in result["districts"]:
                    if check_district_name(district["name"], districts_data):
                        res_table += add_district_to_table(district)

                        checking_district = find_district_in_result(district["id"], previous_result)
                        if checking_district is None:
                            table_diff += add_new_district_to_table(district)
                        else:
                            for pharmacy in district["apothecaries"]:
                                checking_pharmacy = find_pharmacy_in_district(pharmacy["name"], checking_district)
                                if checking_pharmacy is None:
                                    table_diff += add_new_pharmacy_to_table(pharmacy)
                                else:
                                    table_diff += add_diff_pharmacy_to_table(checking_pharmacy, pharmacy)

                res_table += "</table>"

                if table_diff:
                    data_diff += print_table_headers(result["name"], HEADERS_DIFF) + table_diff + "</table>"
            break
        except error.HTTPError as e:
            print(e.__dict__)
        except error.URLError as e:
            print(e.__dict__)

    return res_table, data_diff


def write_report(report_name_template, css_style_name, time_now, html_table):
    if not html_table:
        return
    try:
        with open(report_name_template.format(time_now.strftime("%Y_%m_%d_%H_%M_%S")), "w", encoding="utf-8") as hs:
            hs.write(HEADER_HTML)
            hs.write(css_style_name)
            hs.writelines(html_table)
            hs.close()
    except IOError as e:
        print(e.__dict__)


def add_file_to_html(name_template, now_time):
    filename = name_template.format(now_time.strftime("%Y_%m_%d_%H_%M_%S"))  # In same directory as script

    with open(filename, "rb") as attachment:
        part = MIMEText(attachment.read(), "html", "utf-8")
    encoders.encode_base64(part)

    part.add_header(
        "Content-Disposition",
        f"attachment; filename= {filename}",
    )
    return part


def send_email(receiver_email, html_text, now_time, send_full):
    if not email:
        return
    if (not html_text or not email) and (send_full is False):
        return

    print("send e-mail to {0}".format(receiver_email))

    sender_email = DIABETES_SEND_EMAIL

    message = MIMEMultipart()
    message["From"] = DIABETES_SEND_EMAIL
    message["To"] = receiver_email
    message["Subject"] = "Наличие препаратов в аптеках"

    if html_text:
        message.attach(MIMEText("Изменения на {0}".format(now_time.strftime("%d.%m.%Y %H:%M:%S")), "plain"))
        message.attach(MIMEText(html_text, "html"))
        part_new = add_file_to_html(NEW_REPORT_NAME_TEMPLATE, now_time)
        message.attach(part_new)
    else:
        message.attach(
            MIMEText("Изменений на {0} нет, к письму приложен полный отчет"
                     .format(now_time.strftime("%d.%m.%Y %H:%M:%S")), "plain"))

    if send_full is True:
        part_full = add_file_to_html(FULL_REPORT_NAME_TEMPLATE, now_time)
        message.attach(part_full)

    text = message.as_string()

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(DIABETES_SEND_EMAIL_LOGIN, DIABETES_SEND_EMAIL_PASSWORD)
        server.sendmail(sender_email, receiver_email, text)


if __name__ == '__main__':
    positions, districts, emails, send_full_report = get_values_from_config()
    table = ""
    new_table = ""
    for position in positions:
        table_res, diff_table_res = get_table_for_one_position(position, districts)
        if table_res:
            table += table_res
        if diff_table_res:
            new_table += diff_table_res

    now = datetime.now()
    write_report(FULL_REPORT_NAME_TEMPLATE, CSS_STYLE_FULL, now, table)
    write_report(NEW_REPORT_NAME_TEMPLATE, CSS_STYLE_NEW, now, new_table)
    for email in emails:
        send_email(email, new_table, now, send_full_report)
    print("process finished")

