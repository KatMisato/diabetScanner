import logging

from telegram.ext import Updater, CommandHandler, Filters, MessageHandler, CallbackQueryHandler
from telegram import ChatAction, InlineKeyboardMarkup

from threading import Thread
from functools import wraps
from datetime import datetime

from Utils import *
from base.DiabetHtmlReportParser import DiabetHtmlReportParser
from base.DiabetHtmlReportSender import DiabetHtmlReportSender

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

global_chat_id = 0

BOT_USER_NAME = os.environ.get('BOT-USER-NAME', "")


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


def start_edit_positions_add(update: Update, _) -> int:
    logger.info("start_edit_positions_add")
    update_callback_answer(update=update, text=TEXT_ADD_POSITION)
    return TYPING_FOR_ADD_POSITIONS


def start_edit_positions_remove(update: Update, _) -> int:
    logger.info("start_edit_positions_remove")
    update_callback_answer(update=update, text=TEXT_REMOVE_POSITION)
    return TYPING_FOR_REMOVE_POSITIONS


def start_edit_reports_email(update: Update, _) -> int:
    logger.info("start_edit_reports_email")
    update_callback_answer(update=update, text=TEXT_INPUT_EMAIL)
    return TYPING_FOR_SET_EMAIL


def save_add_positions_input(update: Update, context: CallbackContext) -> int:
    logger.info("save_add_positions_input")
    user_data = context.user_data

    user_data[POSITIONS] += clear_list_for_edit(update.message.text)
    user_data[START_OVER] = True

    return show_menu_positions_settings(update, context)


def save_remove_positions_input(update: Update, context: CallbackContext) -> int:
    logger.info("save_remove_positions_input")
    user_data = context.user_data

    list_for_removing = clear_list_for_edit(update.message.text)

    for position_removing in list_for_removing:
        if position_removing in user_data[POSITIONS]:
            user_data[POSITIONS].remove(position_removing)

    user_data[START_OVER] = True
    return show_menu_positions_settings(update, context)


def save_email_input(update: Update, context: CallbackContext) -> int:
    logger.info("save_email_input")
    user_data = context.user_data
    user_data[EMAIL] = update.message.text
    return show_menu_reports_settings(update, context)


def start(update: Update, context: CallbackContext):
    logger.info("start")
    global global_chat_id
    global_chat_id = update.effective_chat.id

    buttons = [
        [
            InlineKeyboardButton(text=f"{RUN_CHECK_ICON} {TEXT_RUN_CHECK}", callback_data=str(RUN_CHECK)),
        ],
        [
            InlineKeyboardButton(text=f"{SETTINGS_ICON} {TEXT_SETTINGS}", callback_data=str(SHOW_MENU_MAIN_SETTINGS)),
        ],
    ]
    keyboard = InlineKeyboardMarkup(buttons)

    if context.user_data.get(START_OVER) and update.callback_query:
        chat_id = update.effective_chat.id
        for message in context.user_data.get(MESSAGES_FOR_REMOVE):
            context.bot.delete_message(chat_id=chat_id, message_id=message.message_id)
        update_callback_answer_with_keyboard(update=update, text=TEXT_FOR_MAIN_HELLO, keyboard=keyboard)
    else:
        update.message.reply_text(text=TEXT_FOR_MAIN_HELLO, parse_mode=telegram.ParseMode.HTML, reply_markup=keyboard)

    context.user_data[START_OVER] = False
    context.user_data[MESSAGES_FOR_REMOVE] = []

    return SELECTING_ACTION


