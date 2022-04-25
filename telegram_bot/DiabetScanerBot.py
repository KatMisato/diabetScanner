import logging
import sys

from telegram.ext import Updater, CommandHandler, Filters, MessageHandler, CallbackQueryHandler
from telegram import ChatAction, InlineKeyboardMarkup

from threading import Thread
from functools import wraps
from datetime import datetime

from Utils import *
from base.DiabetHtmlReportParser import DiabetHtmlReportParser
from base.DiabetHtmlReportSender import DiabetHtmlReportSender
from base.DiabetParamsFabric import DiabetParamsFabric

# logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO, filename="bot_log.log")
logger = logging.getLogger(__name__)

global_heroku_run = False
global_chat_id = 0


def update_callback_answer(update: Update, context: CallbackContext, text):
    res_array = []
    if not update.callback_query and update.message:
        res_array.append(update.message.reply_text(text=text, parse_mode=telegram.ParseMode.HTML))
    else:
        try:
            update.callback_query.answer()
            if update.callback_query.message.text != text:
                return update.callback_query.edit_message_text(text=text, parse_mode=telegram.ParseMode.HTML)
        except Exception as e:
            logger.info(f"update_callback_answer error = {e}")
            bot = context.bot
            if not update.message:
                if len(text) > 4096:
                    for x in range(0, len(text), 4096):
                        res_array.append(bot.send_message(global_chat_id, text[x:x + 4096]))
                else:
                    res_array.append(bot.send_message(global_chat_id, text=text, parse_mode=telegram.ParseMode.HTML))
            else:
                logger.info(f"update_callback_answer not update.callback_query")
                res_array.append(update.message.reply_text(text=text, parse_mode=telegram.ParseMode.HTML))
    return res_array


def update_callback_answer_with_keyboard(update: Update, context: CallbackContext, text, keyboard):
    if not update.callback_query and update.message:
        update.message.reply_text(text=text, parse_mode=telegram.ParseMode.HTML, reply_markup=keyboard)
    else:
        try:
            update.callback_query.answer()
            if update.callback_query.message.text != text or update.callback_query.message.reply_markup != keyboard:
                update.callback_query.edit_message_text(text=text, parse_mode=telegram.ParseMode.HTML,
                                                        reply_markup=keyboard)
        except Exception as e:
            logger.info(f"update_callback_answer_with_keyboard error = {e}")
            bot = context.bot
            if not update.message:
                if len(text) > 4096:
                    for x in range(0, len(text), 4096):
                        bot.send_message(global_chat_id, text[x:x + 4096])
                else:
                    bot.send_message(global_chat_id, text=text, parse_mode=telegram.ParseMode.HTML,
                                     reply_markup=keyboard)
            else:
                logger.info(f"update_callback_answer_with_keyboard not update.callback_query")
                update.message.reply_text(text=text, parse_mode=telegram.ParseMode.HTML, reply_markup=keyboard)


def set_start_over_flag(context: CallbackContext, value: bool):
    user_data = context.user_data
    if context.user_data:
        user_data[START_OVER] = value


def set_long_operation_flag(context: CallbackContext):
    user_data = context.user_data
    if context.user_data and context.user_data.get(LONG_OPERATIONS_RUNNING):
        user_data[LONG_OPERATIONS_RUNNING] = True


def clear_long_operation_flag(context: CallbackContext):
    user_data = context.user_data
    if context.user_data and context.user_data.get(LONG_OPERATIONS_RUNNING):
        user_data[LONG_OPERATIONS_RUNNING] = False


def is_long_operation_flag(context: CallbackContext) -> bool:
    user_data = context.user_data
    if context.user_data and context.user_data.get(LONG_OPERATIONS_RUNNING):
        return user_data[LONG_OPERATIONS_RUNNING]
    return False


def get_config_parser(chat_id):
    config_fabric = DiabetParamsFabric(global_heroku_run, logger, chat_id)
    return config_fabric.get_config_worker()


def send_typing_action(func):
    logger.info("send_typing_action")

    @wraps(func)
    def command_func(update, context, *args, **kwargs):
        context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.UPLOAD_DOCUMENT)
        return func(update, context, *args, **kwargs)

    return command_func


@send_typing_action
def my_handler(_, _1):
    pass


def start_edit_positions_add(update: Update, context: CallbackContext) -> int:
    logger.info("start_edit_positions_add")
    update_callback_answer(update=update, context=context, text=TEXT_ADD_POSITION)
    return TYPING_FOR_ADD_POSITIONS


def start_edit_positions_remove(update: Update, context: CallbackContext) -> int:
    logger.info("start_edit_positions_remove")
    update_callback_answer(update=update, context=context, text=TEXT_REMOVE_POSITION)
    return TYPING_FOR_REMOVE_POSITIONS


def start_edit_reports_email(update: Update, context: CallbackContext) -> int:
    logger.info("start_edit_reports_email")

    delete_messages(update=update, context=context)
    if context.user_data.get(START_OVER):
        update_callback_answer(update=update, context=context, text=TEXT_INPUT_ERROR_EMAIL)
    else:
        update_callback_answer(update=update, context=context, text=TEXT_INPUT_EMAIL)

    return TYPING_FOR_SET_EMAIL


def save_add_positions_input(update: Update, context: CallbackContext) -> int:
    logger.info("save_add_positions_input")
    user_data = context.user_data
    if user_data:
        user_data[POSITIONS] += clear_list_for_edit(new_list=update.message.text, current_list=user_data[POSITIONS],
                                                    logger=logger, without_checking=False)
        set_start_over_flag(context, True)

    return show_menu_positions_settings(update, context)


def save_remove_positions_input(update: Update, context: CallbackContext) -> int:
    logger.info("save_remove_positions_input")
    user_data = context.user_data

    list_for_removing = clear_list_for_edit(new_list=update.message.text, current_list=user_data[POSITIONS],
                                            logger=logger, without_checking=True)

    for position_removing in list_for_removing:
        index_for_remove = -1
        for index, positions in enumerate(user_data[POSITIONS]):
            if position_removing.lower() == positions.lower():
                index_for_remove = index
                break
        if index_for_remove != -1:
            user_data[POSITIONS].pop(index_for_remove)

    set_start_over_flag(context, True)
    return show_menu_positions_settings(update, context)


def save_email_input(update: Update, context: CallbackContext) -> int:
    logger.info("save_email_input")
    delete_messages(update=update, context=context)
    user_data = context.user_data
    if user_data:
        user_data[MESSAGES_FOR_REMOVE] = update.message.reply_text(text=TEXT_INPUT_CHECK_EMAIL,
                                                                   parse_mode=telegram.ParseMode.HTML)
    if check_email_address(update.message.text):
        if user_data:
            user_data[EMAIL] = update.message.text
            set_start_over_flag(context, True)
        return show_menu_schedule_settings(update=update, context=context)
    else:
        set_start_over_flag(context, True)
        return show_menu_schedule_settings(update=update, context=context)


def send_feedback(update: Update, context: CallbackContext) -> int:
    logger.info(f"send_feedback, text = {update.message.text}")
    delete_messages(update=update, context=context)

    user_data = context.user_data

    buttons = [[get_back_button()]]
    keyboard = InlineKeyboardMarkup(buttons)

    if user_data:
        now = datetime.now()
        report_sender = DiabetHtmlReportSender(now, 0)
        feedback_text = update.message.text

        user = update.message.from_user
        text_email = f"<h3>Сообщение от пользователя {user['username']}</h3>\n\n{feedback_text}"
        report_sender.send_email_feedback(subject="", html_text=text_email)
        user_data[MESSAGES_FOR_REMOVE] = update.message.reply_text(
            text=f"Спасибо, отправил информацию",
            parse_mode=telegram.ParseMode.HTML,
            reply_markup=keyboard)

    set_start_over_flag(context, True)

    return SHOWING


