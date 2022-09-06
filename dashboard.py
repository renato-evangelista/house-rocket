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

    # Change Types

    # change the "date" column from type "object" to "datetime"
    data['date'] = pd.to_datetime(data['date'])

    # change the "yr_built" and "yr_renovated" columns from type "int" to "datetime"
    data['yr_built'] = pd.to_datetime(data['yr_built'], format='%Y')

    # if "yr_renovated" value is equal to "0", replace with "1900"
    data['yr_renovated'] = data['yr_renovated'].apply(lambda x: pd.to_datetime('1900', format='%Y') if x == 0 else
    pd.to_datetime(x, format='%Y'))

    # change the "waterfront" column to "str" type
    data['waterfront'] = data['waterfront'].astype(str)

    # change the "condition" column to "str" type
    data['condition'] = data['condition'].astype(str)


    # Line Filtering

    # remove row with outlier from the "bedrooms" column
    data = data.drop(data[data['bedrooms'] == 33].index)

    # sort values by 'id' and 'date'
    data = data.sort_values(['id', 'date'])

    # keep only recent rows by dropping previous dates
    data = data.drop_duplicates(subset=['id'], keep='last').reset_index()

    # drop extra index column
    data = data.drop(columns=['index'])


    # Column Selection

    # select columns to drop
    cols_drop = ['sqft_living15', 'sqft_lot15']

    # drop selected columns
    data = data.drop(columns=cols_drop)


    # Hypotheses

    # H1
    # add new column with waterfront option ("yes" or "no")
    data['waterfront_option'] = data['waterfront'].apply(lambda x: 'yes' if x == '1' else 'no')

    # H2
    # create new column with before and after 1955 values
    data['is_before_1955'] = data['yr_built'].apply(lambda x: 'before' if x.year < 1955 else 'after')

    # H3
    # create 'basement' column
    data['basement_option'] = data['sqft_basement'].apply(lambda x: 'no basement' if x == 0 else 'basement')

    # H4
    # create 'year' column
    data['year'] = data['date'].dt.year

    # H5
    # create new column with year-month format
    data['month_year'] = data['date'].dt.strftime('%Y-%m')

    # H6
    # create new column with floor amount
    data['is_floor'] = data['floors'].apply(lambda x: 'ground floor' if x == 1 else 'more floors')

    # H7
    # create month column
    data['month'] = data['date'].dt.strftime('%m')

    # change from object format to int
    data['month'] = data['month'].astype('int64')

    # create column with season
    data['season'] = data['month'].apply(lambda x: 'Summer' if 6 <= x <= 8 else
    'Fall' if 9 <= x <= 11 else
    'Winter' if (x == 12) or (x == 1) or (x == 2) else
    'Spring' if 3 <= x <= 5 else None)

    # H8
    # create column with renovation option
    data['is_renovated'] = data['yr_renovated'].apply(
        lambda x: 'not renovated' if x.strftime('%Y') == '1900' else 'renovated')

    # H9
    # create column with before and after 2010 renovation values
    data['renovated_2010'] = data['yr_renovated'].apply(lambda x: 'before' if int(x.strftime('%Y')) < 2010 else 'after')

    # H10
    # create column with condition type
    data['condition_type'] = data['condition'].apply(lambda x: 'good' if int(x) >= 4 else 'bad')

    # H11
    # create column with bedroom amount
    data['bedrooms_amount'] = data['bedrooms'].apply(lambda x: 'up to 2' if x <= 2 else 'more than 2')

    # H12
    # create column with bathroom amount
    data['bathrooms_amount'] = data['bathrooms'].apply(lambda x: 'up to 1' if x <= 1 else 'more than 1')

    return data

def overview_data(data):

    f_attributes = st.sidebar.multiselect('Enter columns', data.columns)
    f_zipcode = st.sidebar.multiselect('Enter zipcode', data['zipcode'].unique())
    st.title('House Rocket Data')
    #st.image("/home/renato/PycharmProjects/zero_ao_ds/Sale-1.jpg", width = 500)
    st.write('House Rocket é uma empresa fictícia de real estate localizada em King County, Seattle. Seu principal negócio é voltado para a revenda de imóveis naquela região. Porém, ultimamente a empresa está passando por dificuldades financeiras porque não consegue encontrar bons imóveis para comprar e, posteriormente, revender. Portanto, os objetivos dessa análise de dados  são encontrar bons imóveis para comprar e decidir o melhor momento e preço para vendê-los.')


    b_dataset = st.checkbox('Display Dataset')
    if b_dataset:
        st.dataframe(data)

    # Hypotheses

    st.title('Hypotheses')

    c1, c2 = st.columns((1, 1))

    #H1
    c1.write('H1) Imóveis que possuem vista para a água são, em média, 30% mais caros.')

    # group by 'waterfront_option' and take average price
    grouped = data[['waterfront_option', 'price']].groupby('waterfront_option').mean().reset_index()

    c1.bar_chart(grouped, x='waterfront_option', y='price')

    #H2
    c2.write('H2) Imóveis com data de construção menor que 1955 são, em média, 50% mais baratos')

    # group data by "before" and "after" year 1955
    grouped = data[['is_before_1955', 'price']].groupby('is_before_1955').mean().reset_index()

    c2.bar_chart(grouped, x='is_before_1955', y='price')


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