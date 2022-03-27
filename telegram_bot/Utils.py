from base.DiabetParamsFabric import DiabetParamsFabric

import os
from Constants import *
import telegram
from telegram import Update, InputMediaDocument, InlineKeyboardButton
from telegram.ext import CallbackContext
import os

import telegram
from telegram import Update, InputMediaDocument, InlineKeyboardButton
from telegram.ext import CallbackContext

from Constants import *
from base.DiabetParamsFabric import DiabetParamsFabric


def update_callback_answer(update: Update, text):
    update.callback_query.answer()
    if update.callback_query.message.text != text:
        update.callback_query.edit_message_text(text=text, parse_mode=telegram.ParseMode.HTML)


def update_callback_answer_with_keyboard(update: Update, text, keyboard):
    update.callback_query.answer()
    if update.callback_query.message.text != text or update.callback_query.message.reply_markup != keyboard:
        update.callback_query.edit_message_text(text=text, parse_mode=telegram.ParseMode.HTML, reply_markup=keyboard)


def schedule_settings_to_string(schedule):
    if schedule and len(schedule):
        numbered_array = [int(i) for i in schedule]
        numbered_array.sort()
        if numbered_array == EVERY_HOUR_SCHEDULE:
            return "включена проверка каждый час"
        elif numbered_array == EVERY_TWO_HOURS_SCHEDULE:
            return "включена проверка каждые 2 часа"
        elif numbered_array == EVERY_THREE_HOURS_SCHEDULE:
            return "включена проверка каждые 3 часа"
        elif numbered_array == EVERY_SIX_HOURS_SCHEDULE:
            return "включена проверка каждые 6 часов"
        else:
            text_current_schedule = "включена проверка в "
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
        return "проверка отключена"


def clear_list_for_edit(list_for_clear):
    try:
        return list_for_clear.replace(", ", ",").replace(" ,", ",").split(",")
    except Exception as e:
        print(e)
        return []


def fill_data_from_settings(heroku_run: bool, update: Update, context: CallbackContext, logger):
    chat_id = update.effective_chat.id
    config_fabric = DiabetParamsFabric(heroku_run, logger, chat_id)
    config_parser = config_fabric.get_config_worker()

    positions, districts, emails, send_e_mail, send_full_report, schedule = config_parser.get_values_from_config(chat_id)
    context.user_data[POSITIONS] = positions
    context.user_data[DISTRICTS] = districts
    if emails and len(emails):
        context.user_data[EMAIL] = emails[0]
    else:
        context.user_data[EMAIL] = ''
    context.user_data[SEND_EMAIL] = send_e_mail
    context.user_data[SEND_FULL_REPORT] = send_full_report
    context.user_data[SCHEDULE] = schedule


def create_media_for_reports(now, send_full_report, full_report_file, full_report_file_path, new_report_file, new_report_file_path):
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
        return MINUS_MARK_ICON


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


def add_one_line_in_schedule(schedule, selected_range):
    result_buttons = []
    for one_hour in selected_range:
        str_mark = get_hour_mark_with_string(one_hour=one_hour, schedule=schedule)
        result_buttons.append(InlineKeyboardButton(text=str_mark, callback_data=str(CHECK_SCHEDULE_HOUR) + "_" +
                                                   str(one_hour)))
    return result_buttons


def get_back_button():
    return InlineKeyboardButton(text=f"{BACK_ICON} {TEXT_BACK}", callback_data=str(END))
