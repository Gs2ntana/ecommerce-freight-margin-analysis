import os
import streamlit as st
from data_loader import DataLoader
from data_analysis_service import DataAnalysisService

@st.cache_data
def process_data():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    folder = '../data'
    dir = os.path.join(current_dir, folder) 
    loader = DataLoader(dir)
    loaded_data = loader.load_csv_files()

    if not loaded_data:
        print("Encerrando: Não há dados para processar.")

    processor = DataAnalysisService(loaded_data)
    data = processor.analyze_freight_ratio()

    return data


def main():
    st.set_page_config(page_title="Olist Logistics ROI", layout="wide")
    st.title("📊 Dashboard de Sangramento Logístico - Olist")

    data = process_data()

    min_pedidos = st.slider(
        "Número Mínimo de Pedidos por Estado",
        min_value=int(data["order_id"].min()),
        max_value=int(data["order_id"].max()),
        value=500,
        step=50
    )

    filtered_data = data[data["order_id"] >= min_pedidos]

    media_nacional = filtered_data["freight_ratio"].mean()
    idx_estado_critico = filtered_data["freight_ratio"].idxmax()
    estado_critico = filtered_data.loc[idx_estado_critico]
    nome_estado = idx_estado_critico
    pior_ratio = estado_critico["freight_ratio"]

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            label="📦 Média Nacional de Frete",
            value=f"{media_nacional:.2%}"
        )

    with col2:
        st.metric(
            label="🚨 Estado Crítico (Pior Ratio)",
            value=nome_estado,
            delta=f"{pior_ratio:.2%}"
        )


    st.bar_chart(filtered_data.sort_values(by="freight_ratio", ascending=False).head(10), y="freight_ratio", y_label="Média de Frete por Estado")
    st.dataframe(filtered_data.sort_values(by="freight_ratio", ascending=False))

if __name__ == "__main__":
    main()