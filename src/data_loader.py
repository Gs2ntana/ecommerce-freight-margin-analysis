import pandas as pd
import os
import glob
from typing import Dict

class DataLoader:
    def __init__(self, directory_path: str):
        self.directory_path = directory_path

    def load_csv_files(self) -> Dict[str, pd.DataFrame]:
        file_pattern = os.path.join(self.directory_path, "*.csv")
        files = glob.glob(file_pattern)
        
        datasets = {}
        config_columns = {
            'olist_customers_dataset': ['customer_id', 'customer_state'],
            'olist_orders_dataset': ['order_id', 'customer_id'],
            'olist_order_items_dataset': ['price', 'freight_value', 'order_id']
        }
       
        if not files:
            print(f"[DataLoader] Nenhum arquivo .csv encontrado em {self.directory_path}")
            return datasets

        for file in files:
            try:
                file_name = os.path.splitext(os.path.basename(file))[0]
                if file_name in config_columns:
                    columns = config_columns[file_name]
                    datasets[file_name] = pd.read_csv(file, usecols= columns)
            except Exception as e:
                print(f"Erro ao carregar {file}: {e}")
        return datasets