def show_menu_settings(update: Update, context: CallbackContext):
    logger.info("edit_main_settings")

    buttons = [
        [
            InlineKeyboardButton(text=f"{POSITIONS_ICON} {TEXT_POSITIONS}",
                                 callback_data=str(SHOW_MENU_POSITIONS_SETTINGS))
        ],
        [
            InlineKeyboardButton(text=f"{DISTRICTS_ICON} {TEXT_DISTRICTS}",
                                 callback_data=str(SHOW_MENU_DISTRICTS_SETTINGS))
        ],
        [
            InlineKeyboardButton(text=f"{REPORT_ICON} {TEXT_REPORTS}", callback_data=str(SHOW_MENU_REPORTS_SETTINGS))
        ],
        [
            InlineKeyboardButton(text=f"{SCHEDULE_ICON} {TEXT_SCHEDULE}",
                                 callback_data=str(SHOW_MENU_SCHEDULE_SETTINGS))
        ],
        [
            InlineKeyboardButton(text=f"{SHOW_SETTINGS_ICON} {TEXT_SHOW_SETTINGS}",
                                 callback_data=str(SHOW_CURRENT_SETTINGS)),
            get_back_button(),
        ],
    ]
    keyboard = InlineKeyboardMarkup(buttons)

    if not context.user_data.get(START_OVER) or not update.message:
        update_callback_answer_with_keyboard(update=update, text=TEXT_FOR_MENU_SETTINGS, keyboard=keyboard)
    else:
        update.message.reply_text(text=TEXT_FOR_MENU_SETTINGS, reply_markup=keyboard)

    fill_data_from_settings(update=update, context=context)

    return RUN_MENU_SETTINGS


def show_menu_positions_settings(update: Update, context: CallbackContext):
    logger.info("positions_settings")
    positions = context.user_data[POSITIONS]

    buttons = [
        [
            InlineKeyboardButton(text=f"{ADD_POSITIONS_ICON} {TEXT_ADD}", callback_data=str(START_EDIT_POSITIONS_ADD)),
            InlineKeyboardButton(text=f"{REMOVE_POSITIONS_ICON} {TEXT_REMOVE}",
                                 callback_data=str(START_EDIT_POSITIONS_REMOVE))
        ],
        [
            InlineKeyboardButton(text=f"{SAVE_ICON} {TEXT_SAVE}", callback_data=str(SAVE_POSITIONS_SETTINGS)),
            get_back_button(),
        ],
    ]
    keyboard = InlineKeyboardMarkup(buttons)

    text = "Препараты для проверки. Сейчас заданы: {0}".format(", ".join(positions))
    if (context.user_data.get(START_OVER) or not update.message) and update.callback_query:
        update_callback_answer_with_keyboard(update=update, text=text, keyboard=keyboard)
    else:
        update.message.reply_text(text=text, parse_mode=telegram.ParseMode.HTML, reply_markup=keyboard)

    return START_EDIT_POSITIONS


def show_menu_districts_settings(update: Update, context: CallbackContext):
    logger.info("districts_settings")
    chat_id = update.effective_chat.id
    districts = context.user_data[DISTRICTS]
    config_parser = DiabetConfigParser(chat_id)

    buttons = []
    for default_district in config_parser.default_districts:
        if config_parser.check_default_district_in_settings(default_district, districts):
            mark = PLUS_MARK_ICON
        else:
            mark = MINUS_MARK_ICON
        clear_district_name = default_district.replace(" район", "").title()
        buttons.append([InlineKeyboardButton(text=f"        {mark} {clear_district_name}",
                                             callback_data=str(SET_DISTRICTS_CHECK) + "_" + clear_district_name)])
    buttons.append([InlineKeyboardButton(text=f"{SAVE_ICON} {TEXT_SAVE}", callback_data=str(SAVE_DISTRICTS_SETTINGS)),
                    get_back_button()])

    keyboard = InlineKeyboardMarkup(buttons)

    text = "Выберите районы для проверки"
    if (context.user_data.get(START_OVER) or not update.message) and update.callback_query:
        update_callback_answer_with_keyboard(update=update, text=text, keyboard=keyboard)
    else:
        update.message.reply_text(text=text, parse_mode=telegram.ParseMode.HTML, reply_markup=keyboard)

    return START_EDIT_DISTRICTS


