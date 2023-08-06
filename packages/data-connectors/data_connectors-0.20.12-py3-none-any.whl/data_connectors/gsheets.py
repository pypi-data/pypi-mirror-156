import os
import pygsheets
from dotenv import load_dotenv
load_dotenv()

class Gsheets:
    """
    Pass in a service account file path and query data stored in Google Sheets
    Example: Gsheets('SPREADSHEET').query('WORKSHEET')
    """
    def __init__(self, spreadsheet):
        self.client = pygsheets.authorize(service_file=(os.getenv("GSHEETS_SERVICE_ACCOUNT")))
        self.spreadsheet = os.getenv(spreadsheet)

    def query(self, worksheet):
        """
        Returns results of spreadsheet, worksheet as a pandas DataFrame
        Spreadsheet is stored as env var
        Worksheet is passed in as plain text
        """        
        return self.client.open_by_key(self.spreadsheet)\
                          .worksheet_by_title(worksheet).get_as_df()