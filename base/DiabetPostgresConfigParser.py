import os
import psycopg

from base.DiabetParamsWorker import DiabetParamsWorker


class DiabetPostgresConfigParser(DiabetParamsWorker):
    def __init__(self, logger, config_suffix=''):
        super().__init__(logger, config_suffix)

        self.db_name = os.environ.get("DB_NAME")
        self.db_user = os.environ.get("DB_USER")
        self.db_password = os.environ.get("DB_PASSWORD")
        self.pg_uri = os.environ.get("DB_URI")

    def get_values_from_config(self, config_suffix=''):
        try:
            connection, cursor = self.open_db()
            cursor.execute("CREATE TABLE IF NOT EXISTS bot_params (id serial PRIMARY KEY, config_suffix text, "
                           "positions text, districts text, email text, send_email boolean, send_full_report boolean, schedule text);")
            connection.commit()
            cursor.execute(f"select positions, districts, email, send_email, send_full_report, schedule from bot_params where config_suffix={config_suffix};")
            result = cursor.fetchall()
            if result and len(result) == 6:
                self.logger.info(f"get_values_from_config result = {result}")
                values_result = str(result[0]).replace(", ", ",").split(","), str(result[1]).replace(", ", ",").split(","), str(result[2]).replace(", ", ",").split(","),  result[3],  result[4], str(result[5]).replace(", ", ",").split(",")
                self.close_db(connection=connection, cursor=cursor)
                self.logger.info(f"get_values_from_config values_result = {values_result}")
                return values_result
            else:
                self.init_config_with_default_values(config_suffix)
        except (Exception, psycopg.Error) as error:
            self.logger.info("Error in update operation", error)
        finally:
            self.close_db(connection=connection, cursor=cursor)

        return self.default_positions, self.default_districts, "", False, True, self.default_schedule

    def init_config_with_default_values(self, config_suffix):
        config_positions = ", ".join([str(elem) for elem in self.default_positions])
        config_districts = ", ".join([str(elem) for elem in self.default_districts])
        config_email = ""
        send_email = False
        send_full_report = True
        config_schedule = ", ".join([str(elem) for elem in self.default_schedule])

        connection, cursor = self.open_db()
        self.execute_update(connection=connection, cursor=cursor, query=f"insert into bot_params (config_suffix, positions, districts, email, send_email, send_full_report, schedule) values({config_suffix}, {config_positions}, {config_districts}, {config_email}, {send_email}, {send_full_report}, {config_schedule});")

    def save_positions_to_config(self, config_suffix, new_positions):
        try:
            connection, cursor = self.open_db()
            str_positions = ", ".join([str(elem) for elem in new_positions])
            self.execute_update(connection=connection, cursor=cursor, query=f"update bot_params set positions = {str_positions}, where config_suffix={config_suffix};")
        except (Exception, psycopg.Error) as error:
            self.logger.info("Error in update operation", error)
        finally:
            self.close_db(connection=connection, cursor=cursor)

    def save_districts_to_config(self, config_suffix, new_districts):
        try:
            connection, cursor = self.open_db()
            str_districts = ", ".join([str(elem) for elem in new_districts])
            self.execute_update(connection=connection, cursor=cursor, query=f"update bot_params set districts = {str_districts}, where config_suffix={config_suffix};")
        except (Exception, psycopg.Error) as error:
            self.logger.info("Error in update operation", error)
        finally:
            self.close_db(connection=connection, cursor=cursor)

    def save_reports_to_config(self, config_suffix, new_email, new_send_email, new_send_full_report):
        try:
            connection, cursor = self.open_db()
            str_emails = ", ".join([str(elem) for elem in new_email])
            self.execute_update(connection=connection, cursor=cursor, query=f"update bot_params set email = {str_emails}, send_email = {new_send_email}, send_full_report = {new_send_full_report} where config_suffix={config_suffix};")
        except (Exception, psycopg.Error) as error:
            self.logger.info("Error in update operation", error)
        finally:
            self.close_db(connection=connection, cursor=cursor)

    def save_schedule_to_config(self, config_suffix, new_schedule):
        try:
            connection, cursor = self.open_db()
            str_schedule = ", ".join([str(elem) for elem in new_schedule])
            self.execute_update(connection=connection, cursor=cursor, query=f"update bot_params set schedule = {str_schedule}, where config_suffix={config_suffix};")
        except (Exception, psycopg.Error) as error:
            self.logger.info("Error in update operation", error)
        finally:
            self.close_db(connection=connection, cursor=cursor)

    @staticmethod
    def execute_update(connection, cursor, query):
        cursor.execute(query)
        connection.commit()

    def open_db(self):
        self.logger.info(f"open_db {self.db_name}, {self.db_user}, {self.db_password}")
        conn_dict = psycopg.conninfo.conninfo_to_dict(self.pg_uri)
        connection = psycopg.connect(**conn_dict)
        #connection = psycopg2.connect(dbname=self.db_name, user=self.db_user, password=self.db_password)
        cursor = connection.cursor()
        return connection, cursor

    @staticmethod
    def close_db(connection, cursor):
        if connection:
            if cursor:
                cursor.close()
            connection.close()