def start(update: Update, context: CallbackContext):
    logger.info("start")
    if is_long_operation_flag(context):
        return RUN_START

    fill_data_from_settings(heroku_run=global_heroku_run, update=update, context=context, logger=logger)

    global global_chat_id
    global_chat_id = update.effective_chat.id

    buttons = [
        [
            InlineKeyboardButton(text=f"{RUN_CHECK_ICON} {TEXT_RUN_CHECK}", callback_data=str(RUN_CHECK)),
        ],
        [
            InlineKeyboardButton(text=f"{SETTINGS_ICON} {TEXT_SETTINGS}", callback_data=str(SHOW_MENU_MAIN_SETTINGS)),
        ],
        [
            InlineKeyboardButton(text=f"{FEEDBACK_ICON} {TEXT_GET_FEEDBACK}", callback_data=str(RUN_GET_FEEDBACK)),
        ],
    ]
    keyboard = InlineKeyboardMarkup(buttons)

    delete_messages(update=update, context=context)

    if context.user_data.get(START_OVER) and update.callback_query:
        update_callback_answer_with_keyboard(update=update, context=context, text=TEXT_FOR_MAIN_HELLO,
                                             keyboard=keyboard)
    else:
        update.message.reply_text(text=TEXT_FOR_MAIN_HELLO, parse_mode=telegram.ParseMode.HTML, reply_markup=keyboard)

    set_start_over_flag(context, False)
    context.user_data[MESSAGES_FOR_REMOVE] = []

    return SELECTING_ACTION


def show_menu_settings(update: Update, context: CallbackContext):
    logger.info("edit_main_settings")

    schedule_check = context.user_data[SCHEDULE_CHECK]

    if schedule_check:
        mark_schedule_every_hour = EMPTY_RADIO_BUTTON_ICON
        mark_schedule_timetable = CHECKED_RADIO_BUTTON_ICON
    else:
        mark_schedule_every_hour = CHECKED_RADIO_BUTTON_ICON
        mark_schedule_timetable = EMPTY_RADIO_BUTTON_ICON

    buttons = [
        [
            InlineKeyboardButton(text=f"{mark_schedule_every_hour} {TEXT_EVERY_HOUR}",
                                 callback_data=str(SET_SCHEDULE_ENABLE_EVERY_HOUR_CHECK)),
        ],
        [
            InlineKeyboardButton(text=f"{mark_schedule_timetable} {TEXT_SCHEDULE}",
                                 callback_data=str(SET_SCHEDULE_ENABLE_SCHEDULE_CHECK))
        ],
        [
            InlineKeyboardButton(text=f"{POSITIONS_ICON} {TEXT_POSITIONS}",
                                 callback_data=str(SHOW_MENU_POSITIONS_SETTINGS))
        ],
        [
            InlineKeyboardButton(text=f"{DISTRICTS_ICON} {TEXT_DISTRICTS}",
                                 callback_data=str(SHOW_MENU_DISTRICTS_SETTINGS))
        ],
        [
            InlineKeyboardButton(text=f"{BENEFITS_ICON} {TEXT_BENEFITS}",
                                 callback_data=str(SHOW_MENU_BENEFITS_SETTINGS))
        ],
        [
            InlineKeyboardButton(text=f"{SCHEDULE_ICON} {TEXT_SCHEDULE}",
                                 callback_data=str(SHOW_MENU_SCHEDULE_SETTINGS))
        ],
        [
            InlineKeyboardButton(text=f"{SHOW_SETTINGS_ICON} {TEXT_SHOW_SETTINGS}",
                                 callback_data=str(SHOW_CURRENT_SETTINGS)),
            get_back_button()
        ]
    ]
    keyboard = InlineKeyboardMarkup(buttons)

    if not context.user_data.get(START_OVER) or not update.message:
        update_callback_answer_with_keyboard(update=update, context=context, text=TEXT_FOR_MENU_SETTINGS,
                                             keyboard=keyboard)
    else:
        update.message.reply_text(text=TEXT_FOR_MENU_SETTINGS, reply_markup=keyboard)

    return RUN_MENU_SETTINGS


def show_menu_positions_settings(update: Update, context: CallbackContext):
    logger.info("positions_settings")
    positions = context.user_data[POSITIONS]

    buttons = [
        [
            InlineKeyboardButton(text=f"{ADD_POSITIONS_ICON} {TEXT_ADD}", callback_data=str(START_EDIT_POSITIONS_ADD)),
            InlineKeyboardButton(text=f"{RED_CROSS_ICON} {TEXT_REMOVE}",
                                 callback_data=str(START_EDIT_POSITIONS_REMOVE))
        ],
        [
            InlineKeyboardButton(text=f"{SAVE_ICON} {TEXT_SAVE}", callback_data=str(SAVE_POSITIONS_SETTINGS)),
            get_back_button(),
        ],
    ]
    keyboard = InlineKeyboardMarkup(buttons)

    if len(positions):
        text = "Препараты для проверки. Сейчас заданы: {0}".format(", ".join(positions))
    else:
        text = "Препараты для проверки. Сейчас не задано ни одного."
    if ((context.user_data and context.user_data.get(START_OVER)) or not update.message) and update.callback_query:
        update_callback_answer_with_keyboard(update=update, context=context, text=text, keyboard=keyboard)
    else:
        update.message.reply_text(text=text, parse_mode=telegram.ParseMode.HTML, reply_markup=keyboard)

    clear_long_operation_flag(context=context)
    return START_EDIT_POSITIONS


def show_menu_districts_settings(update: Update, context: CallbackContext):
    logger.info("districts_settings")
    chat_id = update.effective_chat.id

    districts = context.user_data[DISTRICTS]
    logger.info(f"districts_settings, districts = {districts}")

    config_parser = get_config_parser(chat_id)

    buttons = []
    is_all_checked = True
    is_all_unchecked = True
    for default_district in DEFAULT_DISTRICTS:
        is_checked = config_parser.check_default_district_in_settings(default_district, districts)
        mark = get_mark_icon(is_checked)
        if is_checked:
            is_all_unchecked = False
        else:
            is_all_checked = False

        clear_district_name = default_district.replace(" район", "").title()
        text = f"        {mark} {clear_district_name}"
        buttons.append([InlineKeyboardButton(text=text,
                                             callback_data=str(SET_DISTRICTS_CHECK) + "_" + clear_district_name)])

    if not is_all_checked and not is_all_unchecked:
        buttons.append(
            [
                InlineKeyboardButton(text=f"{SELECT_ALL_ICON} {SELECT_ALL_ICON} {TEXT_SELECT_ALL}",
                                     callback_data=str(CHECK_ALL_DISTRICTS)),
                InlineKeyboardButton(text=f"{UNSELECT_ALL_ICON} {UNSELECT_ALL_ICON} {TEXT_UNSELECT_ALL}",
                                     callback_data=str(UNCHECK_ALL_DISTRICTS))
            ]
        )
    else:
        if not is_all_checked:
            buttons.append(
                [
                    InlineKeyboardButton(text=f"{SELECT_ALL_ICON} {SELECT_ALL_ICON} {TEXT_SELECT_ALL}",
                                         callback_data=str(CHECK_ALL_DISTRICTS))
                ]
            )
        if not is_all_unchecked:
            buttons.append(
                [
                    InlineKeyboardButton(text=f"{UNSELECT_ALL_ICON} {UNSELECT_ALL_ICON} {TEXT_UNSELECT_ALL}",
                                         callback_data=str(UNCHECK_ALL_DISTRICTS))
                ]
            )

    buttons.append([InlineKeyboardButton(text=f"{SAVE_ICON} {TEXT_SAVE}", callback_data=str(SAVE_DISTRICTS_SETTINGS)),
                    get_back_button()])

    keyboard = InlineKeyboardMarkup(buttons)

    text = "Выберите районы для проверки"
    if ((context.user_data and context.user_data.get(START_OVER)) or not update.message) and update.callback_query:
        update_callback_answer_with_keyboard(update=update, context=context, text=text, keyboard=keyboard)
    else:
        update.message.reply_text(text=text, parse_mode=telegram.ParseMode.HTML, reply_markup=keyboard)

    clear_long_operation_flag(context=context)
    return START_EDIT_DISTRICTS


