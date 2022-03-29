from datetime import datetime

from base.DiabetHtmlReportParser import DiabetHtmlReportParser
from base.DiabetHtmlReportSender import DiabetHtmlReportSender
from base.DiabetParamsFabric import DiabetParamsFabric

if __name__ == '__main__':
    now = datetime.now()

    config_fabric = DiabetParamsFabric(False)
    config_parser = config_fabric.get_config_worker()
    positions, districts, emails, send_email, send_full_report, schedule_hours, schedule_days, benefit_federal = config_parser.get_values_from_config()

    html_parser = DiabetHtmlReportParser()

    table, new_table = html_parser.get_tables_from_html_positions(positions=positions, districts=districts, benefit_federal=benefit_federal)

    report_sender = DiabetHtmlReportSender(now)
    report_sender.write_report(True, now, table)
    report_sender.write_report(False, now, new_table)

    if send_email:
        report_sender.send_emails(emails=emails, new_table=new_table, send_full_report=send_full_report)

    print("process finished")

