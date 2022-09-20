import geopandas
import streamlit as st
import pandas as pd
import numpy as np
import folium

from streamlit_folium import folium_static
from folium.plugins import MarkerCluster

from streamlit_option_menu import option_menu

import plotly.express as px

from datetime import datetime

st.set_page_config(layout='wide')

with st.sidebar:
    selected = option_menu("Menu", ['Introduction', 'Insights', 'Conclusion'],
        icons=['house', 'lightbulb', 'bookmark-check'], menu_icon="cast", default_index=0)

# Header Image
col1, col2, col3 = st.columns(3)
col2.image('img1.png')

@st.cache(allow_output_mutation=True)
def get_data(path):
    data = pd.read_csv(path)
    return data

def introduction(data):

    if selected == 'Introduction':

        st.markdown("<h1 style='text-align: center; color: black;'>House Rocket Project</h1>", unsafe_allow_html=True)
        st.write('')
        st.write("House Rocket is a fictitious real estate company - its business model is buying and selling properties. The business team doesn't make good decisions because the amount of data is large and it would take a long time to do the work manually. So, this project aims to get insights through the analysis and manipulation of data to assist business team decisions.")
        st.write(":pushpin: What properties should House Rocket buy?")
        st.write(":pushpin: Once bought, at what price should it sell?")
        st.write(":pushpin: When is the best time to sell it?")

        st.header('The Data')
        b_dataset = st.checkbox('Display Dataset')
        if b_dataset:
            st.dataframe(data)

        st.header('Assumptions')
        st.write(":small_orange_diamond: For repeated id's, the most recent sale of the property was considered;")
        st.write(':small_orange_diamond: Properties with a renewal year equal to 0 were considered without renovation;')
        st.write(':small_orange_diamond: The line corresponding to a property with 33 bedrooms has been removed as it was considered a typo;')
        st.write(':small_orange_diamond: The sqft_living15 and sqft_lot15 features, which correspond to the area of neighborhood properties, were disregarded.')

        st.header('The Final Product')
        st.write('The following products will be delivered to the company to solve the business problems:')
        st.write(':small_orange_diamond: Report with properties to buy;')
        st.write(':small_orange_diamond: Map with the best season to sell it and the suggested price.')
    return None

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


    # Selling Dataframe

    # group by zipcode and season and return the median price
    grouped = data[['season', 'zipcode', 'price']].groupby(['zipcode', 'season']).median().reset_index()

    # organize values by zipcode first and then price
    grouped = grouped.sort_values(['zipcode', 'price'])

    # keep the highest price only
    grouped = grouped.drop_duplicates(subset=['zipcode'], keep='last').reset_index()

    # drop index column
    grouped = grouped.drop(columns='index')

    # rename columns
    grouped = grouped.rename(columns={'season': 'high_season', 'price': 'season_median_price'})
    # filter columns by profitable houses (column 'status' equal to 'buy' value)

    # merge grouped dataset with general dataset by zipcode to return highest season median prices
    data = pd.merge(data, grouped, on='zipcode', how='inner')
    # create new column 'selling_price'
    data['selling_price'] = 0

    # for each line in dataset
    for i in range(len(data)):

        # if 'price' is lower than 'season_median_price'
        if (data.loc[i, 'price'] < data.loc[i, 'season_median_price']):

            # column 'selling_price' receives 'price' plus 30%
            data.loc[i, 'selling_price'] = (data.loc[i, 'price']) * 1.30

        else:

            # column 'selling_price' receives 'price' plus 10%
            data.loc[i, 'selling_price'] = (data.loc[i, 'price']) * 1.10

    # create profit column
    data['profit'] = data['selling_price'] - data['price']

    return data

