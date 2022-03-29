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
RED_CROSS_ICON = "\U0000274C"
BACK_ICON = "\U00002B06"
# "\U00002934"
SAVE_ICON = "\U0001F4BE"
MAIL_SETTINGS_ICON = "\U0001F4EE"
ADDITIONAL_SETTINGS_ICON = "\U0001F9FE"
EMAIL_ICON = "\U0001F4E7"
HELLO_ICON = "\U0001F44B"
NOTHING_ICON = "\U0001F937"

SCHEDULE_ICON = "\U0001F4C5"
SCHEDULE_MENU_CHANGE_DAYS_ICON = "\U0001F5D3"
SCHEDULE_MENU_CHANGE_HOURS_ICON = "\U000023F0"
SCHEDULE_EVERY_HOUR_ICON = "\U0001F550"
SCHEDULE_EVERY_TWO_HOURS_ICON = "\U0001F551"
SCHEDULE_EVERY_THREE_HOURS_ICON = "\U0001F552"
SCHEDULE_EVERY_SIX_HOURS_ICON = "\U0001F555"
SCHEDULE_EVERY_HOUR_ICON_SETTINGS = "\U000023F0"
SCHEDULE_OFF_ICON = "\U0001F6D1"

RESTART_CHECK_ICON = "\U0001F504"
CHECKED_RADIO_BUTTON_ICON = PLUS_MARK_ICON
#"\U0001F518"
EMPTY_RADIO_BUTTON_ICON = "\U0001F532"

THINKING_ICON = "\U0001F914"
BYE_ICON = "\U0001F917"

ICON_MONOCLE = "\U0001F9D0"

SELECT_ALL_ICON = PLUS_MARK_ICON
UNSELECT_ALL_ICON = RED_CROSS_ICON

EVERY_HOUR_SCHEDULE = list(range(24))
EVERY_TWO_HOURS_SCHEDULE = list(range(0, 24, 2))
EVERY_THREE_HOURS_SCHEDULE = list(range(0, 24, 3))
EVERY_SIX_HOURS_SCHEDULE = list(range(0, 24, 6))

EVERY_DAY_SCHEDULE = list(range(7))

(
    POSITIONS,
    DISTRICTS,
    EMAIL,
    SEND_EMAIL,
    SEND_FULL_REPORT,
    SCHEDULE_HOURS,
    SCHEDULE_DAYS,
    SCHEDULE_CHECK,
    BENEFIT_FEDERAL,
    START_OVER,
    MESSAGES_FOR_REMOVE,
    LONG_OPERATIONS_RUNNING
) = map(chr, range(90, 102))

# Меню первого уровня
RUN_CHECK, SHOW_MENU_MAIN_SETTINGS, RUN_START, SELECTING_ACTION = range(4)

# State definitions for second level conversation
RUN_MENU_SETTINGS = range(10, 12)

# State definitions for third level conversation
SHOW_MENU_POSITIONS_SETTINGS, \
    SHOW_MENU_DISTRICTS_SETTINGS, \
    SHOW_MENU_EMAIL_SETTINGS, \
    SHOW_MENU_SCHEDULE_SETTINGS, \
    SHOW_MENU_ADDITIONAL_SETTINGS, \
    SHOW_MENU_SCHEDULE_HOURS_SETTINGS, \
    SHOW_MENU_SCHEDULE_DAYS_SETTINGS, \
    SHOW_CURRENT_SETTINGS = range(20, 28)

