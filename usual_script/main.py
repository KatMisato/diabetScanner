from datetime import datetime


from base_classes.DiabetConfigParser import DiabetConfigParser
from base_classes.DiabetHtmlReportParser import DiabetHtmlReportParser
from base_classes.DiabetHtmlReportSender import DiabetHtmlReportSender

if __name__ == '__main__':
    now = datetime.now()

    configparser = DiabetConfigParser()
    positions, districts, emails, send_email, send_full_report, schedule = configparser.get_values_from_config()

    html_parser = DiabetHtmlReportParser()

    table = ""
    new_table = ""
    for position in positions:
        table_res, diff_table_res = html_parser.get_table_for_one_position(position, districts)
        if table_res:
            table += table_res
        if diff_table_res:
            new_table += diff_table_res

    report_sender = DiabetHtmlReportSender(now)
    report_sender.write_report(True, now, table)
    report_sender.write_report(False, now, new_table)
    if send_email:
        for email in emails:
            report_sender.send_email(email, new_table, send_full_report)

    print("process finished")