def delete_messages(update: Update, context: CallbackContext):
    if context.user_data.get(MESSAGES_FOR_REMOVE):
        chat_id = update.effective_chat.id
        messages = context.user_data.get(MESSAGES_FOR_REMOVE)
        if isinstance(messages, list):
            for message in context.user_data.get(MESSAGES_FOR_REMOVE):
                context.bot.delete_message(chat_id=str(chat_id), message_id=message.message_id)
        else:
            context.bot.delete_message(chat_id=str(chat_id), message_id=messages.message_id)
        context.user_data[MESSAGES_FOR_REMOVE] = []


def show_menu_benefits_settings(update: Update, context: CallbackContext):
    logger.info("show_menu_benefits_settings")
    benefit_federal = context.user_data[BENEFIT_FEDERAL]

    text_for_menu = TEXT_MENU_BENEFITS_SETTINGS

    if benefit_federal:
        mark_federal = CHECKED_RADIO_BUTTON_ICON
        mark_regional = EMPTY_RADIO_BUTTON_ICON
    else:
        mark_federal = EMPTY_RADIO_BUTTON_ICON
        mark_regional = CHECKED_RADIO_BUTTON_ICON

    buttons = [
        [
            InlineKeyboardButton(text=f"{mark_federal} {TEXT_BENEFIT_FEDERAL}",
                                 callback_data=str(SET_BENEFIT_FEDERAL_CHECK)),
        ],
        [
            InlineKeyboardButton(text=f"{mark_regional} {TEXT_BENEFIT_REGIONAL}",
                                 callback_data=str(SET_BENEFIT_REGIONAL_CHECK))
        ],
        [
            InlineKeyboardButton(text=f"{SAVE_ICON} {TEXT_SAVE}", callback_data=str(SAVE_BENEFITS_SETTINGS)),
            get_back_button(),
        ],
    ]
    keyboard = InlineKeyboardMarkup(buttons)

    if ((context.user_data and context.user_data.get(START_OVER)) or not update.message) and update.callback_query:
        update_callback_answer_with_keyboard(update=update, context=context, text=text_for_menu, keyboard=keyboard)
    else:
        update.message.reply_text(text_for_menu, reply_markup=keyboard)

    clear_long_operation_flag(context=context)

    return START_EDIT_BENEFITS_SETTINGS


def show_menu_schedule_settings(update: Update, context: CallbackContext):
    logger.info(f"show_menu_schedule_settings")
    schedule_days = context.user_data[SCHEDULE_DAYS]
    schedule_hours = context.user_data[SCHEDULE_HOURS]
    email = context.user_data[EMAIL]
    email_send = context.user_data[SEND_EMAIL]

    mark_email = get_mark_icon(email_send)

    is_hours_and_days_set = is_shedule_on(schedule_hours) and is_shedule_on(schedule_days)

    buttons = [
        [
            InlineKeyboardButton(text=f"{EMAIL_ICON} {TEXT_CHANGE_EMAIL}", callback_data=str(START_EDIT_REPORTS_EMAIL)),
        ],
        [
            InlineKeyboardButton(text=f"{mark_email} {TEXT_SENDING_EMAIL}?",
                                 callback_data=str(SET_REPORTS_SEND_EMAIL_CHECK))
        ],
        [
            InlineKeyboardButton(text=f"{SCHEDULE_MENU_CHANGE_DAYS_ICON} {TEXT_MENU_SETTINGS_DAYS}",
                                 callback_data=str(SHOW_MENU_SCHEDULE_DAYS_SETTINGS)),
        ],
        [
            InlineKeyboardButton(text=f"{SCHEDULE_MENU_CHANGE_HOURS_ICON} {TEXT_MENU_SETTINGS_HOURS}",
                                 callback_data=str(SHOW_MENU_SCHEDULE_HOURS_SETTINGS)),
        ],
        [
            InlineKeyboardButton(text=f"{SAVE_ICON} {TEXT_SAVE}", callback_data=str(SAVE_SCHEDULE_SETTINGS)),
            get_back_button(),
        ],
    ]
    keyboard = InlineKeyboardMarkup(buttons)

    text_for_menu = f"<b>{TEXT_SETTINGS_SCHEDULE} настроено так:</b>\n{schedule_to_string(schedule_days=schedule_days, schedule_hours=schedule_hours, email_send=email_send, emails=email)}"
    if not is_hours_and_days_set:
        text_for_menu += f"<i>{TEXT_INFO_MUST_SET_SCHEDULE_SETTINGS}</i>\n\n"
    text_for_menu = TEXT_MENU_REPORTS

    if email:
        text_for_menu += f"{TEXT_EMAIL}: {email}\n"
    else:
        text_for_menu += f"Сейчас e-mail не задан\n"

    if ((context.user_data and context.user_data.get(START_OVER)) or not update.message) and update.callback_query:
        update_callback_answer_with_keyboard(update=update, context=context, text=text_for_menu, keyboard=keyboard)
    else:
        update.message.reply_text(text=text_for_menu, reply_markup=keyboard)

    clear_long_operation_flag(context=context)
    context.user_data[START_OVER] = False

    return START_EDIT_SCHEDULE


def set_schedule_enable_every_hour_check(update: Update, context: CallbackContext) -> int:
    logger.info("set_schedule_enable_every_hour_check")
    if is_long_operation_flag(context):
        return START_EDIT_SCHEDULE
    else:
        set_long_operation_flag(context)
    context.user_data[SCHEDULE_CHECK] = False
    return save_all_settings(update=update, context=context)


def set_schedule_enable_schedule_check(update: Update, context: CallbackContext) -> int:
    logger.info("set_schedule_enable_schedule_check")
    if is_long_operation_flag(context):
        return START_EDIT_SCHEDULE
    else:
        set_long_operation_flag(context)
    context.user_data[SCHEDULE_CHECK] = True
    return save_all_settings(update=update, context=context)


