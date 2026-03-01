import os
import streamlit as st
import altair as at
import plotly.express as px
import numpy as np
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
    st.set_page_config(page_title="Olist Logistics ROI", page_icon="📈", layout="wide")
    st.title("📊 Logistics Cost Leakage Dashboard - Olist")
    st.subheader("Freight Cost Ratio by Brazilian State")

    data = process_data()
    
    with st.container():
        left_col, right_col = st.columns([1, 2])
        with left_col:
            min_pedidos = st.slider(
                "Minimal number of orders per State",
                min_value=int(data["order_id"].min()),
                max_value=int(data["order_id"].max()),
                value=500,
                step=50
            )

            filtered_data = data[data["order_id"] >= min_pedidos].copy()
            media_nacional = filtered_data["freight_ratio"].mean()
            idx_estado_critico = filtered_data["freight_ratio"].idxmax()
            estado_critico = filtered_data.loc[idx_estado_critico]
            filtered_data['chart_color'] = np.where(filtered_data.index == idx_estado_critico, "#e74c3c", "#196da7")
            plot_data = filtered_data.reset_index()
            state_col = "customer_state" if "customer_state" in plot_data.columns else "index"
            
            st.metric(
                label="📦 National Freight Average",
                value=f"{media_nacional:.2%}"
            )

            st.metric(
                label="🚨 Critical State",
                value=idx_estado_critico,
                delta=f"{estado_critico['freight_ratio']:.2%}",
                delta_color="inverse"
            )

        with right_col:
            bar_data = plot_data.sort_values(by="freight_ratio", ascending=False)
            
            fig_bar = px.bar(
                bar_data, 
                x=state_col, 
                y="freight_ratio", 
                color='chart_color',
                color_discrete_map="identity"
            )
            
            fig_bar.update_layout(
                showlegend=False,
                yaxis=dict(rangemode='tozero'),
                xaxis_title="",
                yaxis_title="Freight Ratio",
                margin=dict(l=0, r=0, t=30, b=0)
            )
            
            fig_bar.add_hline(y=media_nacional, line_dash="dash", line_color="gray", annotation_text="National Avg")
            
            st.plotly_chart(fig_bar, use_container_width=True)
    
    with st.container():
        left_col, right_col = st.columns([1, 2])
        with left_col:
            st.subheader("Top 10 States by Volume")
            
            top_10_vol = plot_data.sort_values(by="order_id", ascending=False).head(10)
            top_10_vol = top_10_vol.sort_values(by="order_id", ascending=True) 
            
            fig_hbar = px.bar(
                top_10_vol, 
                x="order_id", 
                y=state_col, 
                orientation="h"
            )
            
            fig_hbar.update_traces(marker_color="#196da7") 
            fig_hbar.update_layout(
                showlegend=False,
                xaxis_title="Total Orders",
                yaxis_title="",
                margin=dict(l=0, r=0, t=10, b=0)
            )
            st.plotly_chart(fig_hbar, use_container_width=True)
        
        with right_col:
            st.subheader("Raw Data")
            
            st.dataframe(
                bar_data,
                column_config={
                    "chart_color": None,
                    state_col: "State",
                    "price": st.column_config.NumberColumn("Avg Ticket", format="$ %.2f"),
                    "freight_value": st.column_config.NumberColumn("Avg Freight", format="$ %.2f"),
                    "freight_ratio": st.column_config.NumberColumn("Freight Ratio", format="%.4f"),
                    "order_id": st.column_config.NumberColumn("Total Orders", format="%d")
                },
                hide_index=True,
                use_container_width=True
            )

if __name__ == "__main__":
    main()