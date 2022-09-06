import geopandas
import streamlit as st
import pandas as pd
import numpy as np
import folium

from streamlit_folium import folium_static
from folium.plugins import MarkerCluster

import plotly.express as px

from datetime import datetime

st.set_page_config(layout='wide')

@st.cache(allow_output_mutation=True)
def get_data(path):
    data = pd.read_csv(path)
    return data

@st.cache(allow_output_mutation=True)
def get_geofile(url):
    geofile = geopandas.read_file(url)
    return geofile

def set_feature(data):
    # add new features
    data['price_m2'] = data['price'] / data['sqft_lot']
    return data

def overview_data(data):

    f_attributes = st.sidebar.multiselect('Enter columns', data.columns)
    f_zipcode = st.sidebar.multiselect('Enter zipcode', data['zipcode'].unique())
    st.title('House Rocket Data')
    st.image("/home/renato/PycharmProjects/zero_ao_ds/Sale-1.jpg", width = 500)
    st.write('House Rocket é uma empresa fictícia de real estate localizada em King County, Seattle. Seu principal negócio é voltado para a revenda de imóveis naquela região. Porém, ultimamente a empresa está passando por dificuldades financeiras porque não consegue encontrar bons imóveis para comprar e, posteriormente, revender. Portanto, os objetivos dessa análise de dados  são encontrar bons imóveis para comprar e decidir o melhor momento e preço para vendê-los.')

    b_dataset = st.checkbox('Display Dataset')
    if b_dataset:
        st.dataframe(data)


    st.title('Hypotheses')
    c1, c2 = st.columns((1, 1))

    c1.write('H1) Imóveis que possuem vista para a água são, em média, 30% mais caros.')
    c1.image("/home/renato/PycharmProjects/zero_ao_ds/hip1.png")

    c2.write('H2) Imóveis com data de construção menor que 1955 são, em média, 50% mais baratos.')
    c2.image("/home/renato/PycharmProjects/zero_ao_ds/hip2.png")

    c1.write('H3) Imóveis com porão são, em média, 20% mais caros.')
    c1.image('/home/renato/PycharmProjects/zero_ao_ds/hip3.png')
    return None

def portfolio_density(data, geofile):

    st.title('Region Overview')

    c1, c2 = st.columns((1, 1))
    c1.header('Portfolio Density')

    df = data.sample(10)

    # Base Map - Folium
    density_map = folium.Map(location=[data['lat'].mean(),
                                       data['long'].mean()],
                             default_zoom_start=15)

    marker_cluster = MarkerCluster().add_to(density_map)
    for name, row in df.iterrows():
        folium.Marker([row['lat'], row['long']],
                      popup='Sold R${0} on: {1}. Features: {2} sqft, {3} bedrooms, {4} bathrooms, year built: {5}'.format(
                          row['price'],
                          row['date'],
                          row['sqft_living'],
                          row['bedrooms'],
                          row['bathrooms'],
                          row['yr_built'])).add_to(marker_cluster)

    with c1:
        folium_static(density_map)

    # Region Price Map
    c2.header('Price Density')

    df = data[['price', 'zipcode']].groupby('zipcode').mean().reset_index()
    df.columns = ['ZIP', 'PRICE']

    geofile = geofile[geofile['ZIP'].isin(df['ZIP'].tolist())]

    region_price_map = folium.Map(location=[data['lat'].mean(),
                                            data['long'].mean()],
                                  default_zoom_start=15)

    region_price_map.choropleth(data=df,
                                geo_data=geofile,
                                columns=['ZIP', 'PRICE'],
                                key_on='feature.properties.ZIP',
                                fill_color='YlOrRd',
                                fill_opacity=0.7,
                                line_opacity=0.2,
                                legend_name='AVG PRICE')

    with c2:
        folium_static(region_price_map)

    return None

