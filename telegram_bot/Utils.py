import os

import telegram
from telegram import Update, InputMediaDocument, InlineKeyboardButton
from telegram.ext import CallbackContext

from base.Constants import *
from base.DiabetParamsFabric import DiabetParamsFabric
from validate_email import validate_email


def update_callback_answer(update: Update, text):
    try:
        update.callback_query.answer()
        if update.callback_query.message.text != text:
            update.callback_query.edit_message_text(text=text, parse_mode=telegram.ParseMode.HTML)
            return update.callback_query.message.message_id
    except Exception:
        if not update.callback_query:
            if update.message.text != text:
                return update.message.reply_text(text=text, parse_mode=telegram.ParseMode.HTML).message_id
        else:
            if update.callback_query.message.text != text != text:
                update.callback_query.edit_message_text(text=text, parse_mode=telegram.ParseMode.HTML)
                return update.callback_query.message.message_id


def update_callback_answer_with_keyboard(update: Update, text, keyboard):
    try:
        update.callback_query.answer()
        if update.callback_query.message.text != text or update.callback_query.message.reply_markup != keyboard:
            update.callback_query.edit_message_text(text=text, parse_mode=telegram.ParseMode.HTML,
                                                    reply_markup=keyboard)
    except Exception:
        if update.callback_query.message.text != text or update.callback_query.message.reply_markup != keyboard:
            if update.message:
                update.message.reply_text(text=text, parse_mode=telegram.ParseMode.HTML, reply_markup=keyboard)
            else:
                update.callback_query.edit_message_text(text=text, parse_mode=telegram.ParseMode.HTML,
                                                        reply_markup=keyboard)


def schedule_settings_hours_to_string(schedule_hours):
    if is_shedule_on(schedule_hours):
        numbered_array = [int(i) for i in schedule_hours]
        numbered_array.sort()
        if numbered_array == EVERY_HOUR_SCHEDULE:
            return "каждый час"
        elif numbered_array == EVERY_TWO_HOURS_SCHEDULE:
            return "каждые 2 часа"
        elif numbered_array == EVERY_THREE_HOURS_SCHEDULE:
            return "каждые 3 часа"
        elif numbered_array == EVERY_SIX_HOURS_SCHEDULE:
            return "каждые 6 часов"
        else:
            text_current_schedule = ""
            hours_string = ''
            for one_hour in numbered_array:
                if hours_string:
                    hours_string += ", "
                if one_hour < 10:
                    hours_string += f"0{one_hour}:00"
                else:
                    hours_string += f"{one_hour}:00"
            text_current_schedule += hours_string
            return text_current_schedule
    else:
        return TEXT_NOT_SET + "а"


def schedule_settings_days_to_string(schedule_days):
    if is_shedule_on(schedule_days):
        numbered_array = [int(i) for i in schedule_days]
        numbered_array.sort()
        if numbered_array == EVERY_DAY_SCHEDULE:
            return "каждый день"
        else:
            text_current_schedule = ""
            days_string = ''
            for one_day in numbered_array:
                if days_string:
                    days_string += ", "
                days_string += DAYS_ARRAY[one_day].lower()
            text_current_schedule += days_string
            return text_current_schedule
    else:
        return TEXT_NOT_SET + "а"


def schedule_to_string(schedule_days, schedule_hours, schedule_check, print_header=True):
    message_text = ""
    if is_shedule_off(schedule_days) and is_shedule_off(schedule_hours):
        if print_header:
            message_text += f"{SCHEDULE_ICON} <b>{TEXT_SCHEDULE}</b>:\n\n        {TEXT_SCHEDULE_OFF}\n\n"
        else:
            message_text += f"        {TEXT_SCHEDULE_OFF}\n\n"
    else:
        if print_header:
            message_text += f"{SCHEDULE_ICON} <b>{TEXT_SCHEDULE}</b>:\n\n"
        if is_shedule_on(schedule_days):
            message_text += f"        {TEXT_SCHEDULE_DAYS_SELECTED}: {schedule_settings_days_to_string(schedule_days)}\n\n"
        else:
            message_text += f"        {TEXT_SCHEDULE_DAYS_SELECTED}: {TEXT_NO_PARAMS}ы\n\n"

        if is_shedule_on(schedule_hours):
            message_text += f"        {TEXT_SCHEDULE_HOURS_SELECTED}: {schedule_settings_hours_to_string(schedule_hours)}\n\n"
        else:
            message_text += f"        {TEXT_SCHEDULE_HOURS_SELECTED}: {TEXT_NO_PARAMS}ы\n\n"

    if print_header:
        if schedule_check:
            mark = PLUS_MARK_ICON
            text = TEXT_ON.capitalize() + "a"
        else:
            mark = RED_CROSS_ICON
            text = TEXT_OFF.capitalize() + "a"
        message_text += f"        {mark} {text}\n\n"

    return message_text


def is_shedule_on(schedule):
    return schedule and len(schedule) and len(str(schedule[0]))


