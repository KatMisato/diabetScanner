import os
from os import path
from configparser import ConfigParser

from base.DiabetParamsWorker import DiabetParamsWorker

MAIN_CONFIG_SECTION = "MAIN_CONFIG"
POSITIONS_SECTION = "POSITIONS"
DISTRICTS_SECTION = "DISTRICTS"
EMAIL_SECTION = "E-MAIL"
SEND_EMAIL_SECTION = "SEND-E-MAIL"
SEND_FULL_REPORT_SECTION = "SEND-FULL-REPORT"
SCHEDULE_HOURS_SECTION = "SCHEDULE-HOURS"
SCHEDULE_DAYS_SECTION = "SCHEDULE-DAYS"
SCHEDULE_CHECK = "SCHEDULE-CHECK"
BENEFIT_FEDERAL = "BENEFIT-FEDERAL"


class DiabetConfigParser(DiabetParamsWorker):
    def __init__(self, logger=None, config_suffix=''):
        super().__init__(logger, config_suffix)
        self.config_dir = "../configs"

        self.config_suffix = config_suffix

    def get_config_filename(self, config_suffix):
        if not config_suffix:
            return "{0}/config.ini".format(self.config_dir)
        return "{0}/config_{1}.ini".format(self.config_dir, config_suffix)

    def get_values_from_config(self, config_suffix=''):
        config_positions = self.default_positions
        config_districts = self.default_districts
        config_emails = ""
        config_send_full_report = True
        config_send_email = False
        config_schedule_hours = self.default_schedule_hours
        config_schedule_days = self.default_schedule_days
        config_schedule_check = False
        config_benefit_federal = True

        config_filename = self.get_config_filename(config_suffix)

        if path.exists(config_filename):
            config_object = ConfigParser()
            config_object.read(config_filename)
            try:
                config_positions = self.get_array_section(config_object, POSITIONS_SECTION)
                config_positions.sort()
                config_districts = self.get_array_section(config_object, DISTRICTS_SECTION)
                config_districts.sort()
                config_emails = self.get_array_section(config_object, EMAIL_SECTION)
                config_send_email = self.get_boolean_section(config_object, SEND_EMAIL_SECTION, False)
                config_send_full_report = self.get_boolean_section(config_object, SEND_FULL_REPORT_SECTION, True)
                config_schedule_hours = self.get_array_section(config_object, SCHEDULE_HOURS_SECTION)
                config_schedule_days = self.get_array_section(config_object, SCHEDULE_DAYS_SECTION)
                config_schedule_check = self.get_boolean_section(config_object, SCHEDULE_CHECK, False)
                config_benefit_federal = self.get_boolean_section(config_object, BENEFIT_FEDERAL, True)
            except KeyError as key_error:
                print(key_error)
                self.init_config_with_default_values(config_suffix)
        else:
            self.init_config_with_default_values(config_suffix)

        return config_positions, config_districts, config_emails, config_send_email, config_send_full_report, config_schedule_hours, config_schedule_days, config_schedule_check, config_benefit_federal

    def init_config_with_default_values(self, config_suffix):
        try:
            if not os.path.isdir(self.config_dir):
                os.makedirs(self.config_dir)
        except OSError as os_error:
            print(os_error)
            return

        config_object = ConfigParser()

        config_object[MAIN_CONFIG_SECTION] = {}
        self.set_array_section(config_object, POSITIONS_SECTION, self.default_positions)
        self.set_array_section(config_object, DISTRICTS_SECTION, self.default_districts)
        self.set_array_section(config_object, EMAIL_SECTION, "")
        self.set_boolean_section(config_object, SEND_EMAIL_SECTION, False)
        self.set_boolean_section(config_object, SEND_FULL_REPORT_SECTION, True)
        self.set_array_section(config_object, SCHEDULE_HOURS_SECTION, self.default_schedule_hours)
        self.set_array_section(config_object, SCHEDULE_DAYS_SECTION, self.default_schedule_days)
        self.set_boolean_section(config_object, SCHEDULE_CHECK, False)
        self.set_boolean_section(config_object, BENEFIT_FEDERAL, True)

        config_filename = self.get_config_filename(config_suffix)
        with open(config_filename, 'w') as conf:
            config_object.write(conf)
            conf.close()

    def save_positions_to_config(self, config_suffix, new_positions):
        self.save_array_to_config(config_suffix=config_suffix, section_name=POSITIONS_SECTION,
                                  array_value=new_positions)

    def save_districts_to_config(self, config_suffix, new_districts):
        print(f"save_districts_to_config, new_districts = {new_districts}")
        self.save_array_to_config(config_suffix=config_suffix, section_name=DISTRICTS_SECTION,
                                  array_value=new_districts)

    def save_reports_to_config(self, config_suffix, new_email, new_send_email):
        config_filename = self.get_config_filename(config_suffix)
        config_object = self.read_config_from_file(config_filename)
        config_object[MAIN_CONFIG_SECTION][EMAIL_SECTION] = new_email
        config_object[MAIN_CONFIG_SECTION][SEND_EMAIL_SECTION] = str(new_send_email)
        self.write_config_to_file(config_filename, config_object)

    def save_schedule_to_config(self, config_suffix, new_schedule_hours, new_schedule_days, new_schedule_check):
        config_filename = self.get_config_filename(config_suffix)
        config_object = self.read_config_from_file(config_filename)
        self.set_array_section(config_object=config_object, section_name=SCHEDULE_HOURS_SECTION,
                               array_value=new_schedule_hours)
        self.set_array_section(config_object=config_object, section_name=SCHEDULE_DAYS_SECTION,
                               array_value=new_schedule_days)
        config_object[MAIN_CONFIG_SECTION][SCHEDULE_CHECK] = str(new_schedule_check)
        print(f"{config_object[MAIN_CONFIG_SECTION][SCHEDULE_CHECK]}")
        self.write_config_to_file(config_filename, config_object)

    def save_additional_settings_to_config(self, config_suffix, new_send_full_report, new_benefit_federal):
        config_filename = self.get_config_filename(config_suffix)
        config_object = self.read_config_from_file(config_filename)
        config_object[MAIN_CONFIG_SECTION][SEND_FULL_REPORT_SECTION] = str(new_send_full_report)
        config_object[MAIN_CONFIG_SECTION][BENEFIT_FEDERAL] = str(new_benefit_federal)
        self.write_config_to_file(config_filename, config_object)

    @staticmethod
    def read_config_from_file(filename):
        config_object = ConfigParser()
        config_object.read(filename)
        return config_object

    @staticmethod
    def write_config_to_file(filename, config_object):
        with open(filename, 'w') as conf:
            config_object.write(conf)
            conf.close()

    @staticmethod
    def get_array_section(config_object, section_name):
        if section_name in config_object[MAIN_CONFIG_SECTION]:
            result = config_object[MAIN_CONFIG_SECTION][section_name].replace(", ", ",").split(",")
            if len(result) and not len(result[0]):
                return []
            return result
        return []

    @staticmethod
    def set_array_section(config_object, section_name, array_value):
        if not len(array_value):
            config_object[MAIN_CONFIG_SECTION][section_name] = ""
        else:
            config_object[MAIN_CONFIG_SECTION][section_name] = ", ".join([str(elem) for elem in array_value])

    @staticmethod
    def set_boolean_section(config_object, section_name, boolean_value):
        config_object[MAIN_CONFIG_SECTION][section_name] = str(boolean_value)

    @staticmethod
    def get_boolean_section(config_object, section_name, default_value):
        if section_name in config_object[MAIN_CONFIG_SECTION]:
            return config_object.getboolean(MAIN_CONFIG_SECTION, section_name)
        return default_value

    def save_array_to_config(self, config_suffix, section_name, array_value):
        config_filename = self.get_config_filename(config_suffix)
        config_object = self.read_config_from_file(config_filename)
        print(f"config_filename = {config_filename}")
        self.set_array_section(config_object, section_name, array_value)
        print(f"data = {config_object[MAIN_CONFIG_SECTION][section_name]}")
        self.write_config_to_file(filename=config_filename, config_object=config_object)
