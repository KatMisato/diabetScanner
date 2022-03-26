class DiabetParamsWorker:
    def __init__(self, logger, config_suffix=''):
        self.logger = logger

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

        self.config_suffix = config_suffix

    def get_values_from_config(self, config_suffix=''):
        pass

    def save_positions_to_config(self, config_suffix, new_positions):
        pass

    def save_districts_to_config(self, config_suffix, new_districts):
        pass

    def save_reports_to_config(self, config_suffix, new_email, new_send_email, new_send_full_report):
        pass

    def save_schedule_to_config(self, config_suffix, new_schedule):
        pass

    @staticmethod
    def check_default_district_in_settings(default_district, districts):
        default_district_clean_name = default_district.lower().replace(" район", "")
        for settings_district in districts:
            filter_setting_name = settings_district.lower().replace(" район", "")
            if default_district_clean_name == filter_setting_name:
                return True
        return False