def is_shedule_off(schedule):
    return not schedule or not len(schedule) or not len(str(schedule[0]))


def clear_list_for_edit(new_list, current_list, logger, without_checking):
    try:
        if without_checking:
            return new_list.replace(", ", ",").replace(" ,", ",").split(",")
        res_list = []
        cleared_new_list = new_list.replace(", ", ",").replace(" ,", ",").split(",")
        logger.info(f"cleared_new_list = {cleared_new_list}")
        for new_position in cleared_new_list:
            is_find = False
            logger.info(f"check new_position = {new_position}")
            for current in current_list:
                logger.info(f"check new_position = {new_position} and current_list = {current_list}")
                if current.lower() == new_position.lower():
                    is_find = True
                    break
            if not is_find:
                res_list.append(new_position)
        return res_list
    except Exception as e:
        print(e)
        return []


def fill_data_from_settings(heroku_run: bool, update: Update, context: CallbackContext, logger):
    chat_id = update.effective_chat.id
    config_fabric = DiabetParamsFabric(heroku_run, logger, chat_id)
    config_parser = config_fabric.get_config_worker()

    positions, districts, emails, send_e_mail, send_full_report, schedule_hours, schedule_days, schedule_check, benefit_federal = config_parser.get_values_from_config(
        chat_id)
    context.user_data[POSITIONS] = positions
    context.user_data[DISTRICTS] = districts
    if emails and len(emails):
        context.user_data[EMAIL] = emails[0]
    else:
        context.user_data[EMAIL] = ''
    context.user_data[SEND_EMAIL] = send_e_mail
    context.user_data[SEND_FULL_REPORT] = send_full_report
    context.user_data[SCHEDULE_HOURS] = schedule_hours
    context.user_data[SCHEDULE_DAYS] = schedule_days
    context.user_data[SCHEDULE_CHECK] = schedule_check
    context.user_data[BENEFIT_FEDERAL] = benefit_federal


def create_media_for_reports(now, send_full_report, full_report_file, full_report_file_path, new_report_file,
                             new_report_file_path):
    media = []
    if send_full_report and full_report_file:
        media.append(InputMediaDocument(caption="Полный отчет на {0}".format(now.strftime("%d.%m.%Y %H:%M:%S")),
                                        media=open(full_report_file_path, 'rb')))

    if new_report_file:
        media.append(InputMediaDocument(caption="Новые позиции на {0}".format(now.strftime("%d.%m.%Y %H:%M:%S")),
                                        media=open(new_report_file_path, 'rb')))
    return media


def remove_reports(full_report_file, full_report_file_path, new_report_file, new_report_file_path):
    if full_report_file:
        os.remove(full_report_file_path)

    if new_report_file:
        os.remove(new_report_file_path)


def get_mark_icon(some_bool):
    if some_bool:
        return PLUS_MARK_ICON
    else:
        return RED_CROSS_ICON


def get_media_suffix(files_array):
    if len(files_array) > 1:
        return "файлах"
    else:
        return "файле"


def get_district_name_for_compare(district):
    return district.replace("район", "").replace(" ", "").lower()


def get_hour_mark_with_string(one_hour, schedule):
    mark = get_mark_icon(str(one_hour) in schedule or one_hour in schedule)
    if one_hour < 10:
        return f"        {mark} 0{one_hour}:00"
    else:
        return f"        {mark} {one_hour}:00"


def add_one_line_in_schedule_hours(schedule, selected_range):
    result_buttons = []
    for one_hour in selected_range:
        str_mark = get_hour_mark_with_string(one_hour=one_hour, schedule=schedule)
        result_buttons.append(InlineKeyboardButton(text=str_mark, callback_data=str(CHECK_SCHEDULE_HOUR) + "_" +
                                                                                str(one_hour)))
    return result_buttons


def get_days_in_schedule(schedule_days):
    result_buttons = []
    for index, one_day in enumerate(DAYS_ARRAY):
        mark = get_mark_icon(index in (int(day) for day in schedule_days))
        text = f"        {mark} {one_day}"
        result_buttons.append([InlineKeyboardButton(text=text, callback_data=str(CHECK_SCHEDULE_DAY) + "_" +
                                                                             str(index))])
    return result_buttons


def get_back_button():
    return InlineKeyboardButton(text=f"{BACK_ICON} {TEXT_BACK}", callback_data=str(END))


def get_restart_check_button():
    return InlineKeyboardButton(text=f"{RESTART_CHECK_ICON} {TEXT_RESTART_CHECK}", callback_data=str(END))


def check_email_address(email):
    res_parse = validate_email(email_address=email, check_format=True, check_smtp=False, check_blacklist=False, check_dns=False)
    return res_parse


def get_chat_id(update, context):
    chat_id = -1

    if update.message is not None:
        chat_id = update.message.chat.id
    elif update.callback_query is not None:
        chat_id = update.callback_query.message.chat.id
    elif update.poll is not None:
        chat_id = context.bot_data[update.poll.id]

    return chat_id
