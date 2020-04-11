import os
import shutil

data_dir = './sunscreen/data'
source_dir = './sunscreen/data_raw'

shutil.rmtree('./sunscreen/data')
os.mkdir('sunscreen/data')

for filename in os.listdir('sunscreen/data'):
    os.remove
