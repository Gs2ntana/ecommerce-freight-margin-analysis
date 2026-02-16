import pandas as pd
from typing import Dict

class DataAnalysisService:
    def __init__(self, datasets: Dict[str, pd.DataFrame]):
        self.datasets = datasets

    def print_summaries(self):
        for name, df in self.datasets.items():
            print(f"Dataset: {name} | Shape: {df.shape}")
            print(f"Dataset: {name} | Columns: {df.columns}")

    def find_relationships(self, base_table_name: str):
        if base_table_name not in self.datasets:
            print(f"Erro: Tabela base '{base_table_name}' não encontrada no dicionário.")
            return
        
        df_base = self.datasets[base_table_name]
        colunas_base = set(df_base.columns)
        print(f"Analisando relacionamentos para a tabela base '{base_table_name}'...")
        encontrou_algo = False

        for name, df_other in self.datasets.items():
            if name == base_table_name:
                continue

            colunas_outra = set(df_other.columns)
            colunas_em_comum = colunas_base.intersection(colunas_outra)
            
            if colunas_em_comum:
                encontrou_algo = True
                print(f"   ➡ Vínculo com '{name}': {colunas_em_comum}")
        
        if not encontrou_algo:
            print("   Nenhum relacionamento óbvio encontrado pelos nomes das colunas.")
    
    def analyze_freight_ratio(self):
        required_tables = ['olist_orders_dataset', 'olist_order_items_dataset', 'olist_customers_dataset']
        for table in required_tables:
            if table not in self.datasets:
                print(f"Erro: Tabela '{table}' necessária para análise não foi encontrada.")
                return
            
        # Select * FROM olist_orders_dataset orders INNER JOIN olist_order_items_dataset items ON orders.order_id = items.order_id
        df_temp = pd.merge(self.datasets['olist_orders_dataset'], self.datasets['olist_order_items_dataset'], on='order_id', how='inner')
        
        #Select * FROM df_temp table INNER JOIN olist_customers_dataset customers ON table.customer_id = customers.customer_id
        df_final = pd.merge(df_temp, self.datasets['olist_customers_dataset'], on='customer_id', how='inner')

        df_grouped = df_final.groupby(['customer_state']).agg({
            'price': 'mean', 
            'freight_value': 'mean', 
            'order_id': 'count'
        })

        df_grouped['freight_ratio'] = df_grouped['freight_value'] / df_grouped['price']
        #Se o slider for funcionar comente o df_filtered
        #df_filtered = df_grouped[df_grouped['order_id'] > 100].sort_values(by='freight_ratio', ascending=False)
        
        return df_grouped