def start_edit_every_hour_schedule(update: Update, context: CallbackContext):
    logger.info("start_edit_every_hour_schedule")

    schedule = context.user_data[SCHEDULE_HOURS]

    buttons = [
        add_one_line_in_schedule_hours(schedule=schedule, selected_range=range(3)),
        add_one_line_in_schedule_hours(schedule=schedule, selected_range=range(3, 6)),
        add_one_line_in_schedule_hours(schedule=schedule, selected_range=range(6, 9)),
        add_one_line_in_schedule_hours(schedule=schedule, selected_range=range(9, 12)),
        add_one_line_in_schedule_hours(schedule=schedule, selected_range=range(12, 15)),
        add_one_line_in_schedule_hours(schedule=schedule, selected_range=range(15, 18)),
        add_one_line_in_schedule_hours(schedule=schedule, selected_range=range(18, 21)),
        add_one_line_in_schedule_hours(schedule=schedule, selected_range=range(21, 24))
    ]

    if is_shedule_off(schedule):
        buttons.append(
            [
                InlineKeyboardButton(text=f"{SELECT_ALL_ICON} {SELECT_ALL_ICON} {TEXT_SELECT_ALL}",
                                     callback_data=str(CHECK_ALL_SCHEDULE_HOURS))
            ])
    else:
        numbered_array = [int(i) for i in schedule]
        numbered_array.sort()
        if numbered_array != EVERY_HOUR_SCHEDULE:
            buttons.append(
                [
                    InlineKeyboardButton(text=f"{SELECT_ALL_ICON} {SELECT_ALL_ICON} {TEXT_SELECT_ALL}",
                                         callback_data=str(CHECK_ALL_SCHEDULE_HOURS)),
                    InlineKeyboardButton(text=f"{UNSELECT_ALL_ICON} {UNSELECT_ALL_ICON} {TEXT_UNSELECT_ALL}",
                                         callback_data=str(UNCHECK_ALL_SCHEDULE_HOURS))
                ]
            )
        else:
            buttons.append(
                [
                    InlineKeyboardButton(text=f"{UNSELECT_ALL_ICON} {UNSELECT_ALL_ICON} {TEXT_UNSELECT_ALL}",
                                         callback_data=str(UNCHECK_ALL_SCHEDULE_HOURS))
                ])

    buttons.append([get_back_button()])

    keyboard = InlineKeyboardMarkup(buttons)

    if ((context.user_data and context.user_data.get(START_OVER)) or not update.message) and update.callback_query:
        update_callback_answer_with_keyboard(update=update, context=context, text=TEXT_CHECK_HOURS, keyboard=keyboard)
    else:
        update.message.reply_text(text=TEXT_CHECK_HOURS, parse_mode=telegram.ParseMode.HTML, reply_markup=keyboard)

    clear_long_operation_flag(context=context)
    return TYPING_FOR_CHECK_SCHEDULE_HOURS


def start_edit_every_day_schedule(update: Update, context: CallbackContext):
    logger.info("start_edit_every_day_schedule")

    schedule = context.user_data[SCHEDULE_DAYS]

    buttons = get_days_in_schedule(schedule_days=schedule)
    if is_shedule_off(schedule):
        buttons.append(
            [
                InlineKeyboardButton(text=f"{SELECT_ALL_ICON} {SELECT_ALL_ICON} {TEXT_SELECT_ALL}",
                                     callback_data=str(CHECK_ALL_SCHEDULE_DAYS))
            ])
    else:
        numbered_array = [int(i) for i in schedule]
        numbered_array.sort()
        if numbered_array != EVERY_DAY_SCHEDULE:
            buttons.append(
                [
                    InlineKeyboardButton(text=f"{SELECT_ALL_ICON} {SELECT_ALL_ICON} {TEXT_SELECT_ALL}",
                                         callback_data=str(CHECK_ALL_SCHEDULE_DAYS)),
                    InlineKeyboardButton(text=f"{UNSELECT_ALL_ICON} {UNSELECT_ALL_ICON} {TEXT_UNSELECT_ALL}",
                                         callback_data=str(UNCHECK_ALL_SCHEDULE_DAYS))
                ]
            )
        else:
            buttons.append(
                [
                    InlineKeyboardButton(text=f"{UNSELECT_ALL_ICON} {UNSELECT_ALL_ICON} {TEXT_UNSELECT_ALL}",
                                         callback_data=str(UNCHECK_ALL_SCHEDULE_DAYS))
                ])

    buttons.append([get_back_button()])

    keyboard = InlineKeyboardMarkup(buttons)

    if ((context.user_data and context.user_data.get(START_OVER)) or not update.message) and update.callback_query:
        update_callback_answer_with_keyboard(update=update, context=context, text=TEXT_CHECK_DAYS, keyboard=keyboard)
    else:
        update.message.reply_text(text=TEXT_CHECK_DAYS, parse_mode=telegram.ParseMode.HTML, reply_markup=keyboard)

    clear_long_operation_flag(context=context)
    return TYPING_FOR_CHECK_SCHEDULE_DAYS


def show_current_settings(update: Update, context: CallbackContext):
    logger.info("show_settings")
    chat_id = update.effective_chat.id

    config_parser = get_config_parser(chat_id)
    positions, districts, emails, send_email, schedule_hours, schedule_days, schedule_check, benefit_federal = config_parser.get_values_from_config(
        chat_id)

    if len(positions):
        str_positions = ", ".join(positions)
        message_text = f"{POSITIONS_ICON} <b>{TEXT_POSITIONS}:</b>\n\n        {str_positions}\n\n"
    else:
        message_text = f"{POSITIONS_ICON} <b>{TEXT_POSITIONS}:</b> {TEXT_NOT_SET}ы\n\n"

    if len(districts):
        message_text += f"{DISTRICTS_ICON} <b>{TEXT_DISTRICTS}:</b>\n\n"
        for district in districts:
            message_text += f"        {district.capitalize()}\n\n"
    else:
        message_text = f"{POSITIONS_ICON} <b>{TEXT_POSITIONS}:</b> {TEXT_NOT_SET}ы\n\n"

    message_text += f"{SCHEDULE_ICON} <b>{TEXT_CHECK_TYPE}:</b> "
    if schedule_check:
        message_text += f"{TEXT_CHECK_TYPE_SCHEDULE}\n\n"
        message_text += schedule_to_string(schedule_days=schedule_days, schedule_hours=schedule_hours,
                                           email_send=send_email, emails=emails)
    else:
        message_text += f"{TEXT_CHECK_TYPE_EVERY_HOUR}\n\n"

    message_text += f"{BENEFITS_ICON} <b>{TEXT_BENEFITS}:</b>\n\n"
    message_text += "        {0} {1}\n\n".format(get_mark_icon(benefit_federal), TEXT_BENEFIT_FEDERAL)
    message_text += "        {0} {1}\n\n".format(get_mark_icon(not benefit_federal), TEXT_BENEFIT_REGIONAL)

    buttons = [[get_back_button()]]
    keyboard = InlineKeyboardMarkup(buttons)

    update_callback_answer_with_keyboard(update=update, context=context, text=message_text, keyboard=keyboard)

    clear_long_operation_flag(context=context)

    return SHOWING_SETTINGS


def check_for_empty_positions_or_districts(positions, districts, update, context):
    empty_positions = not positions or not len(positions) or not len(positions[0])
    empty_districts = not districts or not len(districts) or not len(districts[0])
    if empty_positions or empty_districts:
        buttons = [[get_restart_check_button(), get_back_button()]]
        keyboard = InlineKeyboardMarkup(buttons)
        if empty_positions and empty_districts:
            text = TEXT_EMPTY_POSITIONS_AND_DISTRICTS
        elif empty_districts:
            text = TEXT_EMPTY_DISTRICTS
        else:
            text = TEXT_EMPTY_POSITIONS
        update_callback_answer_with_keyboard(update=update, context=context, text=text, keyboard=keyboard)
        return True
    return False


