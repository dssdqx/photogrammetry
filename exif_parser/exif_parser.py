import subprocess
import pandas as pd
import os

ExposureProgram_dict = {0: 'Not_Defined', 1: 'Manual', 2: 'Program_AE', 3: 'Aperture-priority_AE', 4: 'Shutter_speed_priority_AE',
                        5: 'Creative_(Slow speed)', 6: 'Action_(High speed)', 7: 'Portrait',
                        8: 'Landscape', 9: 'Bulb'}

MeteringMode_dict = {0: 'Unknown', 1: 'Average', 2: 'Center-weighted-average', 3: 'Spot', 4: 'Multi-spot',
                     5: 'Multi-segment', 6: 'Partial', 255: 'Other'}


def exif_parser(dir: str):
    find = f'exiftool -r -filename -Model -ImageSize -CreateDate -Aperture -ExposureTime -ExposureProgram -ISO -RtkFlag -ShutterType -MeteringMode -ExifVersion -DewarpData -T -n {dir} > {dir}out.txt'
    subprocess.run(find, shell=True, capture_output=True, text=True)

    w_tab = pd.read_csv((f'{dir}out.txt'), sep='\t', names=["photo", "model", "image_size", "create_date", "Aperture", "Exposure", "program", "iso",
                                                            'flag', 'shutter', 'mode', 'exif_ver', 'dewarping'])
    df = pd.DataFrame(w_tab)
    df = df.query("Exposure != '-' ")
    df.reset_index(drop= True , inplace= True )

    df2 = df.copy()
    exposure_lst = []
    exposure = set()
    q = 0
    while q < len(df['Exposure']):
        value = df['Exposure'][q]
        a = float(1/float(value))
        b = int(round(a, 0))
        exposure.add(b)
        exposure_lst.append(b)
        df2.loc[q,'Exposure'] = int(b)
        if str(df.loc[q, 'dewarping']) == '-':
            df2.loc[q, 'dewarping'] = 'on'
  
        if str(df.loc[q, 'dewarping']) != '-':
            df2.loc[q, 'dewarping'] = 'off'
        q+=1
    df2.drop(['shutter', 'exif_ver','mode'], axis= 1 , inplace= True )
    df2 = df2.sort_values("create_date", ascending=True) 

    dewarping_mode = set()
    for i in df2['dewarping']:
        dewarping_mode.add(i)


   
    df2.to_excel(f'{dir}out.xlsx', sheet_name='Sheet1', index = False)
    

    flags_lst = []

    for (columnName, columnData) in df.items():
        #print('Column Name : ', columnName)
        #print('Column Contents : ', set(columnData.values))
        if columnName == 'Aperture':
            aperture = set(columnData.values)
        if columnName == 'model':
            model = set(columnData.values)
        if columnName == 'image_size':
            image_size = set(columnData.values)

        if columnName == 'create_date':
            date_capture = []
            for i in columnData.values:
                date_capture.append(i[0:10])


        if columnName == 'program':
            program = set(columnData.values)
        if columnName == 'iso':
            iso = set(columnData.values)
        if columnName == 'flag':
            flag = set(columnData.values)
            for i in columnData.values:
                flags_lst.append(i)

        if columnName == 'shutter':
            shutter = set(columnData.values)
        if columnName == 'mode':
            mode = set(columnData.values)
        if columnName == 'exif_ver':
            exif_ver = set(columnData.values)

    for q in mode:
        for k, v in MeteringMode_dict.items():
            if int(q) == k:
                metering_name = str(v)

    for q in program:
        for k, v in ExposureProgram_dict.items():
            if int(q) == k:
                program_name = str(v)



    print(f'{dir}\n\ncamera model - {model}\nimage size - {image_size}\nflight date(yyyy-mm-dd) - {set(date_capture)}\nphotos - {len(df)}\n\naperture - {sorted(aperture)}\nshutter - {sorted(exposure)}\niso -{sorted(iso)}\nprogram - {program_name}\nrtk - {sorted(flag)}\nshutter - {shutter}\n'
          f'mode -{metering_name}\nver- {exif_ver}\ndewarping - {dewarping_mode}\n')

    troubles = []
    for i in exposure:
        if i < 600:
            troubles.append(i)
    if len(troubles) > 3:
        print(f'\nshutter values are critical minimal {sorted(troubles)} possibility BLUR-NO FOCUS \nmaybe you should ask the pilot,' 
            f' to use shutter speed priority mode with (1\\1000)\n')


    for i in sorted(exposure):
        number = exposure_lst.count(i)
        pct = str(round(int(number)/int(len(df))*100,1))
        print(f'{i} value shutter - {number} photos, {pct}% ')

    print('\n')

    for i in sorted(flag):
        number_flag = flags_lst.count(i)
        pct2 = str(round(int(number_flag)/int(len(flags_lst))*100,1))
        print(f'{i} value rtk flag - {number_flag} photos, {pct2}%')


    print(f'\nxlsx here {dir}out.xlsx')
    os.remove(f'{dir}\\out.txt')


i = 0
while i < 50:

    u_input = input('folder with photos: ')
    try:
        exif_parser(f'{u_input}')
        print('\nnext folder...\n')

    except FileNotFoundError:
        print('wrong path, please use as example- c:\\traceairroot\\account\\project\\YYYY-MM-DD\\scan\\input ')
    
    i += 1 
else:
    print(input("press enter to exit: "))



#exif_parser('c:\\MAPS\\thousand-hills-company\\heritage-walk-phase-ii\\2023-12-29\\')

