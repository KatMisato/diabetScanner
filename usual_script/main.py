from datetime import datetime

from base.DiabetConfigParser import DiabetConfigParser
from base.DiabetHtmlReportParser import DiabetHtmlReportParser
from base.DiabetHtmlReportSender import DiabetHtmlReportSender

if __name__ == '__main__':
    now = datetime.now()

    configparser = DiabetConfigParser()
    positions, districts, emails, send_email, send_full_report, schedule = configparser.get_values_from_config()

    html_parser = DiabetHtmlReportParser()

    table, new_table = html_parser.get_tables_from_html_positions(positions=positions, districts=districts)

    report_sender = DiabetHtmlReportSender(now)
    report_sender.write_report(True, now, table)
    report_sender.write_report(False, now, new_table)

    if send_email:
        report_sender.send_emails(emails=emails, new_table=new_table, send_full_report=send_full_report)

    print("process finished")

