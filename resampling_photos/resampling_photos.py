import os
from datetime import datetime
from PIL import Image
import threading
from progress.bar import IncrementalBar
import sys

start_time = datetime.now()
cpu_n = int(os.cpu_count())


path = input('\nfolder with original photos: ')

src = f'{path}\\resampled\\'


if os.path.isdir(src):
    files = os.listdir(src)
    for i in files:
        os.remove(src + i)
else:
    os.makedirs(src)


def check_frame(photos: list):
    original_frame = set()
    for i in photos:
        image = Image.open(i)
        original_frame.add(image.size)
    a = " ".join(str(e) for e in original_frame).split(',')
    x = int(a[0].replace('(',''))
    y = int(a[1].replace(')',''))
    scale = x/y
    if x <= 6336 or y <= 4224 :
        return -1
    else:
        return x, y
    

fileList = []
fileName = []


for root, dirs, files in os.walk(path):
    for file in files:
        if file.endswith(".JPG") or file.endswith('.jpg'):
            fileList.append(os.path.join(root, file))
            fileName.append(file)


if len(fileList) == 0:
    v = input("the folder does not contain photos, try again, press enter...")
    sys.exit()
else:
    v2 = check_frame(fileList)
    print(f'\noriginal photos frame: {v2[0]} X {v2[1]} will be resampling to -> 6336 X 4224\n\nused threads: {cpu_n-1} ')
    if v2 == -1:
        print('no need resampling here')
        sys.exit()



print('\n')

def resampling(photo: str, name: str):
    image = Image.open(photo)
    #print(f"Original size : {image.size}")  # 9504, 6336
    tmp_resized = image.resize((6336, 4224), resample = Image.LANCZOS)
    exif = image.getexif()
    tmp_resized.save(f'{src}{name}', quality=90, exif=exif)


num_threads = int(cpu_n-1)
threads = []
bar = IncrementalBar('processing resize...', max = len(fileList))

while fileList:
    # Извлекаем файлы для текущего набора потоков
    files_for_thread = fileList[:num_threads]
    fileList = fileList[num_threads:]

    for file_name in files_for_thread:
        name = file_name.split('\\')
        thread = threading.Thread(target=resampling, args=(file_name, name[-1]))
        thread.start()
        threads.append(thread)
        bar.next()

    # Ждем завершения всех потоков текущего набора
    for thread in threads:
        #print(thread, 'done')
        thread.join()
    threads = []

bar.finish()

print(f"all photos are resampled, processing time: {datetime.now() - start_time}\n")

print(f'photos here -  {path}resampled\n')

f = input("\nfor exit, press enter...")