def show_menu_reports_settings(update: Update, context: CallbackContext):
    logger.info("email_settings")
    email = context.user_data[EMAIL]
    email_send = context.user_data[SEND_EMAIL]
    full_report_send = context.user_data[SEND_FULL_REPORT]

    text_for_menu = TEXT_MENU_REPORTS

    if email:
        text_for_menu += f"{TEXT_EMAIL}: {email}\n"
    else:
        text_for_menu += f"Сейчас e-mail не задан\n"

    mark_email = get_mark_icon(email_send)
    mark_full_report = get_mark_icon(full_report_send)

    buttons = [
        [
            InlineKeyboardButton(text=f"{EMAIL_ICON} {TEXT_CHANGE_EMAIL}", callback_data=str(START_EDIT_REPORTS_EMAIL)),
        ],
        [
            InlineKeyboardButton(text=f"{mark_email} {TEXT_SENDING_EMAIL}",
                                 callback_data=str(SET_REPORTS_SEND_EMAIL_CHECK))
        ],
        [
            InlineKeyboardButton(text=f"{mark_full_report} {TEXT_FULL_REPORT}",
                                 callback_data=str(SET_REPORTS_SEND_FULL_REPORT_CHECK))
        ],
        [
            InlineKeyboardButton(text=f"{SAVE_ICON} {TEXT_SAVE}", callback_data=str(SAVE_REPORTS_SETTINGS)),
            get_back_button(),
        ],
    ]
    keyboard = InlineKeyboardMarkup(buttons)

    if (context.user_data.get(START_OVER) or not update.message) and update.callback_query:
        update_callback_answer_with_keyboard(update=update, text=text_for_menu, keyboard=keyboard)
    else:
        update.message.reply_text(text_for_menu, reply_markup=keyboard)

    return START_EDIT_REPORTS


def show_menu_schedule_settings(update: Update, context: CallbackContext):
    schedule = context.user_data[SCHEDULE]
    logger.info(f"schedule_settings, schedule = {schedule}")

    buttons = [
        [
            InlineKeyboardButton(text=f"{SCHEDULE_EVERY_HOUR_ICON} {TEXT_EVERY_HOUR}",
                                 callback_data=str(SET_SCHEDULE_EVERY_HOUR_CHECK)),
        ],
        [
            InlineKeyboardButton(text=f"{SCHEDULE_EVERY_TWO_HOURS_ICON} {TEXT_EVERY_TWO_HOURS}",
                                 callback_data=str(SET_SCHEDULE_EVERY_TWO_HOURS_CHECK)),
        ],
        [
            InlineKeyboardButton(text=f"{SCHEDULE_EVERY_THREE_HOURS_ICON} {TEXT_EVERY_THREE_HOURS}",
                                 callback_data=str(SET_SCHEDULE_EVERY_THREE_HOURS_CHECK)),
        ],
        [
            InlineKeyboardButton(text=f"{SCHEDULE_EVERY_SIX_HOURS_ICON} {TEXT_EVERY_SIX_HOURS}",
                                 callback_data=str(SET_SCHEDULE_EVERY_SIX_HOURS_CHECK)),
        ],
        [
            InlineKeyboardButton(text=f"{SCHEDULE_EVERY_HOUR_ICON_SETTINGS} {TEXT_CHOOSE_HOURS}",
                                 callback_data=str(START_EDIT_EVERY_HOUR_CHECK)),
        ],
        [
            InlineKeyboardButton(text=f"{SCHEDULE_OFF_ICON} {TEXT_OFFCHECK}",
                                 callback_data=str(SET_SCHEDULE_OFF_CHECK)),
        ],
        [
            InlineKeyboardButton(text=f"{SAVE_ICON} {TEXT_SAVE}", callback_data=str(SAVE_SCHEDULE_SETTINGS)),
            get_back_button(),
        ],
    ]
    keyboard = InlineKeyboardMarkup(buttons)

    text_current_schedule = schedule_settings_to_string(schedule)

    text = f"{TEXT_SETTINGS_SCHEDULE} {text_current_schedule}"
    if (context.user_data.get(START_OVER) or not update.message) and update.callback_query:
        update_callback_answer_with_keyboard(update=update, text=text, keyboard=keyboard)
    else:
        update.message.reply_text(text=text, reply_markup=keyboard)

    return START_EDIT_SCHEDULE