# State definitions for descriptions conversation
START_EDIT_POSITIONS_ADD, START_EDIT_POSITIONS_REMOVE, TYPING_FOR_ADD_POSITIONS, TYPING_FOR_REMOVE_POSITIONS, \
    SET_DISTRICTS_CHECK, CHECK_ALL_DISTRICTS, UNCHECK_ALL_DISTRICTS, \
    TYPING_FOR_SET_EMAIL, SET_REPORTS_SEND_EMAIL_CHECK, SET_REPORTS_SEND_FULL_REPORT_CHECK, \
    SET_SCHEDULE_EVERY_HOUR_CHECK, SET_SCHEDULE_EVERY_TWO_HOURS_CHECK, SET_SCHEDULE_EVERY_THREE_HOURS_CHECK, \
    SET_SCHEDULE_EVERY_SIX_HOURS_CHECK, START_EDIT_EVERY_HOUR_CHECK, START_EDIT_EVERY_DAY_CHECK, CHECK_ALL_SCHEDULE_HOURS, \
    UNCHECK_ALL_SCHEDULE_HOURS, CHECK_ALL_SCHEDULE_DAYS, UNCHECK_ALL_SCHEDULE_DAYS, \
    SET_SCHEDULE_EVERY_DAY_CHECK, SET_SCHEDULE_CHECK, \
    TYPING_FOR_CHECK_SCHEDULE_HOURS, TYPING_FOR_CHECK_SCHEDULE_DAYS, CHECK_SCHEDULE_HOUR, CHECK_SCHEDULE_DAY, \
    SET_BENEFIT_FEDERAL_CHECK, SET_BENEFIT_REGIONAL_CHECK = range(30, 58)

# Meta states
STOPPING, SHOWING, SHOWING_SETTINGS, \
    START_EDIT_POSITIONS, SAVE_POSITIONS_SETTINGS, \
    START_EDIT_DISTRICTS, SAVE_DISTRICTS_SETTINGS, \
    START_EDIT_REPORTS, START_EDIT_REPORTS_EMAIL, SAVE_REPORTS_SETTINGS, \
    START_EDIT_SCHEDULE, SAVE_SCHEDULE_SETTINGS, START_EDIT_ADDITIONAL_SETTINGS, SAVE_ADDITIONAL_SETTINGS = range(70, 84)

END = ConversationHandler.END

TEXT_FOR_MAIN_HELLO = f"Привет {HELLO_ICON}.\nЯ бот для поиска льготных лекарственных препаратов в аптеках СпБ.\n" \
                      f"Работаю с данными офиц. сайта: https://eservice.gu.spb.ru/portalFront/resources/portal.html#medicament\n\n" \
                      "<i>На момент обращения в аптеку не гарантируется наличие лекарственного препарата к выдаче, в связи с " \
                      "ограничением количества препарата в аптеке. Информацию о наличии препарата необходимо уточнить по телефону</i>"

TEXT_FOR_MENU_SETTINGS = "Вы можете редактировать или посмотреть сохраненные настройки"

TEXT_POSITIONS = "Препараты"

TEXT_DISTRICTS = "Районы"

TEXT_EMAIL_SETTINS = "Рассылка на почту"

TEXT_SCHEDULE = "Авто-проверка"

TEXT_ADDITIONAL_SETTINGS = "Доп настройки"

TEXT_SHOW_SETTINGS = "Показать настройки"

TEXT_BACK = "Назад"

TEXT_ADD_POSITION = "Для добавления введите названия препаратов через запятую"

TEXT_REMOVE_POSITION = "Для удаления введите названия препаратов через запятую"

TEXT_INPUT_EMAIL = "Введите e-mail"

TEXT_INPUT_ERROR_EMAIL = "Вы ввели неверный e-mail, повторите ввод"

TEXT_INPUT_CHECK_EMAIL = f"Выполняю проверку e-mail {ICON_MONOCLE}"

TEXT_RUN_CHECK = "Проверить наличие"

TEXT_SETTINGS = "Настроить фильтры"

TEXT_SAVE = "Сохранить"

TEXT_ADD = "Добавить"

TEXT_REMOVE = "Удалить"

TEXT_CHANGE_EMAIL = "Изменить e-mail"

TEXT_SENDING_EMAIL = "Отправлять e-mail"

TEXT_FULL_REPORT = "Нужен полный отчет"

TEXT_EVERY_HOUR = "Проверять каждый час"

TEXT_EVERY_TWO_HOURS = "Проверять каждые 2 часа"

