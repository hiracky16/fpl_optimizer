from .const import IS_GCS, DATAMART_BUCKET
import pandas as pd

class Repository:
    def __init__(self):
        self.bucket = f'gs://{DATAMART_BUCKET}'

    def __csv_path(self, file):
        return f'{self.bucket}/{file}/data.csv' if IS_GCS else f'data/{file}.csv'

    def read_expected_elements(self):
        return pd.read_csv(self.__csv_path('expected_elements'))

    def read_current_next_event(self):
        return pd.read_csv(self.__csv_path('current_next_event'))