def start_edit_every_hour_schedule(update: Update, context: CallbackContext):
    logger.info("start_edit_every_hour_schedule")

    schedule = context.user_data[SCHEDULE]

    buttons = [
        add_one_line_in_schedule(schedule=schedule, selected_range=range(4)),
        add_one_line_in_schedule(schedule=schedule, selected_range=range(4, 8)),
        add_one_line_in_schedule(schedule=schedule, selected_range=range(8, 12)),
        add_one_line_in_schedule(schedule=schedule, selected_range=range(12, 16)),
        add_one_line_in_schedule(schedule=schedule, selected_range=range(16, 20)),
        add_one_line_in_schedule(schedule=schedule, selected_range=range(20, 24)),
        [get_back_button()]
    ]

    keyboard = InlineKeyboardMarkup(buttons)

    if (context.user_data.get(START_OVER) or not update.message) and update.callback_query:
        update_callback_answer_with_keyboard(update=update, text=TEXT_CHECK_HOURS, keyboard=keyboard)
    else:
        update.message.reply_text(text=TEXT_CHECK_HOURS, parse_mode=telegram.ParseMode.HTML, reply_markup=keyboard)

    return TYPING_FOR_CHECK_SCHEDULE_HOURS


def show_current_settings(update: Update, _):
    logger.info("show_settings")
    chat_id = update.effective_chat.id

    config_parser = DiabetConfigParser(chat_id)
    positions, districts, emails, send_email, send_full_report, schedule = config_parser.get_values_from_config(chat_id)

    str_positions = ", ".join(positions)
    message_text = f"{POSITIONS_ICON} <b>{TEXT_POSITIONS}:</b>\n\n        {str_positions}\n\n"

    message_text += f"{DISTRICTS_ICON} <b>{TEXT_DISTRICTS}:</b>\n\n"
    for default_district in config_parser.default_districts:
        message_text += "        {0} {1}\n\n".format(
            get_mark_icon(config_parser.check_default_district_in_settings(default_district, districts)),
            default_district)

    message_text += f"{REPORT_ICON} <b>{TEXT_REPORTS}:</b>\n\n"
    if not emails or not emails[0]:
        message_text += f"        {EMAIL_ICON} <b>{TEXT_EMAIL}</b>: {TEXT_NOT_SET}\n\n"
    else:
        str_emails = ", ".join(emails)
        message_text += f"        {EMAIL_ICON} <b>{TEXT_EMAIL}</b>: {str_emails}\n\n"

    message_text += "        {0} {1}\n\n".format(get_mark_icon(send_email), TEXT_SENDING_EMAIL)
    message_text += "        {0} {1}\n\n".format(get_mark_icon(send_full_report), TEXT_FULL_REPORT)

    message_text += f"{SCHEDULE_ICON} <b>{TEXT_SCHEDULE}</b>:\n\n        {schedule_settings_to_string(schedule).capitalize()}"

    buttons = [[get_back_button()]]
    keyboard = InlineKeyboardMarkup(buttons)

    update_callback_answer_with_keyboard(update=update, text=message_text, keyboard=keyboard)

    return SHOWING_SETTINGS


