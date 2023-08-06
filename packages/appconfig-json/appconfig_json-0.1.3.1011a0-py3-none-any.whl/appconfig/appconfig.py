import logging
import logging.config
import pathlib
import json
import os
import errno


class AppConfig(object):

    def __init__(self):
        
        self._logger = None
        self._config = None
        self._root_path = None
    

    def init(self, 
                    root_path = None, 
                    config_group: str = None, 
                    config_file: str = 'config/private.configdef.json',
                    logger=None,
                    logger_config_file: str = 'config/logging.conf',
                    logger_config_section: str = 'dbg' 
                    ):
        
        self._logger = None
        self._config = None
    
        if (root_path is None):
            self._root_path = pathlib.Path('.')
        else:
            self._root_path = pathlib.Path(root_path)
            # TODO Check if the path exists

        # print(f'Root path {root_path}')

        self.init_logging(logger, logger_config_file, logger_config_section)    

        self._logger.debug('ApiClient.__init__')
        self.read_json(config_group, config_file)

    
    
    def init_logging(self, 
                    logger=None,
                    logger_config_file: str = 'config/logging.conf',
                    logger_config_section: str = 'dbg' 
                    ):
        if(not self._logger is None):
            return

        if logger is None:

            logfile = self._root_path.joinpath(logger_config_file)

            # Check if the file exists, otherwise rise exception
            # print(f'logfile {logfile}')

            if(not logfile.is_file()):
                # print(f"File {logfile} not found")
                raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), logfile)
                

            logging.config.fileConfig(logfile)
            logger = logging.getLogger(logger_config_section)
        self._logger = logger


    def read_json(self,
                    config_group: str = None,
                    config_file: str = 'config/private.configdef.json'):
        """
        Read following values from config_file (JSON) from section config_group
        Example of config_file content (config_group is test):
            "test": {
                "section_1": {
               "key": "value"
        },
                
        Arguments:
            config_group {str} -- name of main group that contains sheet_id, event_sheet_name.
                                  If it's None, it looks for "active_config" key in that config file
            config_file {str} -- relative path+fname to config file
        """

        with open(self._root_path.joinpath(config_file), 'r', encoding='utf-8') as cfg_file:
            cfg_values = json.load(cfg_file)
            if (not config_group):
                config_group = cfg_values['active_config']
            self._config = cfg_values[config_group]
            self._logger.debug('Opening config file')
            self._logger.debug('cfg_values= {}'.format(cfg_values))

    @property
    def logger(self):
        return self._logger


    @property
    def config(self):
        self._logger.debug('config {}'.format(self._config))
        return self._config

app_config = AppConfig()
