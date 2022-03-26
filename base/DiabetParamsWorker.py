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

        self.config_districts = []

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
