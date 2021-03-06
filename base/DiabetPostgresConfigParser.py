import os
import psycopg

from base.DiabetParamsWorker import DiabetParamsWorker


class DiabetPostgresConfigParser(DiabetParamsWorker):
    def __init__(self, logger, config_suffix=''):
        super().__init__(logger, config_suffix)

        self.pg_uri = os.environ.get("DB_URI")

    def get_values_from_config(self, config_suffix=''):
        query = ""
        try:
            connection, cursor = self.open_db()
            query = "CREATE TABLE IF NOT EXISTS bot_params (id serial PRIMARY KEY, config_suffix bigint, " \
                    "positions text, districts text, email text, send_email boolean, send_full_report boolean, schedule text);"
            cursor.execute(query)
            connection.commit()
            str_config = self.string_to_string_for_db(config_suffix)
            query = f"select positions, districts, email, send_email, send_full_report, schedule from bot_params where config_suffix={str_config};"
            cursor.execute(query)
            self.logger.info(f"get_values_from_config {query}")
            if cursor.rowcount:
                result = cursor.fetchall()[0]
                self.logger.info(f"get_values_from_config result = {result}")
                positions = self.string_from_db_to_array(result[0])
                positions.sort()
                districts = self.string_from_db_to_array(result[1])
                districts.sort()
                emails = self.string_from_db_to_array(result[2])
                send_email = result[3]
                send_full_report = result[4]
                schedule = self.string_from_db_to_array(result[5])
                benefit_federal = result[6]
                self.logger.info(f"get_values_from_config values_result = {positions}, {districts}, {emails}, {send_email}, {send_full_report}, {schedule}, {benefit_federal}")
                return positions, districts, emails, send_email, send_full_report, schedule, benefit_federal
            else:
                self.close_db(connection=connection, cursor=cursor)
                self.init_config_with_default_values(config_suffix)
        except (Exception, psycopg.Error) as error:
            self.close_db(connection=connection, cursor=cursor)
            self.logger.info(f"Error in get_values_from_config, query = {query}", error)
        finally:
            self.close_db(connection=connection, cursor=cursor)

        return self.default_positions, self.default_districts, [], False, True, self.default_schedule, True

    def init_config_with_default_values(self, config_suffix):
        try:
            config_positions = self.array_to_string_for_db(self.default_positions)
            config_districts = self.array_to_string_for_db(self.default_districts)
            send_email = False
            send_full_report = True
            config_schedule = self.array_to_string_for_db(self.default_schedule)

            str_config = self.string_to_string_for_db(config_suffix)

            connection, cursor = self.open_db()
            query = f"insert into bot_params (config_suffix, positions, districts, send_email, send_full_report, schedule) values({str_config}, {config_positions}, {config_districts}, {send_email}, {send_full_report}, {config_schedule});"
            self.execute_update(connection=connection, cursor=cursor, query=query)
        except (Exception, psycopg.Error) as error:
            self.logger.info(f"Error init_config_with_default_values, query = {query}", error)
        finally:
            self.close_db(connection=connection, cursor=cursor)

    def save_positions_to_config(self, config_suffix, new_positions):
        try:
            str_positions = self.array_to_string_for_db(new_positions)
            str_config = self.string_to_string_for_db(config_suffix)
            query = f"update bot_params set positions = {str_positions} where config_suffix={str_config};"

            connection, cursor = self.open_db()
            self.execute_update(connection=connection, cursor=cursor, query=query)
        except (Exception, psycopg.Error) as error:
            self.logger.info(f"Error save_positions_to_config, query = {query}", error)
        finally:
            self.close_db(connection=connection, cursor=cursor)

    def save_districts_to_config(self, config_suffix, new_districts):
        try:
            str_districts = self.array_to_string_for_db(new_districts)
            str_config = self.string_to_string_for_db(config_suffix)
            query = f"update bot_params set districts = {str_districts} where config_suffix={str_config};"

            connection, cursor = self.open_db()
            self.execute_update(connection=connection, cursor=cursor, query=query)
        except (Exception, psycopg.Error) as error:
            self.logger.info(f"Error save_districts_to_config, query = {query}", error)
        finally:
            self.close_db(connection=connection, cursor=cursor)

    def save_reports_to_config(self, config_suffix, new_email, new_send_email):
        try:
            str_emails = self.array_to_string_for_db([new_email])
            str_config = self.string_to_string_for_db(config_suffix)
            query = f"update bot_params set email = {str_emails}, send_email = {new_send_email} where config_suffix={str_config};"

            connection, cursor = self.open_db()
            self.execute_update(connection=connection, cursor=cursor, query=query)
        except (Exception, psycopg.Error) as error:
            self.logger.info(f"Error save_reports_to_config, query = {query}", error)
        finally:
            self.close_db(connection=connection, cursor=cursor)

    def save_schedule_to_config(self, config_suffix, new_schedule_hours, new_schedule_days, new_schedule_check, new_email, new_send_email):
        try:
            connection, cursor = self.open_db()
            str_schedule = self.array_to_string_for_db(new_schedule_days)
            str_config = self.string_to_string_for_db(config_suffix)
            query = f"update bot_params set schedule = {str_schedule} where config_suffix={str_config};"

            connection, cursor = self.open_db()
            self.execute_update(connection=connection, cursor=cursor, query=query)
        except (Exception, psycopg.Error) as error:
            self.logger.info(f"Error save_schedule_to_config, query = {query}", error)
        finally:
            self.close_db(connection=connection, cursor=cursor)

    @staticmethod
    def array_to_string_for_db(array_value):
        if len(array_value):
            return "'" + ", ".join([str(elem) for elem in array_value]) + "'"
        else:
            return "Null"

    @staticmethod
    def string_from_db_to_array(str_value):
        if str_value is None or str_value == 'Null' or not len(str_value):
            return []

        return str_value.replace(", ", ",").split(",")

    @staticmethod
    def string_to_string_for_db(str_value):
        return "'" + str(str_value) + "'"

    def execute_update(self, connection, cursor, query):
        self.logger.info(f"execute_update, query = {query}")
        cursor.execute(query)
        connection.commit()

    def open_db(self):
        conn_dict = psycopg.conninfo.conninfo_to_dict(self.pg_uri)
        connection = psycopg.connect(**conn_dict)
        cursor = connection.cursor()
        return connection, cursor

    @staticmethod
    def close_db(connection, cursor):
        if connection:
            if cursor:
                cursor.close()
            connection.close()