def insights(data):


    if selected == 'Insights':

        # Hypotheses
        st.markdown("<h1 style='text-align: center; color: black;'>Hypotheses</h1>", unsafe_allow_html=True)
        st.write('')
        c1, c2 = st.columns((1, 1))

        # H1
        c1.subheader(':small_orange_diamond: Properties with waterfront are, on average, 30% more expensive.')
        c1.write(':heavy_check_mark: True because properties with waterfront are, on average, 212% more expensive than properties without waterfront.')
        # group by 'waterfront_option' and take average price
        grouped = data[['waterfront_option', 'price']].groupby('waterfront_option').mean().reset_index()
        fig = px.bar(grouped, x='waterfront_option', y='price')
        fig.update_traces(marker_color='rgba(0, 255, 17, 0.6)')
        c1.plotly_chart(fig, use_container_width=True)

        # H6
        c2.subheader(':small_orange_diamond: Ground floor properties are, on average, 40% cheaper.')
        c2.write(':heavy_multiplication_x: False because ground floor properties are, on average, 30% cheaper than properties with more floors.')
        # group by floor and return mean values
        grouped = data[['price', 'is_floor']].groupby('is_floor').mean().reset_index()
        # plot
        fig = px.bar(grouped, x='is_floor', y='price')
        fig.update_traces(marker_color='rgba(255, 0, 0, 0.6)')
        c2.plotly_chart(fig, use_container_width=True)

        # H3
        c1.subheader(':small_orange_diamond: Properties with a basement are, on average, 20% more expensive.')
        c1.write(':heavy_check_mark: True because properties with a basement are, on average, 28% more expensive than properties without a basement.')
        # group by basement
        grouped = data[['basement_option', 'price']].groupby('basement_option').mean().reset_index()
        # plot
        fig = px.bar(grouped, x='basement_option', y='price')
        fig.update_traces(marker_color='rgba(0, 255, 17, 0.6)')
        c1.plotly_chart(fig, use_container_width=True)


        #H2
        c2.subheader(':small_orange_diamond: Properties built before 1955 are, on average, 50% cheaper.')
        c2.write(':heavy_multiplication_x: False because properties built before 1955 are only 0.4% cheaper, on average, than properties built after that year.')
        # group data by "before" and "after" year 1955
        grouped = data[['is_before_1955', 'price']].groupby('is_before_1955').mean().reset_index()
        # plot
        fig = px.bar(grouped, x='is_before_1955', y='price')
        fig.update_traces(marker_color='rgba(255, 0, 0, 0.6)')
        c2.plotly_chart(fig, use_container_width=True)

        #H5
        c1.subheader(':small_orange_diamond: Properties with 3 bathrooms have a month over month growth of 15%.')
        c1.write(':heavy_multiplication_x: False because the growth was less than 15% in all months.')
        # group by year-month and return the mean value
        grouped = data[['price', 'month_year']].groupby('month_year').mean().reset_index()
        # plot
        fig = px.line(grouped, x='month_year', y='price')
        #fig.update_traces(marker_color='rgba(255, 0, 0, 0.6)')
        c1.plotly_chart(fig, use_container_width=True)

        #H10
        c2.subheader(':small_orange_diamond: Properties in good condition are, on average, 50% more expensive.')
        c2.write(':heavy_multiplication_x: False because properties in good condition are, on average, only 0.4% more expensive than properties in bad condition.')
        # group by condition
        grouped = data[['condition_type', 'price']].groupby('condition_type').mean().reset_index()
        # plot
        fig = px.bar(grouped, x='condition_type', y='price')
        fig.update_traces(marker_color='rgba(255, 0, 0, 0.6)')
        c2.plotly_chart(fig, use_container_width=True)

        #H12
        c1.subheader(':small_orange_diamond: Properties with 1 bathroom are, on average, 30% cheaper.')
        c1.write(':heavy_check_mark: True because properties with up to 1 bathroom are, on average, 40% cheaper than properties with more bathrooms.')
        # group by bathroom amount
        grouped = data.loc[:, ['price', 'bathrooms_amount']].groupby('bathrooms_amount').mean().reset_index()
        # plot
        fig = px.bar(grouped, x='bathrooms_amount', y='price')
        fig.update_traces(marker_color='rgba(0, 255, 17, 0.6)')
        c1.plotly_chart(fig, use_container_width=True)

        # H7
        c2.subheader(':small_orange_diamond: The price of real estate in winter is, on average, 20% cheaper than in summer.')
        c2.write(':heavy_multiplication_x: False because real estate prices in winter are, on average, only 5% cheaper than in summer.')
        # group by season and return mean price
        grouped = data[['price', 'season']].groupby('season').mean().reset_index()
        # plot
        fig = px.bar(grouped, x='season', y='price')
        fig.update_traces(marker_color='rgba(255, 0, 0, 0.6)')
        c2.plotly_chart(fig, use_container_width=True)

        # H11
        c1.write('')
        c1.write('')
        c1.subheader(':small_orange_diamond: Properties with up to 2 bedrooms are, on average, 20% cheaper.')
        c1.write(':heavy_check_mark: True because properties with up to 2 bedrooms are, on average, 30% cheaper than properties with more than 2 bedrooms.')
        # group by bedroom
        grouped = data.loc[:, ['bedrooms_amount', 'price']].groupby('bedrooms_amount').mean().reset_index()
        # plot
        fig = px.bar(grouped, x='bedrooms_amount', y='price')
        fig.update_traces(marker_color='rgba(0, 255, 17, 0.6)')
        c1.plotly_chart(fig, use_container_width=True)

        # H9
        c2.subheader(':small_orange_diamond: Properties renovated after 2010, on average, 40% more expensive than properties previously renovated (or without renovation).')
        c2.write(':heavy_multiplication_x: False because properties renovated after 2010 are, on average, 27% more expensive than previously renovated (or unrenovated) properties.')
        # group by renovation
        grouped = data.loc[:, ['renovated_2010', 'price']].groupby('renovated_2010').mean().reset_index()
        # plot
        fig = px.bar(grouped, x='renovated_2010', y='price')
        fig.update_traces(marker_color='rgba(255, 0, 0, 0.6)')
        c2.plotly_chart(fig, use_container_width=True)

        # H8
        c1.subheader(':small_orange_diamond: Unrenovated properties are, on average, 30% cheaper than renovated properties.')
        c1.write(':heavy_check_mark: True because unrenovated properties are, on average, 30% cheaper than renovated properties.')
        # group by renovation
        grouped = data.loc[:, ['is_renovated', 'price']].groupby('is_renovated').mean().reset_index()
        # plot
        fig = px.bar(grouped, x='is_renovated', y='price')
        fig.update_traces(marker_color='rgba(0, 255, 17, 0.6)')
        c1.plotly_chart(fig, use_container_width=True)

        # Main Insights
        st.markdown("<h1 style='text-align: center; color: black;'>Main Insights</h1>", unsafe_allow_html=True)
        st.write('')
        st.write(':small_orange_diamond: Ground floor properties are, on average, 30% cheaper than properties with more floors;')
        st.write(':small_orange_diamond: Properties with waterfront are, on average, 212% more expensive than properties without waterfront;')
        st.write(':small_orange_diamond: Properties with a basement are, on average, 28% more expensive than properties without a basement;')
        st.write(':small_orange_diamond: Properties with up to 2 bedrooms are, on average, 30% cheaper than properties with more bedrooms;')
        st.write(':small_orange_diamond: Properties with up to 1 bathroom are, on average, 40% cheaper than properties with more bathrooms.')


        return None