def check(update: Update, context: CallbackContext) -> int:
    try:
        logger.info(f"check, is_long_operation_flag = {is_long_operation_flag(context)}")

        global global_chat_id
        global_chat_id = update.effective_chat.id

        if is_long_operation_flag(context):
            return SHOWING
        else:
            set_long_operation_flag(context)

        bot = context.bot
        chat_id = update.callback_query.message.chat.id
        now = datetime.now()

        update.callback_query.answer()
        bot.send_chat_action(chat_id=chat_id, action=telegram.ChatAction.TYPING)

        logger.info(f"check, start get_values_from_config")

        config_parser = get_config_parser(chat_id)
        positions, districts, emails, send_email, schedule_hours, schedule_days, schedule_check, benefit_federal = config_parser.get_values_from_config(
            chat_id)
        if check_for_empty_positions_or_districts(positions=positions, districts=districts, update=update,
                                                  context=context):
            return SHOWING

        logger.info(f"check, get_values_from_config")

        email_string = ""
        if emails and len(emails) and emails[0] and send_email and schedule_check:
            email_string = f"{TEXT_SEND_TO_EMAIL} {emails[0]}\n\n"

        districts_string = "\n    ".join(districts).title()
        table = ""
        result_array = []

        if benefit_federal:
            text_benefit = TEXT_BENEFIT_FEDERAL_CHECK
        else:
            text_benefit = TEXT_BENEFIT_REGIONAL_CHECK

        logger.info(f"check, start for position in positions")
        html_parser = DiabetHtmlReportParser(chat_id)
        for position in positions:
            update.callback_query.edit_message_text(
                text=f"{TEXT_RECEIVING_DATA} {text_benefit} {TEXT_RECEIVING_DISTRICTS}\n    {districts_string}\n\n{email_string}Ищу {position}")

            logger.info(f"check, before get_table_for_one_position")
            table_res, map_diff = html_parser.get_table_for_one_position(position, districts, benefit_federal)
            logger.info(f"check, after get_table_for_one_position")
            if table_res:
                table += table_res
            if map_diff:
                result_array.append(map_diff)

        if send_email:
            bot.send_chat_action(chat_id=chat_id, action=telegram.ChatAction.UPLOAD_DOCUMENT)
            report_sender = DiabetHtmlReportSender(now, chat_id)

            full_report_file, full_report_file_path = report_sender.write_report(time_now=now, html_table=table)

            report_sender.send_emails(emails=emails, new_table=table)
            remove_reports(full_report_file=full_report_file, full_report_file_path=full_report_file_path)
        logger.info(f"check, finish for position in positions, after send_email")

        buttons = [[get_restart_check_button(), get_back_button()]]
        keyboard = InlineKeyboardMarkup(buttons)

        logger.info(
            f"check, finish for position in positions, before create_text_by_result_array. result_array = {result_array}")
        str_array_result = create_text_by_result_array(result_array)
        logger.info(f"check, finish for position in positions, after create_text_by_result_array")

        logger.info(f"check, finish for position in positions, before get_text_for_results")
        results_text = get_text_for_results(table=table, str_array_result=str_array_result,
                                            emails=emails, send_email=send_email, benefit_federal=benefit_federal,
                                            schedule_check=schedule_check)
        logger.info(f"check, finish for position in positions, after get_text_for_results")

        logger.info(f"check, finish for position in positions, before update_callback_answer_with_keyboard")
        update_callback_answer_with_keyboard(update=update, context=context, text=results_text, keyboard=keyboard)
        logger.info(f"check, finish for position in positions, after update_callback_answer_with_keyboard")

        set_start_over_flag(context, True)

        clear_long_operation_flag(context=context)
    except Exception as e:
        print(f"error = {e}")
    return SHOWING


def feedback(update: Update, context: CallbackContext) -> int:
    try:
        logger.info(f"feedback, is_long_operation_flag = {is_long_operation_flag(context)}")

        global global_chat_id
        global_chat_id = update.effective_chat.id

        if is_long_operation_flag(context):
            return SHOWING
        else:
            set_long_operation_flag(context)

        delete_messages(update=update, context=context)
        user_data = context.user_data
        user_data[MESSAGES_FOR_REMOVE] = update_callback_answer(update=update, context=context,
                                                                text=TEXT_INPUT_FEEDBACK)

        return TYPING_FOR_FEEDBACK

    except Exception as e:
        print(f"error = {e}")
    return SHOWING


def check_periodic(context: CallbackContext):
    try:
        bot = context.bot
        context.refresh_data()

        now = datetime.now()
        day_of_week = now.today().weekday()

        config_parser = get_config_parser(global_chat_id)
        positions, districts, emails, send_email, schedule_hours, schedule_days, schedule_check, benefit_federal = config_parser.get_values_from_config(
            global_chat_id)

        logger.info(
            f"check_periodic, global_chat_id = {global_chat_id}, day_of_week = {day_of_week}, current_hour = {now.hour}, schedule_check={schedule_check}, positions = {positions}")

        if not positions or not len(positions) or not len(positions[0]):
            logger.info(f"check_periodic, global_chat_id = {global_chat_id}, positions empty, exit")
            return

        is_find_day = check_value_in_schedule(schedule=schedule_days, value=day_of_week)
        is_find_hour = check_value_in_schedule(schedule=schedule_hours, value=now.hour)

        if schedule_check and (not is_find_day or not is_find_hour):
            logger.info(
                f"check_periodic, global_chat_id = {global_chat_id}, schedule_check False, is_find_day = {is_find_day}, is_find_hour = {is_find_hour}, exit")
            return

        html_parser = DiabetHtmlReportParser(global_chat_id)

        table, result_array = html_parser.get_tables_from_html_positions(positions=positions,
                                                                         districts=districts,
                                                                         benefit_federal=benefit_federal)

        if schedule_check:
            report_sender = DiabetHtmlReportSender(now, global_chat_id)
            full_report_file, full_report_file_path = report_sender.write_report(now, table)

            report_sender.send_emails(emails=emails, new_table=table)
            remove_reports(full_report_file=full_report_file, full_report_file_path=full_report_file_path)

        if result_array:
            str_array_result = create_text_by_result_array(result_array)
            results_text = get_text_for_results(table=table, str_array_result=str_array_result,
                                                emails=emails, send_email=send_email, benefit_federal=benefit_federal,
                                                schedule_check=schedule_check,
                                                for_periodical_check=True)

            bot.send_message(global_chat_id, text=results_text)

    except Exception as e:
        print(f"error = {e}")

    clear_long_operation_flag(context=context)

    return END


def stop(update: Update, context: CallbackContext) -> int:
    logger.info("stop")

    global global_chat_id
    global_chat_id = update.effective_chat.id

    clear_long_operation_flag(context=context)
    update.message.reply_text(TEXT_BYE)

    return END


def return_to_start(update: Update, context: CallbackContext) -> int:
    logger.info("return_to_start")
    set_start_over_flag(context, True)
    clear_long_operation_flag(context=context)
    start(update, context)

    return END


def stop_nested(update: Update, context: CallbackContext) -> int:
    logger.info("stop_nested")
    global global_chat_id
    global_chat_id = update.effective_chat.id

    clear_long_operation_flag(context=context)
    update.message.reply_text(TEXT_BYE)
    return STOPPING


def end_change_settings(update: Update, context: CallbackContext) -> int:
    logger.info("end_change_settings")
    return return_to_main_settings(update=update, context=context)


def end_change_schedule_hours(update: Update, context: CallbackContext) -> int:
    logger.info("end_change_schedule_hours")

    set_start_over_flag(context, True)
    show_menu_schedule_settings(update, context)

    return START_EDIT_SCHEDULE


def end_change_schedule_days(update: Update, context: CallbackContext) -> int:
    logger.info("end_change_schedule_days")

    set_start_over_flag(context, True)
    show_menu_schedule_settings(update, context)

    return START_EDIT_SCHEDULE


def save_positions_settings(update: Update, context: CallbackContext) -> int:
    logger.info("save_settings_positions")

    chat_id = update.callback_query.message.chat.id
    config_parser = get_config_parser(chat_id)
    config_parser.save_positions_to_config(chat_id, context.user_data[POSITIONS])

    return return_to_main_settings(update=update, context=context)


def save_all_settings(update: Update, context: CallbackContext) -> int:
    logger.info("save_all_settings")

    chat_id = update.callback_query.message.chat.id

    config_parser = get_config_parser(chat_id)
    config_parser.save_all_to_config(chat_id,
                                     config_positions=context.user_data[POSITIONS],
                                     config_districts=context.user_data[DISTRICTS],
                                     config_emails=context.user_data[EMAIL],
                                     config_send_email=context.user_data[SEND_EMAIL],
                                     config_schedule_hours=context.user_data[SCHEDULE_HOURS],
                                     config_schedule_days=context.user_data[SCHEDULE_DAYS],
                                     config_schedule_check=context.user_data[SCHEDULE_CHECK],
                                     config_benefit_federal=context.user_data[BENEFIT_FEDERAL])

    return return_to_showing_menu_main_settings(update=update, context=context)


