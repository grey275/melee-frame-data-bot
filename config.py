import yaml
import re


class Config:
    """
    Retrieves and stores info from the user's configuration file.
    Also computes the spreadsheet Id from the given sheet url.
    """
    def __init__(self, config_file="config.yaml"):

        with open(config_file) as f:
            config_dict = yaml.load(f.read())

        self.__dict__.update(**config_dict)
        self.sheet_id = self.getSpreadsheetID(self.sheet_url)

        self.config_file = config_file

    def getSpreadsheetID(self, url):
        start = re.search("id\=", url).end()
        return url[start:]


conf = Config()
