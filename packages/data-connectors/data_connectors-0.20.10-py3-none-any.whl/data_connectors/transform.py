import pendulum
import pandas as pd


class Transform:
    
    def __init__(self, df):
        self.df = df

    def lower_case_columns(self):
        self.df.columns = self.df.columns.str.lower().str.replace(' ', '_')
        return self

    def add_updated_timestamp(self):
        # Add a UTC timestamp
        self.df['updated_at'] = pendulum.now().strftime('%Y-%m-%d %H:%M:%S %p')
        self.df['updated_at'] = self.df['updated_at'].apply(pd.to_datetime, format='%Y-%m-%d %H:%M:%S %p', utc=True)
        return self