def save_settings_schedule(update: Update, context: CallbackContext) -> int:
    if is_shedule_off(context.user_data[SCHEDULE_HOURS]) or is_shedule_off(context.user_data[SCHEDULE_DAYS]):
        schedule_check = False
    else:
        schedule_check = context.user_data[SCHEDULE_CHECK]

    logger.info(f"save_settings_schedule, context.user_data[SCHEDULE_CHECK] = {context.user_data[SCHEDULE_CHECK]}")

    chat_id = update.callback_query.message.chat.id
    config_parser = get_config_parser(chat_id)
    config_parser.save_schedule_to_config(config_suffix=chat_id, new_schedule_hours=context.user_data[SCHEDULE_HOURS],
                                          new_schedule_days=context.user_data[SCHEDULE_DAYS],
                                          new_schedule_check=schedule_check, new_email=context.user_data[EMAIL],
                                          new_send_email=context.user_data[SEND_EMAIL])

    return return_to_main_settings(update=update, context=context)


def return_to_main_settings(update: Update, context: CallbackContext) -> int:
    logger.info("return_to_main_settings")

    set_start_over_flag(context, True)
    show_menu_settings(update, context)

    return END


def set_district_check(update: Update, context: CallbackContext) -> int:
    logger.info("check_district")
    if is_long_operation_flag(context):
        return START_EDIT_DISTRICTS
    else:
        set_long_operation_flag(context)

    checking_district = update.callback_query.data.split("_", 1)[1]
    user_data = context.user_data
    set_long_operation_flag(context=context)

    current_districts = user_data[DISTRICTS]

    index_district = -1
    for index, current_district in enumerate(current_districts):
        if checking_district.lower() == get_district_name_for_compare(current_district):
            index_district = index
            break

    if index_district == -1:
        current_districts.append(checking_district)
    else:
        current_districts.pop(index_district)

    return set_districts_data(update=update, context=context, data_districts=current_districts)


def set_check_all_districts(update: Update, context: CallbackContext) -> int:
    logger.info("set_check_all_districts")
    if is_long_operation_flag(context):
        return START_EDIT_DISTRICTS
    else:
        set_long_operation_flag(context)
    return set_districts_data(update=update, context=context, data_districts=DEFAULT_DISTRICTS)


def set_uncheck_all_districts(update: Update, context: CallbackContext) -> int:
    logger.info("set_uncheck_all_districts")
    if is_long_operation_flag(context):
        return START_EDIT_DISTRICTS
    else:
        set_long_operation_flag(context)
    return set_districts_data(update=update, context=context, data_districts=[])


def set_districts_data(update: Update, context: CallbackContext, data_districts):
    context.user_data[DISTRICTS] = data_districts.copy()
    set_start_over_flag(context, True)
    show_menu_districts_settings(update, context)
    return START_EDIT_DISTRICTS


def set_reports_send_email_check(update: Update, context: CallbackContext) -> int:
    logger.info("set_reports_send_email_check")
    if is_long_operation_flag(context):
        return START_EDIT_DISTRICTS
    context.user_data[SEND_EMAIL] = not context.user_data[SEND_EMAIL]
    return show_menu_schedule_settings(update=update, context=context)


def set_benefit_federal_check(update: Update, context: CallbackContext) -> int:
    logger.info("set_benefit_federal_check")
    if is_long_operation_flag(context):
        return START_EDIT_ADDITIONAL_SETTINGS
    else:
        set_long_operation_flag(context)
    context.user_data[BENEFIT_FEDERAL] = True
    return return_to_showing_menu_benefits_settings(update=update, context=context)


def set_benefit_regional_check(update: Update, context: CallbackContext) -> int:
    logger.info("set_benefit_regional_check")
    if is_long_operation_flag(context):
        return START_EDIT_ADDITIONAL_SETTINGS
    else:
        set_long_operation_flag(context)
    context.user_data[BENEFIT_FEDERAL] = False
    return return_to_showing_menu_benefits_settings(update=update, context=context)


def save_benefits_settings(update: Update, context: CallbackContext) -> int:
    logger.info("save_benefits_settings")
    chat_id = update.callback_query.message.chat.id

    config_parser = get_config_parser(chat_id)
    config_parser.save_benefits_settings_to_config(config_suffix=chat_id,
                                                   new_benefit_federal=context.user_data[BENEFIT_FEDERAL])

    return return_to_main_settings(update=update, context=context)


def return_to_showing_menu_main_settings(update: Update, context: CallbackContext) -> int:
    set_start_over_flag(context, True)
    show_menu_settings(update, context)
    return SHOWING_SETTINGS


def return_to_showing_menu_benefits_settings(update: Update, context: CallbackContext) -> int:
    set_start_over_flag(context, True)
    show_menu_benefits_settings(update, context)
    return START_EDIT_BENEFITS_SETTINGS


def check_schedule_hour(update: Update, context: CallbackContext) -> int:
    logger.info("check_schedule_hour")

    checking_hour = int(update.callback_query.data.split("_", 1)[1])
    current_schedule = context.user_data[SCHEDULE_HOURS]

    index_hour = -1
    for index, current_hour in enumerate(current_schedule):
        if checking_hour == int(current_hour):
            index_hour = index
            break

    if index_hour == -1:
        current_schedule.append(int(checking_hour))
    else:
        current_schedule.pop(index_hour)

    current_schedule.sort()

    set_start_over_flag(context, True)
    start_edit_every_hour_schedule(update, context)

    return TYPING_FOR_CHECK_SCHEDULE_HOURS


def check_schedule_day(update: Update, context: CallbackContext) -> int:
    logger.info("check_schedule_day")

    checking_day = int(update.callback_query.data.split("_", 1)[1])
    current_schedule = context.user_data[SCHEDULE_DAYS]

    index_day = -1
    for index, current_hour in enumerate(current_schedule):
        if checking_day == int(current_hour):
            index_day = index
            break

    if index_day == -1:
        current_schedule.append(int(checking_day))
    else:
        current_schedule.pop(index_day)
    current_schedule.sort()

    set_start_over_flag(context, True)
    start_edit_every_day_schedule(update, context)

    return TYPING_FOR_CHECK_SCHEDULE_DAYS


def set_check_all_schedule_hours(update: Update, context: CallbackContext) -> int:
    logger.info("set_check_all_schedule_hours")
    if is_long_operation_flag(context):
        return START_EDIT_EVERY_HOUR_CHECK
    else:
        set_long_operation_flag(context)
    return set_schedule_hours_data(update=update, context=context, data_hours=EVERY_HOUR_SCHEDULE)


def set_uncheck_all_schedule_hours(update: Update, context: CallbackContext) -> int:
    logger.info("set_uncheck_all_schedule_hours")
    if is_long_operation_flag(context):
        return START_EDIT_EVERY_HOUR_CHECK
    else:
        set_long_operation_flag(context)
    return set_schedule_hours_data(update=update, context=context, data_hours=[])


def set_check_all_schedule_days(update: Update, context: CallbackContext) -> int:
    logger.info("set_check_all_schedule_days")
    if is_long_operation_flag(context):
        return START_EDIT_EVERY_DAY_CHECK
    else:
        set_long_operation_flag(context)
    return set_schedule_days_data(update=update, context=context, data_days=EVERY_DAY_SCHEDULE)


def set_uncheck_all_schedule_days(update: Update, context: CallbackContext) -> int:
    logger.info("set_uncheck_all_schedule_days")
    if is_long_operation_flag(context):
        return START_EDIT_EVERY_DAY_CHECK
    else:
        set_long_operation_flag(context)
    return set_schedule_days_data(update=update, context=context, data_days=[])


