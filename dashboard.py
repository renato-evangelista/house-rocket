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
    col1, col2, col3 = st.columns(3)
    col2.image('sale.jpg', width=300)


    st.title('House Rocket Data')
    st.write('House Rocket é uma empresa fictícia de real estate localizada em King County, Seattle. Seu principal negócio é voltado para a revenda de imóveis naquela região. Porém, ultimamente a empresa está passando por dificuldades financeiras porque não consegue encontrar bons imóveis para comprar e, posteriormente, revender. Portanto, os objetivos dessa análise de dados  são encontrar bons imóveis para comprar e decidir o melhor momento e preço para vendê-los.')

    b_dataset = st.checkbox('Display Dataset')
    if b_dataset:
        st.dataframe(data)

    # Hypotheses

    st.title('Hipóteses')

    c1, c2 = st.columns((1, 1))


    #H1
    c1.write('H1) Imóveis que possuem vista para a água são, em média, 30% mais caros.')
    # group by 'waterfront_option' and take average price
    grouped = data[['waterfront_option', 'price']].groupby('waterfront_option').mean().reset_index()
    # plot
    c1.bar_chart(grouped, x='waterfront_option', y='price')

    #H2
    c2.write('H2) Imóveis com data de construção menor que 1955 são, em média, 50% mais baratos')
    # group data by "before" and "after" year 1955
    grouped = data[['is_before_1955', 'price']].groupby('is_before_1955').mean().reset_index()
    # plot
    c2.bar_chart(grouped, x='is_before_1955', y='price')

    #H3
    c1.write('H3) Imóveis com porão são, em média, 20% mais caros.')
    # group by basement
    grouped = data[['basement_option', 'price']].groupby('basement_option').mean().reset_index()
    # plot
    c1.bar_chart(grouped, x='basement_option', y='price')

    #H4
    c2.write('H4) O crescimento do preço dos imóveis year over year (YoY) é de 10%.')
    # group by year
    grouped = data[['year', 'price']].groupby('year').mean().reset_index()
    # plot
    c2.bar_chart(grouped, x='year', y='price')

    #H5
    c1.write('H5) Imóveis com 3 banheiros tem um crescimento month over month (MoM) de 15%.')
    # group by year-month and return the mean value
    grouped = data[['price', 'month_year']].groupby('month_year').mean().reset_index()
    # plot
    c1.line_chart(grouped, x='month_year', y='price')

    #H6
    c2.write('H6) Imóveis térreos são, em média, 50% mais baratos do que imóveis com andar.')
    # group by floor and return mean values
    grouped = data[['price', 'is_floor']].groupby('is_floor').mean().reset_index()
    # plot
    c2.bar_chart(grouped, x='is_floor', y='price')

    #H7
    c1.write('H7) O preço dos imóveis no inverno é, em média, 20% mais barato do que no verão.')
    # group by season and return mean price
    grouped = data[['price', 'season']].groupby('season').mean().reset_index()
    # plot
    c1.bar_chart(grouped, x='season',y='price')

    #H8
    c2.write('H8) Imóveis sem reforma são, em média, 30% mais baratos do que imóveis reformados.')
    # group by renovation
    grouped = data.loc[:, ['is_renovated', 'price']].groupby('is_renovated').mean().reset_index()
    # plot
    c2.bar_chart(grouped, x='is_renovated', y='price')

    #H9
    c1.write('H9) Imóveis reformados a partir de 2010 são, em média, 40% mais caros do que imóveis reformados anteriormente (ou sem reforma).')
    # group by renovation
    grouped = data.loc[:, ['renovated_2010', 'price']].groupby('renovated_2010').mean().reset_index()
    # plot
    c1.bar_chart(grouped, x='renovated_2010', y='price')

    #H10
    c2.write('H10) Imóveis em boas condições são, em média, 50% mais caros do que imóveis em más condições.')
    # group by condition
    grouped = data[['condition_type', 'price']].groupby('condition_type').mean().reset_index()
    # plot
    c2.bar_chart(grouped, x='condition_type', y='price')

    #H11
    c1.write('H11) Imóveis com até 2 quartos são, em média, 20% mais baratos do que imóveis com mais quartos.')
    # group by bedroom
    grouped = data.loc[:, ['bedrooms_amount', 'price']].groupby('bedrooms_amount').mean().reset_index()
    # plot
    c1.bar_chart(grouped, x='bedrooms_amount', y='price')

    #H12
    c2.write('H12) Imóveis com 1 banheiro são, em média, 30% mais baratos do que imóveis com mais banheiros.')
    # group by bathroom amount
    grouped = data.loc[:, ['price', 'bathrooms_amount']].groupby('bathrooms_amount').mean().reset_index()
    # plot
    c2.bar_chart(grouped, x='bathrooms_amount', y='price')

    return None

def portfolio_density(data):

    # group by zipcode and return median price
    grouped = data[['zipcode', 'price']].groupby('zipcode').median().reset_index()

    # rename column 'price' to 'median_price'
    grouped = grouped.rename(columns={'price': 'median_price'})

    # merge dataframes by zipcode - the new column shows median price per zipcode
    data = pd.merge(data, grouped, on='zipcode', how='inner')

    # create new empty column
    data['status'] = 0

    # for each line (i) in dataframe
    for i in range(len(data)):

        # if the conditions below
        if (data.loc[i, 'price'] <= data.loc[i, 'median_price']) & (data.loc[i, 'condition_type'] == 'good') & (
                data.loc[i, 'waterfront_option'] == 'no') & (data.loc[i, 'basement_option'] == 'no basement') & (
                data.loc[i, 'is_floor'] == 'ground floor') & (data.loc[i, 'bedrooms'] <= 2) & (
                data.loc[i, 'bathrooms_amount'] == 'up to 1'):

            # the empty column assign "buy"
            data.loc[i, 'status'] = "buy"

        else:

            # the empty column assign "don't buy"
            data.loc[i, 'status'] = "don't buy"

    # Data Separation
    data_dont_buy = data[data['status'] == "don't buy"]
    data_buy = data[data['status'] == 'buy']




    # MAP

    st.title('Map')

    # Base Map - Folium
    m = folium.Map(location=[data['lat'].mean(), data['long'].mean()], default_zoom_start=15)




    # Dont buy dots
    locations = list(zip(data_dont_buy['lat'], data_dont_buy['long']))

    for i in range(len(locations)):
        folium.CircleMarker(location=locations[i], radius=1).add_to(m)




    # Marker buy dots
    for name, row in data_buy.iterrows():

        folium.Marker([row['lat'], row['long']], popup='Price: R${0}. Bedrooms: {1}. Bathrooms: {2}. Sqft_living: {3}. Year built: {4}'.format(row['price'], row['bedrooms'], row['bathrooms'], row['sqft_living'], row['yr_built']), icon=folium.Icon(color='green')).add_to(m)

    folium_static(m)

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

    portfolio_density(data)

    commercial_distribution(data)

    attributes_distribution(data)