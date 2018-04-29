import sys
import csv
from datetime import datetime, timedelta
import pandas as pd
import Global
from utils import FileHelper

class SECDataFolder:
    def __init__(self):
        self.base_folder = Global.EDGAR_DATA_FOLDER
        self.sec_folder = '{}/sec'.format(self.base_folder)
        self.edgar_folder = '{}/edgar'.format(self.sec_folder)
        self.cik_folder = '{}/cik'.format(self.edgar_folder)
        self.index_base_folder = '{}/index'.format(self.edgar_folder)
        self.forms_base_folder = '{}/forms'.format(self.edgar_folder)
        self.extract_base_folder = '{}/extract'.format(self.edgar_folder)
        self.extract_metadata_folder = '{}/metadata'.format(self.extract_base_folder)
        self.extract_cik_folder = '{}/cik'.format(self.extract_base_folder)
        self.extract_json_folder = '{}/json'.format(self.extract_base_folder)
        self.search_base_folder = '{}/search'.format(self.edgar_folder)

class CIKDownloader():
    def __init__(self):
        self.SECDataFolder = SECDataFolder()
        self.cik_src_url = Global.EDGAR_CIK_LOOKUPFILE
    
    def get_cik_target_filename(self):
        target_folder = self.SECDataFolder.cik_folder
        target_file = '{}/{}'.format(target_folder, self.cik_src_url.split('/')[-1])
        return target_folder, target_file
        
    def download_cik_file(self):
        # Download the CIK file here
        target_folder, target_filepathname = self.get_cik_target_filename()
        FileHelper.create_dir_tree(target_folder)
        return FileHelper.download_file(src_url=self.cik_src_url, target_file=target_filepathname)

