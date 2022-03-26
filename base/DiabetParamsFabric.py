from base.DiabetConfigParser import DiabetConfigParser
from base.DiabetPostgresConfigParser import DiabetPostgresConfigParser


class DiabetParamsFabric:
    def __init__(self, is_heroku=False, logger=None, config_suffix=''):
        self.is_heroku = is_heroku
        self.logger = logger
        self.config_suffix = config_suffix

    def get_config_worker(self):
        if self.is_heroku:
            return DiabetPostgresConfigParser(self.logger, self.config_suffix)
        else:
            return DiabetConfigParser(self.logger, self.config_suffix)