def commercial_distribution(data):

    st.sidebar.title('Commercial Options')
    st.title('Commercial Attributes')

    # ----- Average price per year
    data['date'] = pd.to_datetime(data['date']).dt.strftime('%Y-%m-%d')

    # filters
    min_year_built = int(data['yr_built'].min())
    max_year_built = int(data['yr_built'].max())

    st.sidebar.subheader('Select Max Year Built')
    f_year_built = st.sidebar.slider('Year Built', min_year_built,
                                     max_year_built,
                                     min_year_built)

    st.header('Average Price per Year Built')

    # data selection
    df = data.loc[data['yr_built'] < f_year_built]
    df = data[['yr_built', 'price']].groupby('yr_built').mean().reset_index()

    # plot
    fig = px.line(df, x='yr_built', y='price')
    st.plotly_chart(fig, use_container_width=True)

    # ----- Average price per day
    st.header('Average Price per day')
    st.sidebar.subheader('Select Max Date')

    # filters
    min_date = datetime.strptime(data['date'].min(), '%Y-%m-%d')
    max_date = datetime.strptime(data['date'].max(), '%Y-%m-%d')

    f_date = st.sidebar.slider('Date', min_date, max_date, min_date)

    # data filtering
    data['date'] = pd.to_datetime(data['date'])
    df = data.loc[data['date'] < f_date]
    df = data[['date', 'price']].groupby('date').mean().reset_index()

    # plot
    fig = px.line(df, x='date', y='price')
    st.plotly_chart(fig, use_container_width=True)

    # ----- Histograma
    st.header('Price Distribution')
    st.sidebar.subheader('Select Max Price')

    # filter
    min_price = int(data['price'].max())
    max_price = int(data['price'].min())
    avg_price = int(data['price'].mean())

    # data filtering
    f_price = st.sidebar.slider('Price', min_price, max_price, avg_price)
    df = data.loc[data['price'] < f_price]

    # data plot
    fig = px.histogram(df, x='price', nbins=50)
    st.plotly_chart(fig, use_container_width=True)

    return None

def attributes_distribution(data):

    st.sidebar.title('Attributes Options')
    st.title('House Attributes')

    # filters
    f_bedrooms = st.sidebar.selectbox('Max number of bedrooms', sorted(set(data['bedrooms'].unique())))
    f_bathrooms = st.sidebar.selectbox('Max number of bathrooms', sorted(set(data['bathrooms'].unique())))

    c1, c2 = st.columns(2)

    # House per bedrooms
    c1.header('Houses per bedrooms')
    df = data[data['bedrooms'] < f_bedrooms]
    fig = px.histogram(df, x='bedrooms', nbins=19)
    c1.plotly_chart(fig, use_container_width=True)

    # House per bathrooms
    c2.header('Houses per bathrooms')
    df = data[data['bathrooms'] < f_bathrooms]
    fig = px.histogram(data, x='bathrooms', nbins=19)
    c2.plotly_chart(fig, use_container_width=True)

    # filters
    f_floors = st.sidebar.selectbox('Max number of floor', sorted(set(data['floors'].unique())))
    f_waterview = st.sidebar.checkbox('Only Houses With Waterview')

    c1, c2 = st.columns(2)

    # House per floors
    c1.header('Houses per Floor')
    df = data[data['floors'] < f_floors]

    # plot
    fig = px.histogram(data, x='floors', nbins=19)
    c1.plotly_chart(fig, use_container_width=True)

    # House per waterview
    if f_waterview:
        df = data[data['waterfront'] == 1]
    else:
        df = data.copy()

    # plot
    fig = px.histogram(df, x='waterfront', nbins=10)
    c2.plotly_chart(fig, use_container_width=True)

    return None


if __name__ == "__main__":
    # ETL
    # data extraction

    path = 'kc_house_data.csv'
    url = 'https://opendata.arcgis.com/datasets/83fc2e72903343aabff6de8cb445b81c_2.geojson'

    data = get_data(path)
    geofile = get_geofile(url)

    # transformation

    data = set_feature(data)

    overview_data(data)

    portfolio_density(data, geofile)

    commercial_distribution(data)

    attributes_distribution(data)