TEXT_EVERY_THREE_HOURS = "Проверять каждые 3 часа"

TEXT_EVERY_SIX_HOURS = "Проверять каждые 6 часов"

TEXT_MENU_SETTINGS_HOURS = "Выбрать часы проверки"

TEXT_MENU_SETTINGS_DAYS = "Выбрать дни проверки"

TEXT_CHOOSE_HOURS = "Выбрать часы проверки"

TEXT_CHOOSE_DAYS = "Выбрать дни проверки"

TEXT_SCHEDULE_CHECK = "Делать авто-проверку"

TEXT_SETTINGS_SCHEDULE = "Вы можете настроить авто-проверку.\nСейчас"

TEXT_EMAIL = "E-mail"

TEXT_NOT_SET = "не задан"

TEXT_SEND_TO_EMAIL = "Результат отправлю на почту"

TEXT_SEND_TO_EMAIL_ONLY_NEW = "Найду что-то новое - отправлю на почту"

TEXT_RECEIVING_DATA = "Выполняю получение данных по "

TEXT_RECEIVING_DISTRICTS = "в районах:"

TEXT_NOT_FOUND = f"Я ничего не нашел {THINKING_ICON}. Попробуйте задать другие настройки поиска."

TEXT_NEW_NOT_FOUND = f"Я не нашел ничего нового {THINKING_ICON}. Такое бывает, если препараты не привозили в аптеки."

TEXT_MENU_REPORTS = "Вы можете изменить e-mail, на который будут отправляться отчеты с найденными препаратами.\n" \
                    "Также можете включить/выключить отправку e-mail.\n"

TEXT_BYE = f"Пока {BYE_ICON}"

TEXT_CHECK_HOURS = "Выберите часы для проверки"

TEXT_CHECK_DAYS = "Выберите дни для проверки"

TEXT_EMPTY_POSITIONS = "Нет препаратов для проверки. Задайте их в настройках, а я пока отдохну."

TEXT_EMPTY_DISTRICTS = "Нет районов для проверки. Задайте их в настройках, а я пока отдохну."

TEXT_EMPTY_POSITIONS_AND_DISTRICTS = "Нет препаратов и районов для проверки. Задайте их в настройках, а я пока отдохну."

DAYS_ARRAY = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]

TEXT_SCHEDULE_OFF = "не заданы дни и часы проверки"

TEXT_SELECT_ALL = "Отметить все"

TEXT_UNSELECT_ALL = "Отменить все"

TEXT_SCHEDULE_DAYS_SELECTED = "Дни"

TEXT_SCHEDULE_HOURS_SELECTED = "Часы"

TEXT_RESTART_CHECK = "Перезапустить поиск"

TEXT_ON = "включен"

TEXT_OFF = "выключен"

TEXT_NO_PARAMS = "не настроен"

TEXT_INFO_MUST_SET_SCHEDULE_SETTINGS = "для включения авто-проверки необходимо задать дни и часы"

DEFAULT_DISTRICTS = ["Адмиралтейский", "Василеостровский", "Выборгский",
                     "Калининский",
                     "Кировский", "Колпинский", "Красногвардейский",
                     "Красносельский",
                     "Кронштадтcкий", "Курортный", "Московский", "Невский",
                     "Петроградский", "Петродворцовый", "Приморский", "Пушкинский",
                     "Фрунзенский", "Центральный"]

TEXT_MENU_ADDITIONAL_SETTINGS = "Вы можете включить/выключить получение полного отчета со всеми найденными препаратами.\n" \
                    "<i>По-умолчанию формируется только отчет с вновь появившимися позициями</i>\n"

TEXT_BENEFIT_REGIONAL = "Региональная льгота"

TEXT_BENEFIT_REGIONAL_CHECK = "региональной льготе"

TEXT_BENEFIT_FEDERAL = "Федеральная льгота"

TEXT_BENEFIT_FEDERAL_CHECK = "федеральной льготе"
