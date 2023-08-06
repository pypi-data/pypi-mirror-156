from datetime import datetime

import pandas as pd
import os
from os import listdir
from os.path import isfile, join
from matplotlib import pyplot as plt
from tqdm import tqdm
from collections import defaultdict


def load_raw_data(filename, keys, date_format_string='%Y-%m-%d %H:%M:%S.%f'):
    item_len = len(keys)
    output = []
    df = pd.read_csv(filename)
    H = df.columns.tolist()
    temp_time_str = df[H[0]].tolist()
    temp_time = [datetime.strptime(k, date_format_string) for k in temp_time_str]
    output.append(temp_time)
    for k in range(item_len):
        output.append(df[H[k + 1]].tolist())


def output_dict_to_file(dic, filename):
    df = pd.DataFrame(dic)
    df.to_csv(filename, index=False, header=True)


def output_arrays_to_file(array, keys, filename):
    dic = {}
    for i, k in enumerate(keys):
        dic[k] = array[i]
    df = pd.DataFrame(dic)
    df.to_csv(filename, index=False, header=True)


def read_save(temp_files, temp_folder, dic, folder_name, sub_folder):
    dic_keys = list(dic.keys())
    print(dic_keys)
    for F in temp_files:
        # with open(join(folder_name + temp_folder, F)) as f:
        f = join(folder_name + temp_folder, F)
        df = pd.read_csv(f)
        H = df.columns.tolist()
        try:
            dic[dic_keys[0]] += [datetime.strptime(k, '%Y-%m-%d %H:%M:%S.%f') for k in df[H[0]].tolist()]
        except:
            dic[dic_keys[0]] += [datetime.strptime(k, '%M:%S.%f') for k in df[H[0]].tolist()]

        for k in range(1, len(dic_keys)):
            dic[dic_keys[k]] += df[H[k]].tolist()
    if not os.path.isdir(folder_name + sub_folder):
        os.makedirs(folder_name + sub_folder)
    plt.savefig(folder_name + sub_folder + temp_folder[1:-1] + '.png')
    df = pd.DataFrame(dic)
    df.to_csv(folder_name + sub_folder + temp_folder[1:-1] + ".csv", index=False, header=False)


def combine_data(sub_folder, date_format_string='%Y-%m-%d %H:%M:%S.%f', out_folder_name='combine'):
    folder_name = os.getcwd()
    sub_folder_path = folder_name + "\\" + sub_folder
    out_folder_path = folder_name + "\\" + out_folder_name
    files = [sub_folder_path + "\\" + f for f in listdir(sub_folder_path)]
    # get the keys of the files
    df = pd.read_csv(files[0])
    keys = df.columns.tolist()
    dic = {}
    for key in keys:
        dic[key]=[]

    print("combine files in: " + sub_folder_path)
    pbar = tqdm(total=len(files))
    for i, f in enumerate(files):
        pbar.update(1)
        df = pd.read_csv(f)
        H = df.columns.tolist()
        dic[keys[0]] += [datetime.strptime(k, date_format_string) for k in df[H[0]].tolist()]
        for k in range(1, len(keys)):
            dic[keys[k]] += df[H[k]].tolist()

    if not os.path.isdir(out_folder_path):
        os.makedirs(out_folder_path)
    df = pd.DataFrame(dic)
    df.to_csv(out_folder_path + "\\" + sub_folder+".csv", index=False, header=False)
    print("saved: " + out_folder_path + "\\" + sub_folder+".csv")
