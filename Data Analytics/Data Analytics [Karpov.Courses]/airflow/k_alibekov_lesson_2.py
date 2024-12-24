#!/usr/bin/env python
# coding: utf-8

# In[1]:


import requests
import pandas as pd
from datetime import timedelta
from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator

TOP_1M_DOMAINS = 'https://storage.yandexcloud.net/kc-startda/top-1m.csv'
TOP_1M_DOMAINS_FILE = 'top-1m.csv'

def get_data():
    # Здесь пока оставили запись в файл, как передавать переменую между тасками будет в третьем уроке
    top_doms = pd.read_csv(TOP_1M_DOMAINS)
    top_data = top_doms.to_csv(index=False)

    with open(TOP_1M_DOMAINS_FILE, 'w') as f:
        f.write(top_data)

def get_top_10_domain_zones():
    top_10_domain_zones = pd.read_csv(TOP_1M_DOMAINS, names=['rank', 'domain'])
    top_10_domain_zones = top_10_domain_zones.groupby('domain_zone', as_index=False).agg({'domain':'count'}).sort_values(by='domain', ascending=False).head(10)
    with open('top_10_domain_zones.csv', 'w') as f:
        f.write(top_10_domain_zones.to_csv(index=False, header=False))


def get_max_len_domain():
    max_len_domain = pd.read_csv(TOP_1M_DOMAINS, names=['rank', 'domain'])
    max_len_domain['domain_len'] = max_len_domain.domain.apply(lambda x: len(x))
    max_len_domain = max_len_domain.sort_values(by='domain_len', ascending=False).head(1)
    with open('max_len_domain.csv', 'w') as f:
        f.write(max_len_domain.to_csv(index=False, header=False))
        
def get_airflow_place():
    airflow_place = pd.read_csv(TOP_1M_DOMAINS_FILE, names=['rank', 'domain'])
    airflow_place = airflow_place.query("domain == 'airflow.com'")
    with open('airflow_place.csv', 'w') as f:
        f.write(airflow_place.to_csv(index=False, header=False))

def print_data(ds):
    with open('top_10_domain_zones.csv', 'r') as f:
        all_data = f.read()
    with open('max_len_domain.csv', 'r') as f:
        all_data_com = f.read()
    with open('airflow_place.csv', 'r') as f:
        all_data_com = f.read()
    date = ds

    print(f'Top 10 domain zones for date {date}')
    print(all_data)

    print(f'Max len domain for date {date}')
    print(all_data_com)
    
    print(f'Airflow place for date {date}')
    print(all_data_com)


default_args = {
    'owner': 'k.alibekov',
    'depends_on_past': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'start_date': datetime(2023, 8, 28),
}
schedule_interval = '0 15 * * *'

dag = DAG('k_alibekov', default_args=default_args, schedule_interval=schedule_interval)

t1 = PythonOperator(task_id='get_data',
                    python_callable=get_data,
                    dag=dag)

t2 = PythonOperator(task_id='get_top_10_domain_zones',
                    python_callable=get_top_10_domain_zones,
                    dag=dag)

t3 = PythonOperator(task_id='get_max_len_domain',
                    python_callable=get_max_len_domain,
                    dag=dag)

t4 = PythonOperator(task_id='get_airflow_place',
                    python_callable=get_airflow_place,
                    dag=dag)

t5 = PythonOperator(task_id='print_data',
                    python_callable=print_data,
                    dag=dag)

t1 >> [t2, t3, t4] >> t5

