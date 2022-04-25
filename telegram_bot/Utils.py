import os

import telegram
from telegram import Update, InputMediaDocument, InlineKeyboardButton
from telegram.ext import CallbackContext

from base.Constants import *
from base.DiabetParamsFabric import DiabetParamsFabric
from validate_email import validate_email


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


def schedule_to_string(schedule_days, schedule_hours, email_send, emails):
    message_text = ""
    if is_shedule_off(schedule_days) and is_shedule_off(schedule_hours):
        message_text += f"        {TEXT_SCHEDULE_OFF}\n\n"
    else:
        if is_shedule_on(schedule_days):
            message_text += f"        {TEXT_SCHEDULE_DAYS_SELECTED}: {schedule_settings_days_to_string(schedule_days)}\n\n"
        else:
            message_text += f"        {TEXT_SCHEDULE_DAYS_SELECTED}: {TEXT_NO_PARAMS}ы\n\n"

        if is_shedule_on(schedule_hours):
            message_text += f"        {TEXT_SCHEDULE_HOURS_SELECTED}: {schedule_settings_hours_to_string(schedule_hours)}\n\n"
        else:
            message_text += f"        {TEXT_SCHEDULE_HOURS_SELECTED}: {TEXT_NO_PARAMS}ы\n\n"

    if not emails or not emails[0]:
        message_text += f"        {EMAIL_ICON} <b>{TEXT_EMAIL}</b>: {TEXT_NOT_SET}\n\n"
    else:
        str_emails = ", ".join(emails)
        message_text += f"        {EMAIL_ICON} <b>{TEXT_EMAIL}</b>: {str_emails}\n\n"

    message_text += "        {0} {1}\n\n".format(get_mark_icon(email_send), TEXT_SENDING_EMAIL)

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

    positions, districts, emails, send_e_mail, schedule_hours, schedule_days, schedule_check, benefit_federal = config_parser.get_values_from_config(
        chat_id)
    context.user_data[POSITIONS] = positions
    context.user_data[DISTRICTS] = districts
    if emails and len(emails):
        context.user_data[EMAIL] = emails[0]
    else:
        context.user_data[EMAIL] = ''
    context.user_data[SEND_EMAIL] = send_e_mail
    context.user_data[SCHEDULE_HOURS] = schedule_hours
    context.user_data[SCHEDULE_DAYS] = schedule_days
    context.user_data[SCHEDULE_CHECK] = schedule_check
    context.user_data[BENEFIT_FEDERAL] = benefit_federal


def remove_reports(full_report_file, full_report_file_path):
    try:
        if full_report_file:
            os.remove(full_report_file_path)
    except Exception as e:
        print(f"error = {e}")


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
    return InlineKeyboardButton(text=f"{RESTART_CHECK_ICON} {TEXT_RESTART_CHECK}", callback_data=str(RUN_CHECK))


def check_email_address(email):
    res_parse = validate_email(email_address=email, check_format=True, check_smtp=False, check_blacklist=False,
                               check_dns=False)
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


def create_text_by_result_array(result_array):
    result = ""

    count_added_districts = 0
    for index, position in enumerate(result_array):
        str_for_district = ""
        for district_key in position:
            array_federal = []
            array_regional = []
            for district_info in position[district_key]:
                for district_info_key in district_info:
                    for pharmacies in district_info[district_info_key]["federal"]:
                        array_federal += f"{pharmacies}\n"

                    for pharmacies in district_info[district_info_key]["regional"]:
                        array_regional += f"{pharmacies}\n"

            is_exists_federal = len(array_federal) > 0
            is_exists_regional = len(array_regional) > 0

            if is_exists_federal or is_exists_regional:
                str_for_district += f"{district_key}\n\n"

                for federal_pharmacy in array_federal:
                    str_for_district += federal_pharmacy

                for regional_pharmacy in array_regional:
                    str_for_district += regional_pharmacy
        if str_for_district:
            if count_added_districts == 0:
                result += f"\n"
            else:
                result += f"\n------------------------\n\n"
            count_added_districts = count_added_districts + 1
            result += str_for_district
    return result


def get_text_for_results(table, str_array_result, emails, send_email, benefit_federal, schedule_check, for_periodical_check=False):
    if benefit_federal:
        str_benefit = TEXT_BENEFIT_FEDERAL_CHECK
    else:
        str_benefit = TEXT_BENEFIT_REGIONAL_CHECK

    if table:
        if emails and len(emails) and emails[0] and send_email:
            if table:
                if str_array_result:
                    if schedule_check:
                        return f"Результаты отправил на {emails[0]}\nВот что изменилось по {str_benefit}:\n{str_array_result}"
                    else:
                        return f"Вот что изменилось по {str_benefit}:\n{str_array_result}"
                else:
                    if for_periodical_check:
                        return ""
                    else:
                        return f"Отправил отчет на {emails[0]}\nНовых изменений по {str_benefit} не нашел"
        else:
            if str_array_result:
                return f"Результаты по {str_benefit}:\n{str_array_result}"
            else:
                if for_periodical_check:
                    return ""
                else:
                    return f"{TEXT_NEW_NOT_FOUND}"
    else:
        if for_periodical_check:
            return ""
        else:
            return f"{TEXT_NOT_FOUND}"


def check_value_in_schedule(schedule, value):
    for one_schedule_value in schedule:
        if int(one_schedule_value) == int(value):
            return True
    return False
