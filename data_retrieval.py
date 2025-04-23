import pickle
import pandas as pd
import os
from ecbdata import ecbdata


class DataRetrieval:
    def __init__(self, pickle_file_path):
        self.pickle_file_path = pickle_file_path
        self.DICT_data = {}  # Retrieved ECB series
        self.key_name_mapping = {}  # For sidebar name display
        self.raw_data = None  # Full reference table from pickle
        self.load_pickle_data()

    def load_pickle_data(self):
        try:
            with open(self.pickle_file_path, "rb") as file:
                data = pickle.load(file)

                # Consolidate multiple sheets into one DataFrame if needed
                if isinstance(data, dict):
                    frames = []
                    for sheet_name, df in data.items():
                        if isinstance(df, pd.DataFrame) and 'KEY' in df.columns:
                            frames.append(df)
                    self.raw_data = pd.concat(frames).dropna(subset=["KEY"]).reset_index(drop=True)

                elif isinstance(data, pd.DataFrame):
                    self.raw_data = data.dropna(subset=["KEY"]).reset_index(drop=True)
                else:
                    print("❌ Pickle structure not supported.")
                    self.raw_data = pd.DataFrame()

                if not self.raw_data.empty and "KEY" in self.raw_data.columns and "Name" in self.raw_data.columns:
                    self.create_key_name_mapping(self.raw_data)
                    print("✅ Raw data loaded and cleaned.")
                else:
                    print("❌ Required columns 'KEY' and 'Name' not found.")
        except Exception as e:
            print(f"❌ Error loading Pickle file: {e}")
            self.raw_data = pd.DataFrame()

    def create_key_name_mapping(self, df):
        self.key_name_mapping = dict(zip(df["KEY"], df["Name"]))
        print("✅ Key-name mapping created successfully.")

    def fetch_data(self, ST_key, start_date=None):
        try:
            print(f"🌍 Fetching data from ECB for key: {ST_key}")
            df = ecbdata.get_series(ST_key, start=start_date)
            df["TIME_PERIOD"] = pd.to_datetime(df["TIME_PERIOD"], errors='coerce')
            df.dropna(subset=["TIME_PERIOD"], inplace=True)
            self.DICT_data[ST_key] = df
            print(f"✅ Data fetched for key: {ST_key}")
        except Exception as e:
            print(f"❌ Error fetching data for key {ST_key}: {e}")

    def get_name_from_key(self, key):
        return self.key_name_mapping.get(key, "❓ Unknown")

    def get_key_from_name(self, name):
        reverse_map = {v: k for k, v in self.key_name_mapping.items()}
        return reverse_map.get(name, None)