class FormDownloader:
    def __init__(self):
        self.SECDataFolder = SECDataFolder()
        self.sec_base_url = Global.EDGAR_BASE_URL
        self.daily_index_url = Global.EDGAR_DAILY_INDEX_URL
        self.qtr_index_url = Global.EDGAR_FULL_INDEX_URL
        self.index_header = Global.EDGAR_INDEX_HEADER
    
    def get_quarter(self, dt):
        quarter = pd.Timestamp(datetime(dt.year, dt.month, dt.day)).quarter
        return quarter
    
    def get_daily_form_idx_url(self, dt):
        year = dt.year
        quarter = 'QTR{}'.format(self.get_quarter(dt=dt))
        form_idx_url = '{}/{}/{}/form.{}{}{}.idx'.format(self.daily_index_url \
                                                             ,year \
                                                             ,quarter \
                                                             ,year \
                                                             ,str(dt.month).zfill(2) \
                                                             ,str(dt.day).zfill(2))
        return form_idx_url
    
    def get_daily_form_idx_target_file(self, form_idx_url):
        base_folder = '{}/daily'.format(self.SECDataFolder.index_base_folder)
        filename = form_idx_url.split('/')[-1]
        target_file = '{}/{}'.format(base_folder, filename)
        return base_folder, target_file
    
    def download_daily_index(self, index_date):       
        print('Downloading index: {}'.format(index_date))
        form_idx_url = self.get_daily_form_idx_url(dt=index_date)
        print('...Form URL: {}'.format(form_idx_url))
        target_folder, target_file = self.get_daily_form_idx_target_file(form_idx_url=form_idx_url)
        print('...Target file: {}'.format(target_file))
        FileHelper.create_dir_tree(target_folder)
        return FileHelper.download_file(src_url=form_idx_url, target_file=target_file)

    def get_qtr_form_idx_url(self, year, qtr):
        form_idx_url = '{}/{}/QTR{}/form.idx'.format(self.qtr_index_url, year, qtr)
        return form_idx_url

    def get_qtr_form_idx_target_file(self, year, qtr):
        base_folder = '{}/full'.format(self.SECDataFolder.index_base_folder)       
        filename = 'form_{}_QTR{}.idx'.format(year, qtr)
        target_file = '{}/{}'.format(base_folder, filename)
        return base_folder, target_file

    def get_form_csv_target_file(self, idx_file):
        return idx_file.replace('.idx', '.csv')

    def download_qtr_index(self, index_year, index_qtr):       
        print('Downloading index: {}-QTR{}'.format(index_year, index_qtr))
        form_idx_url = self.get_qtr_form_idx_url(index_year, index_qtr)
        print('...Form URL: {}'.format(form_idx_url))
        target_folder, target_file = self.get_qtr_form_idx_target_file(index_year, index_qtr)
        print('...Target file: {}'.format(target_file))
        FileHelper.create_dir_tree(target_folder)
        return FileHelper.download_file(src_url=form_idx_url, target_file=target_file)

    def convert_indx_to_csv(self, target_folder, target_idx):
        target_csv = self.get_form_csv_target_file(target_idx)
        if FileHelper.does_file_exists(target_idx):
            fileWriter = open(target_csv, 'w', encoding="utf-8")
            csvWriter = csv.DictWriter(fileWriter, self.index_header)
            csvWriter.writeheader()
            print('...Wrote header')
            with open(target_idx, mode="r", encoding="utf-8") as idx:
                bStart = False                    
                for line in idx:
                    if not bStart and line.startswith('-----'):
                        print('...opened file for reading')
                        bStart = True
                    elif bStart:
                        fields = [token.strip() for token in line.rstrip('\n').split('  ') if len(token.strip()) > 0]
                        #print(line)
                        data_row = {}
                        data_row['form_id'] = line[0:12].strip()
                        data_row['company_name'] = line[12:74].strip().replace('\\', '').replace('/', '')
                        data_row['cik'] = line[74:86].strip()
                        filing_dt = line[86:98].strip().replace('-', '')
                        edgar_file =  line[98:].strip()  
                        # Get derived values
                        data_row['f_year'] = int(filing_dt[0:4])
                        data_row['f_month'] = int(filing_dt[4:6])
                        data_row['f_day'] = int(filing_dt[6:8])
                        data_row['dt_file'] = datetime(data_row['f_year'], data_row['f_month'], data_row['f_day'])
                        data_row['edgar_file'] = edgar_file  
                        data_row['form_url'] = self.get_form_url(edgar_file) 
                        target_folder, target_file = self.get_form_target_file(data_row['form_id'], data_row['company_name'] \
                                                                             , data_row['cik'], filing_dt, edgar_file)
                        data_row['target_folder'] = target_folder
                        data_row['target_file'] = target_file
                        csvWriter.writerow(data_row)
                fileWriter.close()
    
    def convert_qtr_indx_to_csv(self, index_year, index_qtr):
        print('...Converting {}-{}'.format(index_year, index_qtr))
        target_folder, target_idx = self.get_qtr_form_idx_target_file(index_year, index_qtr)
        self.convert_indx_to_csv(target_folder, target_idx)

    def convert_daily_indx_to_csv(self, index_date):
        print('...Converting {}'.format(index_date))
        form_idx_url = self.get_daily_form_idx_url(dt=index_date)
        target_folder, target_idx = self.get_daily_form_idx_target_file(form_idx_url=form_idx_url)
        self.convert_indx_to_csv(target_folder, target_idx)
        
    def get_form_url(self, edgar_file):
        form_url = '{}/{}'.format(self.sec_base_url, edgar_file)
        return form_url
 
    def get_form_target_file(self, form_id, company_name, cik, filing_dt, edgar_file):
        base_folder = self.SECDataFolder.forms_base_folder
        year = filing_dt[0:4]
        month = filing_dt[4:6]
        day = filing_dt[6:8]
        filename = edgar_file.split('/')[-1]
        target_folder = '{}/{}/{}/{}/{}'.format(base_folder, year, month, day, cik)
        target_file = '{}/{}_{}'.format(target_folder, form_id, filename)
        return target_folder, target_file

    def download_forms(self, target_folder, target_idx, forms):
        fileCount = 0
        target_csv = self.get_form_csv_target_file(target_idx)
        if FileHelper.does_file_exists(target_csv):
            print('...Reading: {}'.format(target_csv))
            with open(target_csv, mode="r", encoding="utf-8") as csvFile:
                csvReader = csv.DictReader(csvFile)
                for row in csvReader: 
                    if row['form_id'] in forms:
                        FileHelper.create_dir_tree(row['target_folder'])
                        print('......Target file: {}'.format(row['target_file']))
                        print('......downloaded: {}'.format(row['form_url']))
                        if not FileHelper.does_file_exists(row['target_file']):
                            FileHelper.download_file(src_url=row['form_url'], target_file=row['target_file'])
                        fileCount += 1
        print('Files dowloaded: {}'.format(fileCount))
        
    def download_qtr_forms(self, index_year, index_qtr, forms=['4', '8-K', '10-K', '10-Q']):
        print('Downloading forms: {}-{}'.format(index_year, index_qtr))
        target_folder, target_idx = self.get_qtr_form_idx_target_file(index_year, index_qtr)
        self.download_forms(target_folder, target_idx, forms)
                            
    def download_daily_forms(self, index_date, forms=['4', '8-K', '10-K', '10-Q']):
        print('Downloading forms: {}'.format(index_date))
        form_idx_url = self.get_daily_form_idx_url(dt=index_date)
        target_folder, target_idx = self.get_daily_form_idx_target_file(form_idx_url=form_idx_url)
        self.download_forms(target_folder, target_idx, forms)