def set_schedule_every_one_day(update: Update, context: CallbackContext) -> int:
    logger.info("set_schedule_every_one_day")
    if is_long_operation_flag(context):
        return START_EDIT_EVERY_DAY_CHECK
    else:
        set_long_operation_flag(context)
    set_schedule_hours_data(update=update, context=context, data_hours=context.user_data[SCHEDULE_DAYS])
    return TYPING_FOR_CHECK_SCHEDULE_DAYS


def set_schedule_hours_data(update: Update, context: CallbackContext, data_hours):
    context.user_data[SCHEDULE_HOURS] = data_hours
    set_start_over_flag(context, True)
    start_edit_every_hour_schedule(update, context)
    return TYPING_FOR_CHECK_SCHEDULE_HOURS


def set_schedule_days_data(update: Update, context: CallbackContext, data_days):
    context.user_data[SCHEDULE_DAYS] = data_days
    set_start_over_flag(context, True)
    start_edit_every_day_schedule(update, context)
    return TYPING_FOR_CHECK_SCHEDULE_DAYS


def save_districts_settings(update: Update, context: CallbackContext) -> int:
    logger.info("save_settings_districts")

    chat_id = update.callback_query.message.chat.id

    config_parser = get_config_parser(chat_id)
    config_parser.save_districts_to_config(chat_id, context.user_data[DISTRICTS])

    set_start_over_flag(context, True)
    show_menu_settings(update, context)

    return END