def check(update: Update, context: CallbackContext) -> int:
    logger.info("check")
    bot = context.bot
    update.callback_query.answer()
    chat_id = update.callback_query.message.chat.id

    update.callback_query.answer()

    bot.send_chat_action(chat_id=chat_id, action=telegram.ChatAction.TYPING, timeout=100500)
    now = datetime.now()

    config_parser = DiabetConfigParser(chat_id)
    positions, districts, emails, send_email, send_full_report, schedule = config_parser.get_values_from_config(chat_id)

    email_string = ""
    if emails and len(emails) and emails[0] and send_email:
        if send_full_report:
            email_string = f"{TEXT_SEND_TO_EMAIL} {emails[0]}\n\n"
        else:
            email_string = f"{TEXT_SEND_TO_EMAIL_ONLY_NEW} {emails[0]}\n\n"

    districts_string = "\n    ".join(districts).title()
    table = ""
    new_table = ""

    html_parser = DiabetHtmlReportParser(chat_id)
    for position in positions:
        update.callback_query.edit_message_text(
            text=f"{TEXT_RECEIVING_DATA}\n    {districts_string}\n\n{email_string}Ищу {position}")
        table_res, diff_table_res = html_parser.get_table_for_one_position(position, districts)
        if table_res:
            table += table_res
        if diff_table_res:
            new_table += diff_table_res

    bot.send_chat_action(chat_id=chat_id, action=telegram.ChatAction.UPLOAD_DOCUMENT)

    report_sender = DiabetHtmlReportSender(now, chat_id)
    full_report_file, full_report_file_path = report_sender.write_report(True, now, table)
    new_report_file, new_report_file_path = report_sender.write_report(False, now, new_table)

    report_sender.send_emails(emails=emails, new_table=new_table, send_full_report=send_full_report)

    media = create_media_for_reports(now=now, send_full_report=send_full_report, full_report_file=full_report_file,
                                     full_report_file_path=full_report_file_path, new_report_file=new_report_file,
                                     new_report_file_path=new_report_file_path)
    buttons = [[get_back_button()]]
    keyboard = InlineKeyboardMarkup(buttons)

    list_messages_for_remove = []
    if media:
        message_suffix = get_media_suffix(media)
        if emails and len(emails) and emails[0] and send_email:
            update_callback_answer_with_keyboard(update=update,
                                                 text=f"Результаты в {message_suffix} ниже.\nОтправил их на {emails[0]}",
                                                 keyboard=keyboard)
        else:
            update_callback_answer_with_keyboard(update=update, text=f"Результаты в {message_suffix} ниже",
                                                 keyboard=keyboard)
        list_messages_for_remove = update.callback_query.message.reply_media_group(media=media)
        remove_reports(full_report_file=full_report_file, full_report_file_path=full_report_file_path,
                       new_report_file=new_report_file, new_report_file_path=new_report_file_path)
    else:
        if send_full_report:
            update_callback_answer_with_keyboard(update=update, text=f"{TEXT_NOT_FOUND}", keyboard=keyboard)
        else:
            update_callback_answer_with_keyboard(update=update, text=f"{TEXT_NEW_NOT_FOUND}", keyboard=keyboard)

    user_data = context.user_data
    user_data[START_OVER] = True
    user_data[MESSAGES_FOR_REMOVE] = list_messages_for_remove

    return SHOWING


def check_periodic(context: CallbackContext):
    bot = context.bot
    now = datetime.now()
    logger.info(f"check_periodic, global_chat_id = {global_chat_id}, current_hour = {now.hour}")

    config_parser = DiabetConfigParser(global_chat_id)
    positions, districts, emails, send_email, send_full_report, schedule = config_parser.get_values_from_config(
        global_chat_id)

    is_find_hour = False
    for one_hour in schedule:
        if int(one_hour) == now.hour:
            logger.info(f"check_periodic, time in schedule range")
            is_find_hour = True
    if not is_find_hour:
        logger.info(f"check_periodic, time {now.hour} not in schedule range {schedule}, exit")
        return

    html_parser = DiabetHtmlReportParser(global_chat_id)

    table, new_table = html_parser.get_tables_from_html_positions(positions=positions, districts=districts)

    report_sender = DiabetHtmlReportSender(now, global_chat_id)
    full_report_file, full_report_file_path = report_sender.write_report(True, now, table)
    new_report_file, new_report_file_path = report_sender.write_report(False, now, new_table)

    report_sender.send_emails(emails=emails, new_table=new_table, send_full_report=send_full_report)

    media = create_media_for_reports(now=now, send_full_report=send_full_report, full_report_file=full_report_file,
                                     full_report_file_path=full_report_file_path, new_report_file=new_report_file,
                                     new_report_file_path=new_report_file_path)
    bot.send_media_group(global_chat_id, media=media)
    remove_reports(full_report_file=full_report_file, full_report_file_path=full_report_file_path,
                   new_report_file=new_report_file, new_report_file_path=new_report_file_path)
    return END


def stop(update: Update, _) -> int:
    logger.info("stop")
    update.message.reply_text(TEXT_BYE)

    return END


