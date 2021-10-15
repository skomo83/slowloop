
from rich import print
from rich.traceback import install

install()

import collections
import csv
import os
import sys
from datetime import date, timedelta
from io import StringIO
from pathlib import Path
from tkinter import *  # Python 3

import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd


############################################### GLOBAL VARIABLES ###############################################


ask_count = False
print_data = False
print_line = False
days_prior = 30
today = date.today()
passed_date = today - timedelta(days = days_prior)

#big_data = []
#ip_list = []

############################################### START OF FUNCTIONS ###############################################


def get_all_data(path):
    
    big_data = []
    ip_list = []
    
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


def get_filtered_data(keyword, big_data: list, ip_list: list):
    filtered_dates = []
    count = 0
    filtered_data_counter=0
    data_counter=0
    
    for index, item, in enumerate(big_data):
        for line in item:
            count+=1
            if keyword.lower() in line.lower():
                data_counter += 1
                if print_line: print(line)
                day=int(line[:2])
                month=int(line[3:5])
                year=int(line[6:10])
                line_date= date(year,month,day)
                if line_date > passed_date:
                    filtered_data_counter += 1
                    if "loop" in keyword.lower():
                        filtered_dates.append(f'{line_date},{ip_list[index]}')
                    elif "backfilling" in keyword.lower():
                        x = line.find("camera")
                        filtered_dates.append(f'{line_date},{ip_list[index]},{ip_list[index]}-{line[x:]}')

    if print_data: print(filtered_dates)
    print(f"Amount of {keyword} events after {passed_date} = {filtered_data_counter} from a total of {data_counter} events ")
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
        create_graph(data_frame, name, 'Date')
        create_graph(data_frame, name, 'IP')
        
        if "backfill" in name.lower():
            create_date_camera_graph(data_frame, name)


def create_graph(data_frame, name, graph_type):
    data_frame[graph_type].value_counts().sort_index().plot(kind='bar');
    #plt.tight_layout()
    plt.xlabel({graph_type}, labelpad=14)
    plt.ylabel(f"# of {name} Events", labelpad=14)
    if "date" in graph_type.lower():
        thing = "day"
    else: thing = "DVR"
    plt.title(f"{name} Events for each {thing} - from {passed_date} to {today}", y=1.02);
    plt.savefig(f"{name}By{graph_type}.png", dpi=300, bbox_inches='tight')
    print(f"Graph for [blue]{name} by {graph_type}[/blue] created ")


def get_count():
    if ask_count:
        data_valid = False
        while data_valid == False:
                count=input("\nHow many backfill events do you want to ignore per Camera per Day from the Graph ? : ")
                try:
                        count = int(count)
                except:
                    print("Error : Please use numbers ")
                    continue
                        
                if ( count <= 0 ):
                    print("Error <= 0 : Please use numbers above 0 ")
                    continue
                else:
                    data_valid = True
    else: count=3
    
    return count


def create_date_camera_graph(data_frame, name):
    graph_type = "Date & Camera"
    plt.figure(figsize=(30, 10))
    count=get_count()
    data = data_frame.groupby(["Date","Camera"]).size().loc[lambda x : x>=count]
    if print_data: print(data)
    #plt.tight_layout()
    plt.xlabel("Date by Camera", labelpad=14)
    plt.ylabel(f"# of {name} Events", labelpad=14)
    plt.title(f"{name} Events (over {count}) for each Day per Camera - from {passed_date} to {today}", y=1.02);
    data.plot(kind='bar')
    plt.savefig(f"{name}ByDate&Camera.png", dpi=300, bbox_inches='tight')
    print(f"Graph for [blue]{name} by {graph_type}[/blue] created ")

def get_path_from_clipboard():
    r = Tk()
    r.withdraw()
    #r.clipboard_clear()
    r.update() # now it stays on the clipboard after the window is closed
    try:
        pasted_data =  Path(r.clipboard_get())
    except TclError:
        pasted_data = None
    r.destroy()
    if pasted_data:
        if os.path.exists(pasted_data):
            print(f"The working folder is \n{pasted_data}\n")
            return pasted_data
        else:
            path_error = "not a valid path"
    else:
        path_error = "missing"

    print(f"\n\n[red]ERROR - Folder path is {path_error}[/red]\nPlease copy the folder path before running.\nThe program will now exit\n\n")
    sys.exit()


############################################### END OF FUNCTIONS ###############################################

def main():
    
    big_data = []
    ip_list = []
    
    #get the folder from the clipboard and run the program
    folder = get_path_from_clipboard()

    big_data, ip_list = get_all_data(folder)

    slowloop_dates = get_filtered_data("slowloop", big_data, ip_list)
    loopratelow_dates = get_filtered_data("Looprate too low", big_data, ip_list)
    backfill_dates = get_filtered_data("start backfilling", big_data, ip_list)

    slowloop_dates.insert(0,f"Date,IP")
    loopratelow_dates.insert(0,f"Date,IP")
    backfill_dates.insert(0,f"Date,IP,Camera")

    collections.Counter(slowloop_dates) 
    collections.Counter(loopratelow_dates)
    collections.Counter(backfill_dates)

    create_graphs(slowloop_dates, "SlowLoop")
    create_graphs(loopratelow_dates, "LoopRateLow")
    create_graphs(backfill_dates, "Backfill") #back fill created a bigger graph that the others so we run this one last

    print(f"\n[green]Program Completed[/green], please check the path below for any graph images\n\n{folder}\n\n")


if __name__ == "__main__":
    
    main()
    
    