def main():
    global global_heroku_run
    is_local_run = "local" in os.environ.get("BOT-TYPE-RUN", "local")
    if is_local_run:
        from credentials import bot_token, bot_user_name
        updater = Updater(token=bot_token, use_context=True)
        bot_webhook_port = 8443
    else:
        global_heroku_run = True
        bot_token = os.environ.get("BOT-TOKEN")
        bot_user_name = os.environ.get("BOT-USER-NAME")
        bot_webhook_port = int(os.environ.get("PORT", '8443'))
        logger.info(f"run bot, port = {bot_webhook_port}, bot_user_name={bot_user_name}, bot_token = {bot_token}")
        updater = Updater(token=bot_token, use_context=True)

    dp = updater.dispatcher

    def stop_and_restart():
        updater.stop()
        os.execl(sys.executable, sys.executable, *sys.argv)

    def restart(update, _):
        update.message.reply_text('Bot is restarting...')
        Thread(target=stop_and_restart).start()

    dp.add_handler(CommandHandler('r', restart, filters=Filters.user(username=bot_user_name)))

    positions_settings_conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(show_menu_positions_settings, pattern='^' + str(SHOW_MENU_POSITIONS_SETTINGS) + '$')],
        states={
            START_EDIT_POSITIONS: [
                CallbackQueryHandler(start_edit_positions_add, pattern='^' + str(START_EDIT_POSITIONS_ADD) + '$'),
                CallbackQueryHandler(start_edit_positions_remove,
                                     pattern='^' + str(START_EDIT_POSITIONS_REMOVE) + '$'),
                CallbackQueryHandler(save_positions_settings, pattern='^' + str(SAVE_POSITIONS_SETTINGS) + '$'),
                CallbackQueryHandler(end_change_settings, pattern='^' + str(END) + '$'),
                MessageHandler(Filters.text & ~Filters.command, save_add_positions_input),
                CallbackQueryHandler(start, pattern='^' + str(RUN_START) + '$')
            ],
            TYPING_FOR_ADD_POSITIONS: [MessageHandler(Filters.text & ~Filters.command, save_add_positions_input),
                                       CallbackQueryHandler(end_change_settings, pattern='^' + str(END) + '$'),
                                       CallbackQueryHandler(start, pattern='^' + str(RUN_START) + '$')],
            TYPING_FOR_REMOVE_POSITIONS: [MessageHandler(Filters.text & ~Filters.command, save_remove_positions_input),
                                          CallbackQueryHandler(end_change_settings, pattern='^' + str(END) + '$'),
                                          CallbackQueryHandler(start, pattern='^' + str(RUN_START) + '$')]
        },
        fallbacks=[
            CallbackQueryHandler(return_to_main_settings, pattern='^' + str(END) + '$'),
            CommandHandler('stop', stop_nested),
        ],
        map_to_parent={
            END: SHOWING_SETTINGS,
            STOPPING: STOPPING,
        }
    )

    districts_settings_conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(show_menu_districts_settings, pattern='^' + str(SHOW_MENU_DISTRICTS_SETTINGS) + '$')],
        states={
            START_EDIT_DISTRICTS: [
                CallbackQueryHandler(set_district_check, pattern='^' + str(SET_DISTRICTS_CHECK)),
                CallbackQueryHandler(set_check_all_districts,
                                     pattern='^' + str(CHECK_ALL_DISTRICTS) + '$'),
                CallbackQueryHandler(set_uncheck_all_districts,
                                     pattern='^' + str(UNCHECK_ALL_DISTRICTS) + '$'),
                CallbackQueryHandler(save_districts_settings, pattern='^' + str(SAVE_DISTRICTS_SETTINGS) + '$'),
                CallbackQueryHandler(end_change_settings, pattern='^' + str(END) + '$'),
                CallbackQueryHandler(start, pattern='^' + str(RUN_START) + '$')
            ]
        },
        fallbacks=[
            CallbackQueryHandler(return_to_main_settings, pattern='^' + str(END) + '$'),
            CommandHandler('stop', stop_nested),
        ],
        map_to_parent={
            END: SHOWING_SETTINGS,
            STOPPING: STOPPING,
        }
    )

    benefits_settings_conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(show_menu_benefits_settings,
                                 pattern='^' + str(SHOW_MENU_BENEFITS_SETTINGS) + '$')],
        states={
            START_EDIT_BENEFITS_SETTINGS: [
                CallbackQueryHandler(set_benefit_federal_check,
                                     pattern='^' + str(SET_BENEFIT_FEDERAL_CHECK) + '$'),
                CallbackQueryHandler(set_benefit_regional_check,
                                     pattern='^' + str(SET_BENEFIT_REGIONAL_CHECK) + '$'),
                CallbackQueryHandler(save_benefits_settings, pattern='^' + str(SAVE_BENEFITS_SETTINGS) + '$'),
                CallbackQueryHandler(end_change_settings, pattern='^' + str(END) + '$'),
                CallbackQueryHandler(start, pattern='^' + str(RUN_START) + '$')
            ]
        },
        fallbacks=[
            CallbackQueryHandler(return_to_main_settings, pattern='^' + str(END) + '$'),
            CommandHandler('stop', stop_nested),
        ],
        map_to_parent={
            END: SHOWING_SETTINGS,
            STOPPING: STOPPING,
        }
    )

    schedule_settings_conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(show_menu_schedule_settings, pattern='^' + str(SHOW_MENU_SCHEDULE_SETTINGS) + '$')],
        states={
            START_EDIT_SCHEDULE: [
                CallbackQueryHandler(start_edit_reports_email, pattern='^' + str(START_EDIT_REPORTS_EMAIL) + '$'),
                CallbackQueryHandler(set_reports_send_email_check, pattern='^' + str(SET_REPORTS_SEND_EMAIL_CHECK)),
                CallbackQueryHandler(start_edit_every_hour_schedule,
                                     pattern='^' + str(SHOW_MENU_SCHEDULE_HOURS_SETTINGS)),
                CallbackQueryHandler(start_edit_every_day_schedule,
                                     pattern='^' + str(SHOW_MENU_SCHEDULE_DAYS_SETTINGS)),
                CallbackQueryHandler(save_settings_schedule, pattern='^' + str(SAVE_SCHEDULE_SETTINGS) + '$'),
                CallbackQueryHandler(end_change_settings, pattern='^' + str(END) + '$'),
                CallbackQueryHandler(start, pattern='^' + str(RUN_START) + '$')
            ],
            TYPING_FOR_SET_EMAIL: [MessageHandler(Filters.text & ~Filters.command, save_email_input),
                                   CallbackQueryHandler(end_change_settings, pattern='^' + str(END) + '$'),
                                   CallbackQueryHandler(start, pattern='^' + str(RUN_START) + '$')],
            TYPING_FOR_CHECK_SCHEDULE_HOURS: [
                CallbackQueryHandler(check_schedule_hour, pattern='^' + str(CHECK_SCHEDULE_HOUR)),
                CallbackQueryHandler(set_check_all_schedule_hours,
                                     pattern='^' + str(CHECK_ALL_SCHEDULE_HOURS) + '$'),
                CallbackQueryHandler(set_uncheck_all_schedule_hours,
                                     pattern='^' + str(UNCHECK_ALL_SCHEDULE_HOURS) + '$'),
                CallbackQueryHandler(end_change_schedule_hours, pattern='^' + str(END) + '$'),
                CallbackQueryHandler(start, pattern='^' + str(RUN_START) + '$')
            ],
            TYPING_FOR_CHECK_SCHEDULE_DAYS: [
                CallbackQueryHandler(check_schedule_day, pattern='^' + str(CHECK_SCHEDULE_DAY)),
                CallbackQueryHandler(set_schedule_every_one_day,
                                     pattern='^' + str(SET_SCHEDULE_EVERY_DAY_CHECK) + '$'),
                CallbackQueryHandler(set_check_all_schedule_days,
                                     pattern='^' + str(CHECK_ALL_SCHEDULE_DAYS) + '$'),
                CallbackQueryHandler(set_uncheck_all_schedule_days,
                                     pattern='^' + str(UNCHECK_ALL_SCHEDULE_DAYS) + '$'),
                CallbackQueryHandler(end_change_schedule_days, pattern='^' + str(END) + '$'),
                CallbackQueryHandler(start, pattern='^' + str(RUN_START) + '$')
            ]
        },
        fallbacks=[
            CallbackQueryHandler(return_to_main_settings, pattern='^' + str(END) + '$'),
            CommandHandler('stop', stop_nested),
        ],
        map_to_parent={
            END: SHOWING_SETTINGS,
            STOPPING: STOPPING,
        }
    )

    show_settings_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(show_current_settings, pattern='^' + str(SHOW_CURRENT_SETTINGS) + '$')],
        states={
            RUN_MENU_SETTINGS: [
                CallbackQueryHandler(show_menu_settings, pattern='^' + str(SHOW_MENU_MAIN_SETTINGS) + '$'),
                CallbackQueryHandler(start, pattern='^' + str(RUN_START) + '$')],
            SHOWING_SETTINGS: [CallbackQueryHandler(return_to_main_settings, pattern='^' + str(END) + '$'),
                               CallbackQueryHandler(start, pattern='^' + str(RUN_START) + '$')]
        },
        fallbacks=[
            CallbackQueryHandler(return_to_main_settings, pattern='^' + str(END) + '$'),
            CommandHandler('stop', stop_nested),
        ],
        map_to_parent={
            END: SHOWING_SETTINGS,
            STOPPING: STOPPING,
        }
    )

    main_menu_settings_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(show_menu_settings, pattern='^' + str(SHOW_MENU_MAIN_SETTINGS) + '$'),
                      CallbackQueryHandler(start, pattern='^' + str(RUN_START) + '$')],
        states={
            SHOWING_SETTINGS: [
                CallbackQueryHandler(show_menu_settings, pattern='^' + str(SHOW_MENU_MAIN_SETTINGS) + '$'),
                CallbackQueryHandler(set_schedule_enable_every_hour_check,
                                     pattern='^' + str(SET_SCHEDULE_ENABLE_EVERY_HOUR_CHECK) + '$'),
                CallbackQueryHandler(set_schedule_enable_schedule_check,
                                     pattern='^' + str(SET_SCHEDULE_ENABLE_SCHEDULE_CHECK) + '$'),
                positions_settings_conv,
                districts_settings_conv,
                benefits_settings_conv,
                schedule_settings_conv,
                show_settings_conv,
                CallbackQueryHandler(start, pattern='^' + str(RUN_START) + '$')],
            RUN_MENU_SETTINGS: [
                CallbackQueryHandler(set_schedule_enable_every_hour_check,
                                     pattern='^' + str(SET_SCHEDULE_ENABLE_EVERY_HOUR_CHECK) + '$'),
                CallbackQueryHandler(set_schedule_enable_schedule_check,
                                     pattern='^' + str(SET_SCHEDULE_ENABLE_SCHEDULE_CHECK) + '$'),
                positions_settings_conv,
                districts_settings_conv,
                benefits_settings_conv,
                schedule_settings_conv,
                show_settings_conv,
                CallbackQueryHandler(start, pattern='^' + str(RUN_START) + '$')
            ]
        },
        fallbacks=[
            CallbackQueryHandler(start, pattern='^' + str(RUN_START) + '$'),
            CallbackQueryHandler(return_to_start, pattern='^' + str(END) + '$'),
            CommandHandler('stop', stop_nested),
        ],
        map_to_parent={
            END: SELECTING_ACTION,
            STOPPING: END,
        }
    )

    run_check_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(check, pattern='^' + str(RUN_CHECK) + '$')],
        states={
            SHOWING: [CallbackQueryHandler(start, pattern='^' + str(RUN_START) + '$'),
                      CallbackQueryHandler(check, pattern='^' + str(RUN_CHECK) + '$'),
                      CallbackQueryHandler(return_to_start, pattern='^' + str(END) + '$')]
        },
        fallbacks=[
            CallbackQueryHandler(start, pattern='^' + str(RUN_START) + '$'),
            CallbackQueryHandler(return_to_start, pattern='^' + str(END) + '$'),
            CommandHandler('stop', stop_nested),
        ],
        map_to_parent={
            END: SELECTING_ACTION,
            STOPPING: END,
        }
    )

    run_feedback_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(feedback, pattern='^' + str(RUN_GET_FEEDBACK) + '$')],
        states={
            TYPING_FOR_FEEDBACK: [MessageHandler(Filters.text & ~Filters.command, send_feedback),
                                  CallbackQueryHandler(return_to_start, pattern='^' + str(END) + '$'),
                                  CallbackQueryHandler(start, pattern='^' + str(RUN_START) + '$')],
        },
        fallbacks=[
            CallbackQueryHandler(start, pattern='^' + str(RUN_START) + '$'),
            CallbackQueryHandler(return_to_start, pattern='^' + str(END) + '$'),
            CommandHandler('stop', stop_nested),
        ],
        map_to_parent={
            END: SELECTING_ACTION,
            STOPPING: END,
        }
    )

    selection_handlers = [
        run_check_conv,
        main_menu_settings_conv,
        run_feedback_conv
    ]
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            SELECTING_ACTION: selection_handlers,
            STOPPING: [CommandHandler('start', start)],
            SHOWING: selection_handlers
        },
        fallbacks=[CommandHandler('stop', stop), CommandHandler('start', start)],
    )

    dp.add_handler(conv_handler)

    j = updater.job_queue
    for hour in range(24):
        time = datetime.now().replace(hour=hour, minute=0, second=0).time()
        j.run_daily(check_periodic, time=time)

    if is_local_run:
        updater.start_polling()
    else:
        updater.start_webhook(listen="0.0.0.0",
                              port=bot_webhook_port,
                              url_path=bot_token,
                              webhook_url='https://diabet-scaner.herokuapp.com/' + bot_token)
    updater.idle()


if __name__ == '__main__':
    main()