def return_to_start(update: Update, context: CallbackContext) -> int:
    logger.info("return_to_start")
    context.user_data[START_OVER] = True
    start(update, context)

    return END


def stop_nested(update: Update, _) -> int:
    logger.info("stop_nested")
    update.message.reply_text(TEXT_BYE)
    return STOPPING


def end_change_settings(update: Update, context: CallbackContext) -> int:
    logger.info("end_change_settings")
    return return_to_main_settings(update=update, context=context)


def end_change_schedule_hours(update: Update, context: CallbackContext) -> int:
    logger.info("end_change_schedule_hours")

    context.user_data[START_OVER] = True
    show_menu_schedule_settings(update, context)

    return START_EDIT_SCHEDULE


def save_positions_settings(update: Update, context: CallbackContext) -> int:
    logger.info("save_settings_positions")

    chat_id = update.callback_query.message.chat.id
    config_parser = DiabetConfigParser(chat_id)
    config_parser.save_positions_to_config(chat_id, context.user_data[POSITIONS])

    return return_to_main_settings(update=update, context=context)


def save_reports_settings(update: Update, context: CallbackContext) -> int:
    logger.info("save_settings_reports")
    chat_id = update.callback_query.message.chat.id

    config_parser = DiabetConfigParser(chat_id)
    config_parser.save_reports_to_config(chat_id, context.user_data[EMAIL], context.user_data[SEND_EMAIL],
                                         context.user_data[SEND_FULL_REPORT])

    return return_to_main_settings(update=update, context=context)


def save_settings_schedule(update: Update, context: CallbackContext) -> int:
    logger.info("save_settings_schedule")

    chat_id = update.callback_query.message.chat.id
    config_parser = DiabetConfigParser(chat_id)
    config_parser.save_schedule_to_config(chat_id, context.user_data[SCHEDULE])

    return return_to_main_settings(update=update, context=context)


def return_to_main_settings(update: Update, context: CallbackContext) -> int:
    logger.info("return_to_main_settings")

    context.user_data[START_OVER] = True
    show_menu_settings(update, context)

    return END


def set_district_check(update: Update, context: CallbackContext) -> int:
    logger.info("check_district")

    checking_district = update.callback_query.data.split("_", 1)[1]
    user_data = context.user_data
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

    context.user_data[START_OVER] = True
    show_menu_districts_settings(update, context)

    return START_EDIT_DISTRICTS


def set_reports_send_email_check(update: Update, context: CallbackContext) -> int:
    logger.info("set_reports_send_email_check")
    context.user_data[SEND_EMAIL] = not context.user_data[SEND_EMAIL]
    return return_to_showing_menu_reports_settings(update=update, context=context)


def set_reports_send_full_report_check(update: Update, context: CallbackContext) -> int:
    logger.info("set_reports_send_full_report_check")
    context.user_data[SEND_FULL_REPORT] = not context.user_data[SEND_FULL_REPORT]
    return return_to_showing_menu_reports_settings(update=update, context=context)


def return_to_showing_menu_reports_settings(update: Update, context: CallbackContext) -> int:
    context.user_data[START_OVER] = True
    show_menu_reports_settings(update, context)
    return START_EDIT_REPORTS


def check_schedule_hour(update: Update, context: CallbackContext) -> int:
    logger.info("check_schedule_hour")

    checking_hour = int(update.callback_query.data.split("_", 1)[1])
    current_schedule = context.user_data[SCHEDULE]

    index_hour = -1
    for index, current_hour in enumerate(current_schedule):
        if checking_hour == int(current_hour):
            index_hour = index
            break

    if index_hour == -1:
        current_schedule.append(str(checking_hour))
    else:
        current_schedule.pop(index_hour)
    current_schedule.sort()

    context.user_data[START_OVER] = True
    start_edit_every_hour_schedule(update, context)

    return TYPING_FOR_CHECK_SCHEDULE_HOURS


