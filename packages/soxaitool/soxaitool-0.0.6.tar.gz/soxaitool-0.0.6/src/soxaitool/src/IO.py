from datetime import datetime

import pandas as pd
import os
from os import listdir
from tqdm import tqdm


def load(file_name, folder="combine", date_format_string='%Y-%m-%d %H:%M:%S.%f'):
    # print(f"loading combined data: {file_name}")
    output = []
    current_folder = os.getcwd()
    file = current_folder + "/" + folder + "/" + file_name + ".csv"
    df = pd.read_csv(file)
    keys = df.columns.tolist()
    temp_time_str = df[keys[0]].tolist()
    temp_time = [datetime.strptime(k, date_format_string) for k in temp_time_str]
    output.append(temp_time)
    item_len = len(keys)
    for k in range(1,item_len):
        output.append(df[keys[k]].tolist())
    print(f"Loaded data size: ( {len(output)} , {len(output[0])} ), keys: {keys}")
    return output, keys


def output_dict_to_file(dic, filename):
    df = pd.DataFrame(dic)
    df.to_csv(filename, index=False, header=True)


def save(array, keys, filename, out_folder_name="output"):
    dic = {}
    folder_name = os.getcwd()
    out_folder_path = folder_name + "/" + out_folder_name
    for i, k in enumerate(keys):
        dic[k] = array[i]
    df = pd.DataFrame(dic)
    if not os.path.isdir(out_folder_path):
        os.makedirs(out_folder_path)
    out_folder_path + "/" + filename + ".csv"
    df.to_csv(out_folder_path + "/" + filename + ".csv", index=False, header=True)


def combine(sub_folder, out_folder_name='combine'):
    folder_name = os.getcwd()
    sub_folder_path = folder_name + "/" + sub_folder
    out_folder_path = folder_name + "/" + out_folder_name
    files = [sub_folder_path + "/" + f for f in listdir(sub_folder_path)]
    # get the keys of the files
    df = pd.read_csv(files[0])
    keys = df.columns.tolist()
    dic = {}
    for key in keys:
        dic[key] = []

    print("combine files in: " + sub_folder_path)
    pbar = tqdm(total=len(files))
    for i, f in enumerate(files):
        pbar.update(1)
        df = pd.read_csv(f)
        for k in keys:
            dic[k] += df[k].tolist()

    if not os.path.isdir(out_folder_path):
        os.makedirs(out_folder_path)
    df = pd.DataFrame(dic)
    df.to_csv(out_folder_path + "/" + sub_folder + ".csv", index=False, header=True)
    print("saved: " + out_folder_path + "/" + sub_folder + ".csv")
    print(f"num of files: ( {len(files)} ), num of points: {len(dic[keys[0]])}, keys: {keys}")

