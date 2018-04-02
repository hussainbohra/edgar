import os
import gzip
import shutil
import glob
from pathlib import Path
import wget
import pycurl

def download_file(src_url, target_file, compress=False):
    response_code = 0
    with open(target_file, 'wb') as f:
        c = pycurl.Curl()
        c.setopt(c.URL, src_url)
        c.setopt(c.WRITEDATA, f)
        c.perform()
        response_code = c.getinfo(c.RESPONSE_CODE)
        c.close()
        if response_code == 200:
            if compress:
                compress_file(target_file)
        else:
            delete_file(target_file)
    return target_file, response_code

def create_dir_tree(folder):
    if not os.path.exists(folder):        
        path = Path(folder)
        path.mkdir(parents=True)

def delete_file(filepathname):
    if os.path.exists(filepathname):
        os.remove(filepathname)

def rename_file(oldfilepathname, newfilepathname):
    if os.path.exists(oldfilepathname):
        os.replace(oldfilepathname, newfilepathname)
        
def delete_folder(folder):
    if os.path.exists(folder):        
        shutil.rmtree(folder)
    
def get_files(folder, prefix='*'):
    files = None
    if os.path.exists(folder):
        file_filter = '{}/{}'.format(folder, prefix)
        files = glob.glob(file_filter)
    return files

def does_folder_exists(folder):
    folder_exists = False
    if os.path.exists(folder):        
        folder_exists = True
    return folder_exists

def does_file_exists(filepathname):
    file_exists = False
    if os.path.exists(filepathname):        
        file_exists = True
    return file_exists

def get_content(filepathname):
    content = None
    if os.path.exists(filepathname):    
        try:
            with open(filepathname, mode='r', encoding='utf8') as f:
                content = f.read()
        except:
            content = None
    return content

def compress_file(filepathname):
    gzip_filepathname = filepathname + '.gz'
    with open(filepathname, 'rb') as f_in, gzip.open(gzip_filepathname, 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)
        
        
