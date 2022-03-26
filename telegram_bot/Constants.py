from telegram.ext import ConversationHandler

SETTINGS_ICON = "\U00002699"
PLUS_MARK_ICON = "\U00002705"
MINUS_MARK_ICON = "\U00002796"

DISTRICTS_ICON = "\U0001F5FA"
POSITIONS_ICON = "\U0001F48A"

SHOW_SETTINGS_ICON = "\U0001F4D1"
RUN_CHECK_ICON = "\U0001F680"

OK_ICON = "\U00002705"
ADD_POSITIONS_ICON = "\U0001F516"
REMOVE_POSITIONS_ICON = "\U0000274C"
BACK_ICON = "\U00002934"
SAVE_ICON = "\U0001F4BE"
REPORT_ICON = "\U0001F9FE"
EMAIL_ICON = "\U0001F4E7"
HELLO_ICON = "\U0001F44B"
NOTHING_ICON = "\U0001F937"

SCHEDULE_ICON = "\U0001F4C5"
SCHEDULE_EVERY_HOUR_ICON = "\U0001F550"
SCHEDULE_EVERY_TWO_HOURS_ICON = "\U0001F551"
SCHEDULE_EVERY_THREE_HOURS_ICON = "\U0001F552"
SCHEDULE_EVERY_SIX_HOURS_ICON = "\U0001F555"
SCHEDULE_EVERY_HOUR_ICON_SETTINGS = "\U000023F0"
SCHEDULE_OFF_ICON = "\U0001F6D1"

THINKING_ICON = "\U0001F914"
BYE_ICON = "\U0001F917"

EVERY_HOUR_SCHEDULE = list(range(24))
EVERY_TWO_HOURS_SCHEDULE = list(range(0, 24, 2))
EVERY_THREE_HOURS_SCHEDULE = list(range(0, 24, 3))
EVERY_SIX_HOURS_SCHEDULE = list(range(0, 24, 6))

(
    POSITIONS,
    DISTRICTS,
    EMAIL,
    SEND_EMAIL,
    SEND_FULL_REPORT,
    SCHEDULE,
    START_OVER,
    MESSAGES_FOR_REMOVE
) = map(chr, range(30, 38))

# Меню первого уровня
RUN_CHECK, SHOW_MENU_MAIN_SETTINGS, RUN_START, SELECTING_ACTION = range(4)

# State definitions for second level conversation
RUN_MENU_SETTINGS = range(10, 12)

# State definitions for third level conversation
SHOW_MENU_POSITIONS_SETTINGS, \
    SHOW_MENU_DISTRICTS_SETTINGS, \
    SHOW_MENU_REPORTS_SETTINGS, \
    SHOW_MENU_SCHEDULE_SETTINGS, \
    SHOW_CURRENT_SETTINGS = range(20, 25)

# State definitions for descriptions conversation
START_EDIT_POSITIONS_ADD, START_EDIT_POSITIONS_REMOVE, TYPING_FOR_ADD_POSITIONS, TYPING_FOR_REMOVE_POSITIONS, \
    SET_DISTRICTS_CHECK, \
    TYPING_FOR_SET_EMAIL, SET_REPORTS_SEND_EMAIL_CHECK, SET_REPORTS_SEND_FULL_REPORT_CHECK, \
    SET_SCHEDULE_EVERY_HOUR_CHECK, SET_SCHEDULE_EVERY_TWO_HOURS_CHECK, SET_SCHEDULE_EVERY_THREE_HOURS_CHECK, \
    SET_SCHEDULE_EVERY_SIX_HOURS_CHECK, START_EDIT_EVERY_HOUR_CHECK, SET_SCHEDULE_OFF_CHECK, \
    TYPING_FOR_CHECK_SCHEDULE_HOURS, CHECK_SCHEDULE_HOUR = range(30, 46)

# Meta states
STOPPING, SHOWING, SHOWING_SETTINGS, \
    START_EDIT_POSITIONS, SAVE_POSITIONS_SETTINGS, \
    START_EDIT_DISTRICTS, SAVE_DISTRICTS_SETTINGS, \
    START_EDIT_REPORTS, START_EDIT_REPORTS_EMAIL, SAVE_REPORTS_SETTINGS, \
    START_EDIT_SCHEDULE, SAVE_SCHEDULE_SETTINGS = range(50, 62)

END = ConversationHandler.END

TEXT_FOR_MAIN_HELLO = f"Привет {HELLO_ICON}.\nЯ бот для проверки наличия льготных препаратов через сайт госуслуг Санкт-Петербурга\n\n" \
                      "<i>На момент обращения в аптеку не гарантируется наличие лекарственного препарата к выдаче, в связи с " \
                      "ограничением количества препарата в аптеке. Информацию о наличии препарата необходимо уточнить по телефону</i>"

TEXT_FOR_MENU_SETTINGS = "Вы можете редактировать или посмотреть сохраненные настройки"

TEXT_POSITIONS = "Препараты"

TEXT_DISTRICTS = "Районы"

TEXT_REPORTS = "Отчеты"

TEXT_SCHEDULE = "Расписание"

TEXT_SHOW_SETTINGS = "Показать настройки"

TEXT_BACK = "Назад"

TEXT_ADD_POSITION = "Для добавления введите названия препаратов через запятую"

TEXT_REMOVE_POSITION = "Для удаления введите названия препаратов через запятую"

TEXT_INPUT_EMAIL = "Введите e-mail"

TEXT_RUN_CHECK = "Запустить проверку"

TEXT_SETTINGS = "Настройки"

TEXT_SAVE = "Сохранить"

TEXT_ADD = "Добавить"

TEXT_REMOVE = "Удалить"

TEXT_CHANGE_EMAIL = "Изменить e-mail"

TEXT_SENDING_EMAIL = "Отправка e-mail"

TEXT_FULL_REPORT = "Формирование полного отчета"

TEXT_EVERY_HOUR = "Проверять каждый час"

TEXT_EVERY_TWO_HOURS = "Проверять каждые 2 часа"

TEXT_EVERY_THREE_HOURS = "Проверять каждые 2 часа"

TEXT_EVERY_SIX_HOURS = "Проверять каждые 6 часов"

TEXT_CHOOSE_HOURS = "Выбрать часы проверки"

TEXT_OFFCHECK = "Выключить проверку по расписанию"

TEXT_SETTINGS_SCHEDULE = "Вы можете настроить расписание проверок\nСейчас"

TEXT_EMAIL = "E-mail"

TEXT_NOT_SET = "не задан"

TEXT_SEND_TO_EMAIL = "Результат отправлю на почту"

TEXT_SEND_TO_EMAIL_ONLY_NEW = "Найду что-то новое - отправлю на почту"

TEXT_RECEIVING_DATA = "Выполняю получение данных по следующим районам:"

TEXT_NOT_FOUND = f"Я ничего не нашел {THINKING_ICON}. Попробуйте задать другие настройки поиска."

TEXT_NEW_NOT_FOUND = f"Я не нашел ничего нового {THINKING_ICON}. Такое бывает, если препараты не привозили в аптеки."

TEXT_MENU_REPORTS = "Вы можете изменить e-mail, на который будут отправляться отчеты с найденными препаратами.\n" \
                    "Также можете включить/выключить отправку отчетов на e-mail и формирование полного отчета со всеми найденными препаратами.\n" \
                    "По-умолчанию формируется только отчет с вновь появившимися позициями\n"

TEXT_BYE = f"Пока {BYE_ICON}"

TEXT_CHECK_HOURS = "Выберите часы для проверки"