def set_schedule_every_one_hour(update: Update, context: CallbackContext) -> int:
    logger.info("set_schedule_every_one_hour")
    set_schedule_data(update=update, context=context, data=EVERY_HOUR_SCHEDULE)
    return START_EDIT_SCHEDULE


def set_schedule_every_two_hours(update: Update, context: CallbackContext) -> int:
    logger.info("set_schedule_every_two_hours")
    set_schedule_data(update=update, context=context, data=EVERY_TWO_HOURS_SCHEDULE)
    return START_EDIT_SCHEDULE


def set_schedule_every_three_hours(update: Update, context: CallbackContext) -> int:
    logger.info("set_schedule_every_three_hours")
    set_schedule_data(update=update, context=context, data=EVERY_THREE_HOURS_SCHEDULE)
    return START_EDIT_SCHEDULE


def set_schedule_every_six_hours(update: Update, context: CallbackContext) -> int:
    logger.info("set_schedule_every_six_hours")
    set_schedule_data(update=update, context=context, data=EVERY_SIX_HOURS_SCHEDULE)
    return START_EDIT_SCHEDULE


def set_schedule_off(update: Update, context: CallbackContext) -> int:
    logger.info("set_schedule_off")
    set_schedule_data(update=update, context=context, data=[])
    return START_EDIT_SCHEDULE


def set_schedule_data(update: Update, context: CallbackContext, data):
    context.user_data[SCHEDULE] = data
    context.user_data[START_OVER] = True
    show_menu_schedule_settings(update, context)


def save_districts_settings(update: Update, context: CallbackContext) -> int:
    logger.info("save_settings_districts")

    chat_id = update.callback_query.message.chat.id

    config_parser = DiabetConfigParser(chat_id)
    config_parser.save_districts_to_config(chat_id, context.user_data[DISTRICTS])

    context.user_data[START_OVER] = True
    show_menu_settings(update, context)

    return END


