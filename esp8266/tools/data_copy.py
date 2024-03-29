import gzip
import os
import shutil

fileDir = os.path.dirname(os.path.abspath(__file__))

data_dir = os.path.join(fileDir, '../sunscreen/data')
source_dir = os.path.join(fileDir, '../sunscreen/data-raw')

# Clean the data dir
try:
    shutil.rmtree(data_dir)
except:
    pass

os.mkdir(data_dir)

# Write all minified files to the data dir
for filename in os.listdir(source_dir):
    if ((filename.find('.min.') != -1) or (filename.find('.xml') != -1) or
            (filename.find('.webmanifest') != -1) or (filename.find('.svg') != -1) or
            (filename.find('.ico') != -1) or (filename.find('.png') != -1) or (filename.find('.html') != -1)):
        with open(source_dir + '/' + filename, 'rb') as f_in:
            if (filename.find('index.min') != -1):
                filename = filename.replace('.min', '')
            with gzip.open(data_dir + '/' + filename + '.gz', 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