def conclusion(data):

    if selected == 'Conclusion':

        st.markdown("<h1 style='text-align: center; color: black;'>Best Properties</h1>", unsafe_allow_html=True)
        st.write(":small_orange_diamond: Considering the insights described before, the purchase opportunities were identified below. You can filter them by neighborhood:")
        st.write('')
        data = data.loc[data['status'] == 'buy', ['id', 'price', 'high_season', 'selling_price', 'profit', 'sqft_living', 'bedrooms', 'bathrooms', 'yr_built', 'zipcode', 'lat', 'long']].reset_index()
        data = data.drop(columns='index')

        all_zipcodes = np.sort(data['zipcode'].unique())
        all_options = st.checkbox("SHOW ALL PROPERTIES", value=True)
        st.write('')

        if all_options:
            selected_option = all_zipcodes
        else:
            selected_option = st.multiselect('In which region would you like to buy a property? Choose a zipcode below:', all_zipcodes, default=98001)

        data = data.loc[data['zipcode'].isin(selected_option), :]


        # round values
        data['price'] = data['price'].astype(int)
        data['selling_price'] = data['selling_price'].astype(int)
        data['profit'] = data['profit'].astype(int)
        data['sqft_living'] = data['sqft_living'].astype(int)
        data['bathrooms'] = data['bathrooms'].round(0)
        data['bathrooms'] = data['bathrooms'].astype(int)
        data['yr_built'] = data['yr_built'].apply(lambda x: x.year)

        df = data.copy()
        df = df.rename(columns={'high_season':'best_season_to_sell'})


        # Metrics

        col1, col2= st.columns(2)

        col2.header(':small_orange_diamond:Data')
        col2.dataframe(df.loc[:, ['id', 'best_season_to_sell', 'bedrooms', 'bathrooms', 'yr_built', 'price', 'selling_price', 'profit']], width=1080)

        col1.header(':small_orange_diamond:Summary')
        col1.metric(label="Properties", value=df.shape[0])
        col1.metric(label="Price (US$)", value=df['price'].sum())
        col1.metric(label="Profit", value=df['profit'].sum())

        # Base Map - Folium
        st.header(':small_orange_diamond:Map')
        st.write('')

        density_map = folium.Map(location=[data['lat'].mean(),
                                           data['long'].mean()],
                                 default_zoom_start=15)

        marker_cluster = MarkerCluster().add_to(density_map)
        for name, row in data.iterrows():
            folium.Marker([row['lat'], row['long']],
                          popup='Price: US${0}. Advisable to sell in the {1} for US${2}. Profit: US${3}. Area: {4} sqft. Bedroom(s): {5}. Bathroom(s): {6}. Year built: {7}.'.format(
                              row['price'],
                              row['high_season'],
                              row['selling_price'],
                              row['profit'],
                              row['sqft_living'],
                              row['bedrooms'],
                              row['bathrooms'],
                              row['yr_built'])).add_to(marker_cluster)

        folium_static(density_map)

        st.markdown("<h1 style='text-align: center; color: black;'>Conclusion</h1>", unsafe_allow_html=True)

        st.write(":small_orange_diamond: Considering all the insights described before, 429 purchase opportunities were identified. These opportunities, combined, generate a profit of approximately 40 million dollars - the average profit, per property, is 93 thousand dollars. The solution was divided between two stages: the purchase stage and the property sale stage. In addition, I considered the season of sales in this segment of the real estate market as a business premise.")
        st.write(":small_orange_diamond: For the purchase stage, with the data processed and organized, during the exploratory analysis I raised some hypotheses. The most relevant hypotheses, such as the one referring to the property's condition were considered for their purchase. For the sale stage, I grouped the properties by region (zipcode) and season, then returned the median price. Properties with a value above the median value of the region will be sold with an increase of 10%. Properties with a value below the median value of the region will be sold with an increase of 30%. This way, I considered the best time of the year for sale in each region.")

    return None

if __name__ == "__main__":
    # ETL
    # data extraction

    path = 'kc_house_data.csv'

    data = get_data(path)

    # transformation

    introduction(data)

    data = set_feature(data)

    insights(data)

    conclusion(data)


