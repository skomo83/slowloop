import pprint
from rich import print
from rich.traceback import install
install()

import os
from datetime import date, timedelta

import re
import collections
import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd
import csv
from io import StringIO


############################################### GLOBAL VARIABLES ###############################################

print_data = False
days_prior = 7
today = date.today()
passed_date = today - timedelta(days = days_prior)

big_data = []
ip_list = []


############################################### START OF FUNCTIONS ###############################################


def get_all_data(path):
    
    working_dir = path
    folders = os.listdir(working_dir)
    if print_data: print(folders)
    
    os.chdir(working_dir)
    txt = "protocol.txt"
    data = []

    for fold in folders:
        if os.path.exists(f'{working_dir}/{fold}/{txt}'):
            with open(f'{working_dir}/{fold}/{txt}') as file:
                if print_data: print(f"Opening {fold}/{txt} and reading data")
                data = file.readlines()
                #if print_data: print(data)
                ip=fold[:fold.find("_")]
                ip_list.append(ip)
                big_data.append(data)

    if print_data: print(ip_list)
    return big_data, ip_list


def get_filtered_data(keyword):
        
    #wanted_data = []
    filtered_dates = []
    #backfill_dates.append(f"Date,IP")
    count = 0
    filtered_data_counter=0
    for index, item, in enumerate(big_data):
        for line in item:
            count+=1
            if keyword.lower() in line.lower():
                filtered_data_counter += 1
                #pp.pprint(f"{line}")
                day=int(line[:2])
                month=int(line[3:5])
                year=int(line[6:10])
                line_date= date(year,month,day)
                if line_date > passed_date:
                    if "loop" in keyword.lower():
                       filtered_dates.append(f'{line_date},{ip_list[index]}')
                    elif "backfilling" in keyword.lower():
                        x = line.find("camera")
                        #print(line[x:])
                        filtered_dates.append(f'{line_date},{ip_list[index]},{ip_list[index]}-{line[x:]}')

    if print_data: print(filtered_dates)
    print(f"Amount of {keyword} events = {filtered_data_counter}")
    return sort_data(filtered_dates)

def sort_data(data):
    if print_data: print(data)
    sorted_data = data.copy()
    if print_data: print("Sorted Data")
    sorted_data.sort()
    return sorted_data

def create_dataframe(date_data):
    header = date_data[0].split(",") 
    #popping the first line as this way of creating the data frame puts the header line in the firstrow of the data frame
    date_data.pop(0)
    csv_data = csv.reader(date_data)
    pd_data_frame = pd.DataFrame(csv_data, columns=header)
    if print_data: print(pd_data_frame)
    return pd_data_frame

def create_graphs(data, name):
    data_frame = create_dataframe(data)
    if not data_frame.empty:
        if print_data: print(data_frame)
        create_date_graph(data_frame, name)
        create_ip_graph(data_frame, name)
        
        if "backfill" in name.lower():
            create_date_camera_graph(data_frame, name)

def create_date_graph(data_frame, name):
    data_frame['Date'].value_counts().sort_index().plot(kind='bar');
    #plt.tight_layout()
    plt.xlabel("Dates", labelpad=14)
    plt.ylabel(f"# of {name} Events", labelpad=14)
    plt.title(f"{name} Events for each day - from {passed_date} to {today}", y=1.02);
    plt.savefig(f"{name}ByDate.png", dpi=300, bbox_inches='tight')


def create_ip_graph(data_frame, name):
    data_frame['IP'].value_counts().sort_index().plot(kind='bar');
    #plt.tight_layout()
    plt.xlabel("IP", labelpad=14)
    plt.ylabel(f"# of {name} Events", labelpad=14)
    plt.title(f"{name} Events for each DVR - from {passed_date} to {today}", y=1.02);
    plt.savefig(f"{name}ByIP.png", dpi=300, bbox_inches='tight')


def create_date_camera_graph(data_frame, name):
    plt.figure(figsize=(30, 10))
    count=2
    data = data_frame.groupby(["Date","Camera"]).size().loc[lambda x : x>=count]
    if print_data: print(data)
    #plt.tight_layout()
    plt.xlabel("Date by Camera", labelpad=14)
    plt.ylabel(f"# of {name} Events", labelpad=14)
    plt.title(f"{name} Events (over {count}) for each Day per Camera - from {passed_date} to {today}", y=1.02);
    data.plot(kind='bar')
    plt.savefig(f"{name}ByDate&Camera.png", dpi=300, bbox_inches='tight')


############################################### END OF FUNCTIONS ###############################################

#TODO write input function to get the path and format for the / 

folder = "C:/Users/aschofield/C R KENNEDY and COMPANY PROPRIETARY LIMITED/Scott Iles - SRS Performance issue/Exports/20211110"

get_all_data(folder)

backfill_dates = get_filtered_data("start backfilling")
slowloop_dates = get_filtered_data("slowloop")
loopratelow_dates = get_filtered_data("Looprate too low")

backfill_dates.insert(0,f"Date,IP,Camera")
slowloop_dates.insert(0,f"Date,IP")
loopratelow_dates.insert(0,f"Date,IP")

collections.Counter(backfill_dates)
collections.Counter(slowloop_dates) 
collections.Counter(loopratelow_dates)

create_graphs(slowloop_dates, "SlowLoop")
create_graphs(loopratelow_dates, "LoopRateLow")
create_graphs(backfill_dates, "Backfill")

print(f"Program Completed, please check the path below for any images\n{folder}")