def main():
    is_local_run = "local" in sys.argv
    if is_local_run:
        from credentials import bot_token, bot_user_name
        updater = Updater(token=bot_token, use_context=True)
    else:
        bot_token = os.environ.get("TOKEN")
        bot_user_name = os.environ.get("BOT-USER-NAME")
        port = int(os.environ.get("PORT"))
        logger.info(f"run bot, port = {port}")
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
                MessageHandler(Filters.text & ~Filters.command, save_add_positions_input)
            ],
            TYPING_FOR_ADD_POSITIONS: [MessageHandler(Filters.text & ~Filters.command, save_add_positions_input),
                                       CallbackQueryHandler(end_change_settings, pattern='^' + str(END) + '$')],
            TYPING_FOR_REMOVE_POSITIONS: [MessageHandler(Filters.text & ~Filters.command, save_remove_positions_input),
                                          CallbackQueryHandler(end_change_settings, pattern='^' + str(END) + '$')]
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
                CallbackQueryHandler(save_districts_settings, pattern='^' + str(SAVE_DISTRICTS_SETTINGS) + '$'),
                CallbackQueryHandler(end_change_settings, pattern='^' + str(END) + '$'),
            ],
            TYPING_FOR_ADD_POSITIONS: [MessageHandler(Filters.text & ~Filters.command, save_add_positions_input),
                                       CallbackQueryHandler(end_change_settings, pattern='^' + str(END) + '$')],
            TYPING_FOR_REMOVE_POSITIONS: [MessageHandler(Filters.text & ~Filters.command, save_remove_positions_input),
                                          CallbackQueryHandler(end_change_settings, pattern='^' + str(END) + '$')]
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

    reports_settings_conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(show_menu_reports_settings, pattern='^' + str(SHOW_MENU_REPORTS_SETTINGS) + '$')],
        states={
            START_EDIT_REPORTS: [
                CallbackQueryHandler(start_edit_reports_email, pattern='^' + str(START_EDIT_REPORTS_EMAIL) + '$'),
                CallbackQueryHandler(set_reports_send_email_check, pattern='^' + str(SET_REPORTS_SEND_EMAIL_CHECK)),
                CallbackQueryHandler(set_reports_send_full_report_check,
                                     pattern='^' + str(SET_REPORTS_SEND_FULL_REPORT_CHECK)),
                CallbackQueryHandler(save_reports_settings, pattern='^' + str(SAVE_REPORTS_SETTINGS) + '$'),
                CallbackQueryHandler(end_change_settings, pattern='^' + str(END) + '$'),
                MessageHandler(Filters.text & ~Filters.command, save_add_positions_input)
            ],
            TYPING_FOR_SET_EMAIL: [MessageHandler(Filters.text & ~Filters.command, save_email_input),
                                   CallbackQueryHandler(end_change_settings, pattern='^' + str(END) + '$')]
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
                CallbackQueryHandler(set_schedule_every_one_hour,
                                     pattern='^' + str(SET_SCHEDULE_EVERY_HOUR_CHECK) + '$'),
                CallbackQueryHandler(set_schedule_every_two_hours,
                                     pattern='^' + str(SET_SCHEDULE_EVERY_TWO_HOURS_CHECK) + '$'),
                CallbackQueryHandler(set_schedule_every_three_hours,
                                     pattern='^' + str(SET_SCHEDULE_EVERY_THREE_HOURS_CHECK) + '$'),
                CallbackQueryHandler(set_schedule_every_six_hours,
                                     pattern='^' + str(SET_SCHEDULE_EVERY_SIX_HOURS_CHECK) + '$'),
                CallbackQueryHandler(start_edit_every_hour_schedule, pattern='^' + str(START_EDIT_EVERY_HOUR_CHECK)),
                CallbackQueryHandler(set_schedule_off,
                                     pattern='^' + str(SET_SCHEDULE_OFF_CHECK) + '$'),
                CallbackQueryHandler(save_settings_schedule, pattern='^' + str(SAVE_SCHEDULE_SETTINGS) + '$'),
                CallbackQueryHandler(end_change_settings, pattern='^' + str(END) + '$'),
                MessageHandler(Filters.text & ~Filters.command, save_add_positions_input)
            ],
            TYPING_FOR_CHECK_SCHEDULE_HOURS: [
                CallbackQueryHandler(check_schedule_hour, pattern='^' + str(CHECK_SCHEDULE_HOUR)),
                CallbackQueryHandler(end_change_schedule_hours, pattern='^' + str(END) + '$')
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
                CallbackQueryHandler(show_menu_settings, pattern='^' + str(SHOW_MENU_MAIN_SETTINGS) + '$')],
            SHOWING_SETTINGS: [CallbackQueryHandler(return_to_main_settings, pattern='^' + str(END) + '$')]
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
        entry_points=[CallbackQueryHandler(show_menu_settings, pattern='^' + str(SHOW_MENU_MAIN_SETTINGS) + '$')],
        states={
            SHOWING_SETTINGS: [
                CallbackQueryHandler(show_menu_settings, pattern='^' + str(SHOW_MENU_MAIN_SETTINGS) + '$'),
                positions_settings_conv,
                districts_settings_conv,
                reports_settings_conv,
                schedule_settings_conv,
                show_settings_conv],
            RUN_MENU_SETTINGS: [
                positions_settings_conv,
                districts_settings_conv,
                reports_settings_conv,
                schedule_settings_conv,
                show_settings_conv
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

    selection_handlers = [
        run_check_conv,
        main_menu_settings_conv
    ]
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            SELECTING_ACTION: selection_handlers,
            STOPPING: [CommandHandler('start', start)],
            SHOWING: selection_handlers
        },
        fallbacks=[CommandHandler('stop', stop)],
    )

    dp.add_handler(conv_handler)

    j = updater.job_queue
    for hour in range(24):
        time = datetime.now().replace(hour=hour, minute=0, second=0).time()
        j.run_daily(check_periodic, time=time)

    if is_local_run:
        updater.start_polling()
    else:
        port = int(os.environ.get('PORT', 8443))
        updater.start_webhook(listen="0.0.0.0",
                              port=int(port),
                              url_path=bot_token)
        updater.bot.setWebhook('https://heroku.com/apps/diabet-scaner-bot/' + bot_token)

    updater.idle()


if __name__ == '__main__':
    main()
