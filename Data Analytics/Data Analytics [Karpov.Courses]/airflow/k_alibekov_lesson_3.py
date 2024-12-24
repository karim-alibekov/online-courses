#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import requests
from zipfile import ZipFile
from io import BytesIO
import pandas as pd
import numpy as np
from datetime import timedelta
from datetime import datetime
from io import StringIO

from airflow.decorators import dag, task
from airflow.operators.python import get_current_context
from airflow.models import Variable

path = '/var/lib/airflow/airflow.git/dags/a.batalov/vgsales.csv'

login = "k-alibekov"
selected_year = 1994 + hash(f'{login}') % 23

default_args = {
    'owner': 'k.alibekov',
    'depends_on_past': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'start_date': datetime(2023, 8, 30)
}


@dag(default_args=default_args, schedule_interval='0 9 * * *',catchup=False)

def k_alibekov_lesson_3():
    
    
    @task(retries=2)
    def get_data():
        df = pd.read_csv(path)
        df = df.to_csv(index=False)
        return df

    @task(retries=2)
    def most_sales_per_year(df):
        df = pd.read_csv(StringIO(df))
        most_sales_per_year = df.query("Year == @selected_year").groupby('Name', as_index=False).agg({'Global_Sales':'sum'})                               .sort_values(by='Global_Sales', ascending=False).head(1).Name.to_list()
        return most_sales_per_year

    @task(retries=2)
    def most_sold_genre_in_europe(df):
        df = pd.read_csv(StringIO(df))
        most_sold_genre_in_europe = df.query("Year == @selected_year").groupby('Genre', as_index=False).agg({'EU_Sales':'sum'})                                     .sort_values(by='EU_Sales', ascending=False).head(1).Genre.to_list()
        return most_sold_genre_in_europe
        

    @task(retries=2)
    def million_sales_platform_NA(df):
        df = pd.read_csv(StringIO(df))
        million_sales_platform_NA = df.query("Year == @selected_year & NA_Sales > 1").groupby('Platform', as_index=False).agg({'Name':'nunique'})                                     .sort_values(by='Name', ascending=False).head(1).Platform.to_list()
        return million_sales_platform_NA

    @task(retries=2)
    def top_mean_sales_in_japan(df):
        df = pd.read_csv(StringIO(df))
        top_mean_sales_in_japan = df.query("Year == @selected_year").groupby('Publisher', as_index=False).agg({'JP_Sales':'mean'})                                   .sort_values(by='JP_Sales', ascending=False).head(1).Publisher.to_list()
        return top_mean_sales_in_japan
    
    @task(retries=2)
    def japan_sales_better_europe_sales(df):
        df = pd.read_csv(StringIO(df))
        japan_sales_better_europe_sales = df.query("Year == @selected_year & EU_Sales > JP_Sales").Name.count()
        return japan_sales_better_europe_sales

    @task(retries=2)
    def print_data(most_sales_per_year, most_sold_genre_in_europe, million_sales_platform_NA, top_mean_sales_in_japan, japan_sales_better_europe_sales):

        context = get_current_context()
        date = context['ds']
        
        print(f'''
              Date: {date}
              Selected year: {selected_year}
              ''')
        
        print(f'''
              Most sold game in the world: {most_sales_per_year}
              Most sold genre in Europe: {most_sold_genre_in_europe}
              More than million sales in NA platforms: {million_sales_platform_NA}
              Highest mean sales publisher in Japan: {top_mean_sales_in_japan}
              Number of games which sold better in Japan than in Europe: {japan_sales_better_europe_sales}
              ''')
        
    df = get_data()

    most_sales_per_year = most_sales_per_year(df)
    most_sold_genre_in_europe = most_sold_genre_in_europe(df)
    million_sales_platform_NA = million_sales_platform_NA(df)
    top_mean_sales_in_japan = top_mean_sales_in_japan(df)
    japan_sales_better_europe_sales = japan_sales_better_europe_sales(df)

    print_data(most_sales_per_year, most_sold_genre_in_europe, million_sales_platform_NA, top_mean_sales_in_japan, japan_sales_better_europe_sales)

k_alibekov_lesson_3 = k_alibekov_lesson_3()

