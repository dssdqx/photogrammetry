import asana
import pandas as pd
import numpy as np
import re
import subprocess
from PyPDF2 import PdfReader
import os
import warnings



def take_report_step23_metashape2(task_name: str):


    try:
        file_report = f"{home}/scan.build.report.pdf"
        reader = PdfReader(file_report)

    except FileNotFoundError:
        print("такого каталога нет на s3")
        value_error = 'xxxxxxxxxx'
        return value_error

    totalPages = int(len(reader.pages))
    # print(totalPages)
    i = 0
    while i < totalPages:
        page = reader.pages[i]
        file_txt = open(f'{home}\\scan.build.report.txt', "at", encoding='utf-8')
        file_txt.write(page.extract_text())
        file_txt.close()
        i += 1

    gsd = ''
    cameras_n = []
    error_idx = []
    re_error = ''
    units_error = []
    ac = np.nan
    rs = np.nan

    with open(f'{home}\\scan.build.report.txt', "r", encoding='utf-8') as f:
        for index, line in enumerate(f):
            if re.search(r"Total error", line):
                units = line.split()
                units_error.append(units[2])
                error_idx.append(index + 1)

            if re.search(r"Number of images:", line):
                t = line.split()
                cameras_n.append(t[3])
            if re.search(r"Ground resolution:", line):
                t2 = line.split(': ')
                gsd = gsd.join(t2[1:3])


            if re.search(r"Reprojection error:", line):
                t3 = line.split(': ')
                re_error = re_error.join(t3[1:3])

            if re.search(r"additional corrections", line):
                ac = 'on'
            if re.search(r"rolling shutter", line):
                rs = 'on'


    if len(cameras_n) == 0:
        return 0
    else:
        pass

    with open(f'{home}\\scan.build.report.txt', "r", encoding='utf-8') as f:
        for index, line in enumerate(f):

            if len(error_idx) == 0:  # там где фотки не учавствовали
                error = '0'
                units_error = ["nan"]
            if len(error_idx) != 0:
                if index == int(error_idx[0]):
                    er = line.split()
                    error = str(er[-1])
                    print(error)

    if units_error[0] == "(cm)":
        value_error2 = float(error) / 100
        value_error = round(value_error2, 3)
    if units_error[0] == "(m)":
        value_error = round(float(error), 3)

    if units_error[0] == 'nan':
        value_error = "0"

    if units_error[0] == "(mm)":
        value_error2 = float(error) / 1000
        value_error = round(value_error2, 3)

    if units_error[0] == "(deg)":
        value_error = "0"

    gsd = gsd.strip()
    re_error = re_error.strip()

    #print(error, units_error[0])
    #print(kp)
    #print(cameras_n[0])
    #print(gsd)
    #print(re_error)
    #print(ac)
    version = 'new'
    #print(value_error, 'm')
    return gsd, cameras_n[0], value_error, re_error, ac, rs, version
def take_report_step23(task_name: str):
    """Функция скачивает scan.build.report.pdf и вовзращает общую ошибку на центрах фото и не только"""

    d_report = f'aws s3 cp s3://internals.traceair.net/{task_name}/process/scan.build.report.pdf {home}/scan.build.report.pdf'
    subprocess.call(d_report)

    try:
        file_report = f"{home}/scan.build.report.pdf"
        reader = PdfReader(file_report)
    except FileNotFoundError:
        print("такого каталога нет на s3")
        value_error = 'xxxxxxxxxx'
        return value_error

    totalPages = int(len(reader.pages))
    #print(totalPages)
    i = 0
    while i < totalPages:
        page = reader.pages[i]
        file_txt = open(f'{home}\\scan.build.report.txt', "at", encoding='utf-8')
        file_txt.write(page.extract_text())
        file_txt.close()
        i += 1

    gsd_idx = []
    cameras_idx = []
    error_idx = []
    re_error_idx = []
    key_point_idx = []
    units_error = []
    ac = np.nan
    with open(f'{home}\\scan.build.report.txt', "r", encoding='utf-8') as f:
        for index, line in enumerate(f):
                if re.search(r"Total    error", line):
                    units = line.split()
                    units_error.append(units[2])
                    error_idx.append(index + 6)
                if re.search(r"Number   of  images:", line):
                    cameras_idx.append(index + 1)
                if re.search(r"Key  point   limit", line):
                    key_point_idx.append(index + 1)
                if re.search(r"Ground   resolution:", line):
                    gsd_idx.append(index + 1)
                if re.search(r"Reprojection error:", line):
                    re_error_idx.append(index + 1)
                if re.search(r"additional corrections", line):
                    ac = 'on'

    gsd = ''
    cameras = ''
    error = ''
    re_error = ''
    key_point = ''

    if len(gsd_idx) == 0 or len(cameras_idx) == 0:
        return take_report_step23_metashape2(task_name)
    else:
        pass

    with open(f'{home}\\scan.build.report.txt', "r", encoding='utf-8') as f:
        for index, line in enumerate(f):
            if index == int(gsd_idx[0]):
                gsd = gsd.join(line).replace("  ", " ")
            if index == int(cameras_idx[0]):
                cameras = cameras.join(line)
            if index == int(re_error_idx[0]):
                re_error = re_error.join(line).replace("    ", " ")

            if len(key_point_idx) == 0:
                key_point = '0'
            if len(key_point_idx) != 0:
                if index == int(key_point_idx[0]):
                    key_point = key_point.join(line).replace("  ", " ")

            if len(error_idx) == 0:       # там где фотки не учавствовали
                error = '0'
                units_error = ["nan"]
            if len(error_idx) != 0:
                if index == int(error_idx[0]):
                    error = error.join(line)

    if len(error) > 9:
        error = '0'

    if units_error[0] == "(cm)":
        value_error2 = float(error) / 100
        value_error = round(value_error2, 3)
    if units_error[0] == "(m)":
        value_error = round(float(error), 3)

    if units_error[0] == 'nan':
        value_error = "0"

    if units_error[0] == "(mm)":
        value_error2 = float(error) / 1000
        value_error = round(value_error2, 3)

    if units_error[0] == "(°)":
        value_error = "0"

    gsd = gsd.replace("\n", "")
    cameras = cameras.replace("\n", "")
    re_error = re_error.replace("\n", "")
    version = 'old'
    #print(gsd, cameras, value_error, re_error, key_point)
    return gsd, cameras, value_error, re_error, ac, version



for i in df['s3']:
    value = take_report_step23(str(i))
    print(value, str(i))