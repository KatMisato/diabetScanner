from telegram_bot.Constants import DEFAULT_DISTRICTS


class DiabetParamsWorker:
    def __init__(self, logger, config_suffix=''):
        self.logger = logger

        self.default_positions = ["Апидра", "Новорапид", "Туджео", "Левемир", "Хумалог", "Ринфаст", "Ринлиз", "Тресиба",
                                  "Росинсулин", "Фиасп", "Лантус"]
        self.default_positions.sort()

        self.default_districts = DEFAULT_DISTRICTS
        self.default_districts.sort()

        self.default_schedule_hours = []

        self.default_schedule_days = []

        self.config_suffix = config_suffix

    def get_values_from_config(self, config_suffix=''):
        pass

    def save_positions_to_config(self, config_suffix, new_positions):
        pass

    def save_districts_to_config(self, config_suffix, new_districts):
        pass

    def save_reports_to_config(self, config_suffix, new_email, new_send_email):
        pass

    def save_schedule_to_config(self, config_suffix, new_schedule_hours, new_schedule_days, new_schedule_check):
        pass

    def save_additional_settings_to_config(self, config_suffix, new_send_full_report):
        pass

    def save_benefits_settings_to_config(self, config_suffix, new_benefit_federal):
        pass

    @staticmethod
    def check_default_district_in_settings(default_district, districts):
        default_district_clean_name = default_district.lower().replace(" район", "")
        for settings_district in districts:
            filter_setting_name = settings_district.lower().replace(" район", "")
            if default_district_clean_name == filter_setting_name:
                return True
        return False
