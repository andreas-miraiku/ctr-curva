import streamlit as st
import pandas as pd
import re
import plotly.graph_objects as go
import plotly.express as px

# Configuración de la página
st.set_page_config(layout="wide")

# Función para cargar el CSV
def load_csv():
    uploaded_file = st.file_uploader("Cargar archivo CSV", type="csv")
    if uploaded_file is not None:
        return pd.read_csv(uploaded_file, names=["Category", "Term", "Impressions", "Clicks", "Position", "CTR"], skiprows=1)
    return None

# Función para filtrar términos de marca
def filter_terms(data, brand_terms, min_impressions):
    brand_regex = '|'.join([re.escape(term.strip()) for term in brand_terms.split(',')])
    data = data[data['Impressions'] >= min_impressions]
    brand_data = data[data['Term'].str.contains(brand_regex, case=False, na=False)]
    non_brand_data = data[~data['Term'].str.contains(brand_regex, case=False, na=False)]
    return brand_data, non_brand_data

# Función para calcular y mostrar las curvas de CTR
def plot_ctr_curves(brand_grouped, non_brand_grouped):
    # Crear gráfico interactivo
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=brand_grouped['Position'], y=brand_grouped['avg_CTR'] * 100,
                             mode='lines+markers', name='Branded',
                             line_shape='spline', line=dict(width=8),
                             hoverinfo='text',
                             text=brand_grouped.apply(lambda row: f"Impressions: {row['total_impressions']}<br>Clicks: {row['total_clicks']}<br>Terms: {row['num_terms']}", axis=1)))
    fig.add_trace(go.Scatter(x=non_brand_grouped['Position'], y=non_brand_grouped['avg_CTR'] * 100,
                             mode='lines+markers', name='Non-Branded',
                             line_shape='spline', line=dict(width=8),
                             hoverinfo='text',
                             text=non_brand_grouped.apply(lambda row: f"Impressions: {row['total_impressions']}<br>Clicks: {row['total_clicks']}<br>Terms: {row['num_terms']}", axis=1)))

    fig.update_layout(title='CTR Curves',
                      xaxis_title='Position',
                      yaxis_title='Average CTR (%)')

    col1, col2 = st.columns([3, 1])
    with col1:
        st.plotly_chart(fig)

    with col2:
        st.subheader("Metrics")
        col3, col4 = st.columns(2)
        with col3:
            st.metric(label="Total Impressions (Branded)", value=f"{int(brand_grouped['total_impressions'].sum()):,}")
            st.metric(label="Total Clicks (Branded)", value=f"{int(brand_grouped['total_clicks'].sum()):,}")
            st.metric(label="Average CTR (Branded)", value=f"{brand_grouped['avg_CTR'].mean() * 100:.2f}%")
            st.metric(label="Total Terms (Branded)", value=f"{int(brand_grouped['num_terms'].sum()):,}")

        with col4:
            st.metric(label="Total Impressions (Non-Branded)", value=f"{int(non_brand_grouped['total_impressions'].sum()):,}")
            st.metric(label="Total Clicks (Non-Branded)", value=f"{int(non_brand_grouped['total_clicks'].sum()):,}")
            st.metric(label="Average CTR (Non-Branded)", value=f"{non_brand_grouped['avg_CTR'].mean() * 100:.2f}%")
            st.metric(label="Total Terms (Non-Branded)", value=f"{int(non_brand_grouped['num_terms'].sum()):,}")

# Función para mostrar el CTR medio de posiciones 1 a 10
def show_avg_ctr_by_position(brand_grouped, non_brand_grouped):
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Average CTR by Position (1-10) - Branded")
        brand_grouped['avg_CTR'] = brand_grouped['avg_CTR'] * 100
        st.dataframe(brand_grouped.round(2))

    with col2:
        st.subheader("Average CTR by Position (1-10) - Non-Branded")
        non_brand_grouped['avg_CTR'] = non_brand_grouped['avg_CTR'] * 100
        st.dataframe(non_brand_grouped.round(2))

    # Gráficas de barras para el volumen de Queries
    col3, col4 = st.columns(2)
    with col3:
        st.subheader("Volume of Queries by Position - Branded")
        fig = px.bar(brand_grouped, x='Position', y='num_terms', labels={'num_terms': 'Number of Queries'})
        st.plotly_chart(fig)

    with col4:
        st.subheader("Volume of Queries by Position - Non-Branded")
        fig = px.bar(non_brand_grouped, x='Position', y='num_terms', labels={'num_terms': 'Number of Queries'})
        st.plotly_chart(fig)

# Función para mostrar las tablas de métricas
def show_top_terms(brand_data, non_brand_data):
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Top 100 Branded Terms")
        brand_data['Avg Position'] = brand_data['Position'].round(2)
        brand_data['CTR'] = brand_data['CTR'] * 100
        st.dataframe(brand_data.nlargest(100, 'Impressions')[['Term', 'Impressions', 'Clicks', 'CTR', 'Avg Position']].round(2))

    with col2:
        st.subheader("Top 100 Non-Branded Terms")
        non_brand_data['Avg Position'] = non_brand_data['Position'].round(2)
        non_brand_data['CTR'] = non_brand_data['CTR'] * 100
        st.dataframe(non_brand_data.nlargest(100, 'Impressions')[['Term', 'Impressions', 'Clicks', 'CTR', 'Avg Position']].round(2))

# Interfaz de Streamlit
def main():
    st.sidebar.title("Análisis de CTR de Términos de Marca")
    st.sidebar.write("Esta aplicación permite analizar el CTR de términos de marca y no marca.")
    st.sidebar.write("### Herramientas Utilizadas:")
    st.sidebar.write("- Streamlit")
    st.sidebar.write("- Pandas")
    st.sidebar.write("- Plotly")

    st.title("CTR Analysis Dashboard")
    data = load_csv()

    if data is not None:
        brand_terms = st.text_input("Introduce los términos de marca separados por comas")
        min_impressions = st.slider("Mínimo de impresiones", 0, 10000, 1000)

        if brand_terms:
            brand_data, non_brand_data = filter_terms(data, brand_terms, min_impressions)
            brand_data['Position'] = brand_data['Position'].round()
            non_brand_data['Position'] = non_brand_data['Position'].round()

            # Filtrar posiciones de 1 a 10
            brand_data = brand_data[brand_data['Position'] <= 10]
            non_brand_data = non_brand_data[non_brand_data['Position'] <= 10]

            brand_grouped = brand_data.groupby('Position').apply(
                lambda x: pd.Series({
                    'avg_CTR': (x['CTR'] * x['Impressions']).sum() / x['Impressions'].sum(),
                    'num_terms': len(x),
                    'total_impressions': x['Impressions'].sum(),
                    'total_clicks': x['Clicks'].sum()
                })
            ).reset_index()

            non_brand_grouped = non_brand_data.groupby('Position').apply(
                lambda x: pd.Series({
                    'avg_CTR': (x['CTR'] * x['Impressions']).sum() / x['Impressions'].sum(),
                    'num_terms': len(x),
                    'total_impressions': x['Impressions'].sum(),
                    'total_clicks': x['Clicks'].sum()
                })
            ).reset_index()

            plot_ctr_curves(brand_grouped, non_brand_grouped)
            show_avg_ctr_by_position(brand_grouped, non_brand_grouped)
            show_top_terms(brand_data, non_brand_data)

if __name__ == "__main__":
    main()