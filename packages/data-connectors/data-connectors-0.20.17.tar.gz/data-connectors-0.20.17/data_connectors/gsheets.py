import os
import pygsheets
import pandas as pd

from .creds import load_creds
load_creds()

class Gsheets:
    """
    Pass in a service account file path and query data stored in Google Sheets
    Example: Gsheets('SPREADSHEET').query('WORKSHEET')
    """
    def __init__(self, spreadsheet):
        self.client = pygsheets.authorize(service_file=(os.getenv("GSHEETS_SERVICE_ACCOUNT")))
        self.spreadsheet = os.getenv(spreadsheet)

    def query(self, worksheet, start_cell=None, end_cell=None):
        """
        Returns results of spreadsheet, worksheet as a pandas DataFrame
        Spreadsheet is stored as env var
        Worksheet is passed in as plain text
        """        
        ws = self.client.open_by_key(self.spreadsheet).worksheet_by_title(worksheet)
        df = ws.get_as_df(start=start_cell, end=end_cell)
        print(f"{self.spreadsheet.title}.{worksheet}: Downloaded {df.shape} shape")
        return df

    # If get_as_df does not work, use this instead
    def select_all_values(self, worksheet):
        return pd.DataFrame(self.spreadsheet.worksheet_by_title(worksheet).get_all_records())

    def write_df(self, df, worksheet, start_cell='A1'):
        self.spreadsheet.worksheet_by_title(worksheet).set_dataframe(df, start=start_cell)