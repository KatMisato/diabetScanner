import os
from os import path
from configparser import ConfigParser


MAIN_CONFIG_SECTION = "MAIN_CONFIG"
POSITIONS_SECTION = "POSITIONS"
DISTRICTS_SECTION = "DISTRICTS"
EMAIL_SECTION = "E-MAIL"
SEND_EMAIL_SECTION = "SEND-E-MAIL"
SEND_FULL_REPORT_SECTION = "SEND-FULL-REPORT"
SCHEDULE_SECTION = "SCHEDULE"


class DiabetConfigParser:
    def __init__(self, config_suffix=''):
        self.default_positions = ["Апидра", "Новорапид", "Туджео", "Левемир", "Хумалог", "Ринфаст", "Ринлиз", "Тресиба",
                                  "Росинсулин", "Фиасп", "Лантус"]

        self.default_districts = ["Адмиралтейский", "Василеостровский", "Выборгский",
                                  "Калининский",
                                  "Кировский", "Колпинский", "Красногвардейский",
                                  "Красносельский",
                                  "Кронштадтcкий", "Курортный", "Московский", "Невский",
                                  "Петроградский", "Петродворцовый", "Приморский", "Пушкинский",
                                  "Фрунзенский", "Центральный"]

        self.default_schedule = []
        self.config_dir = "../configs"

        self.config_suffix = config_suffix

        self.config_districts = []

    def get_config_filename(self, config_suffix):
        if not config_suffix:
            return "{0}/config.ini".format(self.config_dir)
        return "{0}/config_{1}.ini".format(self.config_dir, config_suffix)

    def get_values_from_config(self, config_suffix=''):
        config_positions = self.default_positions
        self.config_districts = self.default_districts
        config_emails = ""
        config_send_full_report = True
        config_send_email = False
        config_schedule = self.default_schedule

        config_filename = self.get_config_filename(config_suffix)

        if path.exists(config_filename):
            config_object = ConfigParser()
            config_object.read(config_filename)
            try:
                if POSITIONS_SECTION in config_object[MAIN_CONFIG_SECTION]:
                    config_positions = config_object[MAIN_CONFIG_SECTION][POSITIONS_SECTION].replace(", ", ",").split(",")

                if DISTRICTS_SECTION in config_object[MAIN_CONFIG_SECTION]:
                    self.config_districts = config_object[MAIN_CONFIG_SECTION][DISTRICTS_SECTION].replace(", ", ",").split(",")

                if EMAIL_SECTION in config_object[MAIN_CONFIG_SECTION]:
                    config_emails = config_object[MAIN_CONFIG_SECTION][EMAIL_SECTION].replace(", ", ",").split(",")

                if SEND_EMAIL_SECTION in config_object[MAIN_CONFIG_SECTION]:
                    config_send_email = config_object.getboolean(MAIN_CONFIG_SECTION, SEND_EMAIL_SECTION)

                if SEND_FULL_REPORT_SECTION in config_object[MAIN_CONFIG_SECTION]:
                    config_send_full_report = config_object.getboolean(MAIN_CONFIG_SECTION, SEND_FULL_REPORT_SECTION)

                if SCHEDULE_SECTION in config_object[MAIN_CONFIG_SECTION]:
                    config_schedule = config_object[MAIN_CONFIG_SECTION][SCHEDULE_SECTION].replace(", ", ",").split(",")
            except KeyError:
                self.init_config_with_default_values(config_suffix)
        else:
            self.init_config_with_default_values(config_suffix)

        return config_positions, self.config_districts, config_emails, config_send_email, config_send_full_report, config_schedule

    def init_config_with_default_values(self, config_suffix):
        try:
            if not os.path.isdir(self.config_dir):
                os.makedirs(self.config_dir)
        except OSError as os_error:
            print(os_error)
            return

        config_object = ConfigParser()
        config_positions = self.default_positions
        config_districts = self.default_districts
        config_schedule = self.default_schedule

        config_object[MAIN_CONFIG_SECTION] = {
            POSITIONS_SECTION: ", ".join([str(elem) for elem in config_positions]),
            DISTRICTS_SECTION: ", ".join([str(elem) for elem in config_districts]),
            EMAIL_SECTION: "",
            SEND_EMAIL_SECTION: "0",
            SEND_FULL_REPORT_SECTION: "1",
            "SHEDULE": ", ".join([str(elem) for elem in config_schedule])
        }
        config_filename = self.get_config_filename(config_suffix)
        with open(config_filename, 'w') as conf:
            config_object.write(conf)
            conf.close()

    def save_positions_to_config(self, config_suffix, new_positions):
        config_filename = self.get_config_filename(config_suffix)
        config_object = self.read_config_from_file(config_filename)
        config_object[MAIN_CONFIG_SECTION][POSITIONS_SECTION] = ", ".join([str(elem) for elem in new_positions])
        self.write_config_to_file(config_filename, config_object)

    def save_districts_to_config(self, config_suffix, new_districts):
        config_filename = self.get_config_filename(config_suffix)
        config_object = self.read_config_from_file(config_filename)
        config_object[MAIN_CONFIG_SECTION][DISTRICTS_SECTION] = ", ".join([str(elem) for elem in new_districts])
        self.write_config_to_file(config_filename, config_object)

    def save_reports_to_config(self, config_suffix, new_email, new_send_email, new_send_full_report):
        config_filename = self.get_config_filename(config_suffix)
        config_object = self.read_config_from_file(config_filename)
        config_object[MAIN_CONFIG_SECTION][EMAIL_SECTION] = new_email
        config_object[MAIN_CONFIG_SECTION][SEND_EMAIL_SECTION] = str(new_send_email)
        config_object[MAIN_CONFIG_SECTION][SEND_FULL_REPORT_SECTION] = str(new_send_full_report)
        self.write_config_to_file(config_filename, config_object)

    def save_schedule_to_config(self, config_suffix, new_schedule):
        config_filename = self.get_config_filename(config_suffix)
        config_object = self.read_config_from_file(config_filename)
        config_object[MAIN_CONFIG_SECTION][SCHEDULE_SECTION] = ", ".join([str(elem) for elem in new_schedule])
        self.write_config_to_file(config_filename, config_object)
        
    @staticmethod
    def check_default_district_in_settings(default_district, districts):
        default_district_clean_name = default_district.lower().replace(" район", "")
        for settings_district in districts:
            filter_setting_name = settings_district.lower().replace(" район", "")
            if default_district_clean_name == filter_setting_name:
                return True
        return False

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
