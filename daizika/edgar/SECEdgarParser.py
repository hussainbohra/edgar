import re
import sys
import xml.etree.ElementTree as ET
import uuid
import json
import csv
from edgar import SECHelper
from utils import FileHelper, ParserUtils
from datetime import datetime
from bs4 import BeautifulSoup

class Form10KParser:
    def __init__(self, filename):
        self.filename = filename
        self.parsed_data = None

    def extract_tag(self, start_tag, end_tag, start_char_index, content):
        data = None
        endtag_end_index= start_char_index
        bFound, starttag_start_index, starttag_end_index = ParserUtils.get_tag_index(start_tag, start_char_index, content)
        if bFound:
            bFound, endtag_start_index, endtag_end_index = ParserUtils.get_tag_index(end_tag, starttag_end_index, content)
            data = content[starttag_end_index:endtag_start_index] 
        return data, endtag_end_index
    
    def get_key_value(self, dict_obj, key):
        value = None
        if key in dict_obj:
            value = dict_obj[key]
        return value
        
    def extract_sec_header(self, content):
        section_header = {}
        keys = ['FORM_TYPE', 'FORM_DATE', 'COMPANY_CIK', 'COMPANY_NAME', 'COMPANY_SIC', 'COMPANY_IRS', 'COMPANY_STATEOFINC' \
                   ,'BUSINESS_STREET', 'BUSINESS_CITY', 'BUSINESS_STATE', 'BUSINESS_ZIP', 'BUSINESS_PHONE' \
                   ,'MAIL_STREET', 'MAIL_CITY', 'MAIL_STATE', 'MAIL_ZIP']
        for key in keys:
            section_header[key] = None        
        char_index = 0
        if content is not None:
            data, char_index = self.extract_tag('<SEC-HEADER>', '</SEC-HEADER>', 0, content)
            temp_section_header = {}
            section_name = ''
            for line in data.split('\n'):
                if ':' in line:
                    line_parts = line.split(':')
                    key = line_parts[0].strip()
                    value = line_parts[1].strip()
                    if value == '':
                        section_name = key
                        if section_name == 'FORMER COMPANY':
                            if section_name not in temp_section_header:
                                temp_section_header[section_name] = []
                        else:
                            temp_section_header[section_name] = {}
                    else:
                        if section_name == '':
                            temp_section_header[key] = value
                        elif section_name == 'FORMER COMPANY':
                            element = {}
                            element[key] = value
                            temp_section_header[section_name].append(element)                
                        else:
                            temp_section_header[section_name][key] = value    
            section_header['FORM_TYPE'] = self.get_key_value(temp_section_header, 'CONFORMED SUBMISSION TYPE')
            section_header['FORM_DATE'] = self.get_key_value(temp_section_header, 'FILED AS OF DATE')
            if 'COMPANY DATA' in temp_section_header:
                section_header['COMPANY_CIK'] = self.get_key_value(temp_section_header['COMPANY DATA'], 'CENTRAL INDEX KEY')
                section_header['COMPANY_NAME'] = self.get_key_value(temp_section_header['COMPANY DATA'], 'COMPANY CONFORMED NAME')
                section_header['COMPANY_SIC'] = self.get_key_value(temp_section_header['COMPANY DATA'], 'STANDARD INDUSTRIAL CLASSIFICATION')
                section_header['COMPANY_IRS'] = self.get_key_value(temp_section_header['COMPANY DATA'], 'IRS NUMBER')
                section_header['COMPANY_STATEOFINC'] = self.get_key_value(temp_section_header['COMPANY DATA'], 'STATE OF INCORPORATION')
            if 'BUSINESS ADDRESS' in temp_section_header:
                section_header['BUSINESS_STREET'] = self.get_key_value(temp_section_header['BUSINESS ADDRESS'], 'STREET 1')
                section_header['BUSINESS_CITY'] = self.get_key_value(temp_section_header['BUSINESS ADDRESS'], 'CITY')
                section_header['BUSINESS_STATE'] = self.get_key_value(temp_section_header['BUSINESS ADDRESS'], 'STATE')
                section_header['BUSINESS_ZIP'] = self.get_key_value(temp_section_header['BUSINESS ADDRESS'], 'ZIP')
                section_header['BUSINESS_PHONE'] = self.get_key_value(temp_section_header['BUSINESS ADDRESS'], 'BUSINESS PHONE')
            if 'MAIL ADDRESS' in temp_section_header:
                section_header['MAIL_STREET'] = self.get_key_value(temp_section_header['MAIL ADDRESS'], 'STREET 1')
                section_header['MAIL_CITY'] = self.get_key_value(temp_section_header['MAIL ADDRESS'], 'CITY')
                section_header['MAIL_STATE'] = self.get_key_value(temp_section_header['MAIL ADDRESS'], 'STATE')
                section_header['MAIL_ZIP'] = self.get_key_value(temp_section_header['MAIL ADDRESS'], 'ZIP')
            section_header['NAME_CHANGES'] = {}
            key = ''
            if 'FORMER COMPANY' in temp_section_header:
                for currkey in temp_section_header['FORMER COMPANY']:
                    if 'FORMER CONFORMED NAME' in currkey:
                        key = currkey['FORMER CONFORMED NAME']
                    else:
                        value = currkey['DATE OF NAME CHANGE']
                        section_header['NAME_CHANGES'][key] = value
        return section_header, char_index

    def extract_single_document(self, start_index, content, extract_type):
        data, char_index = self.extract_tag('<DOCUMENT>', '</DOCUMENT>', start_index, content)
        document = None
        if data is not None:
            document = {}
            for line in data.split('\n'):
                if line == '<TEXT>':
                    break
                else:
                    line_stripped = line.strip()
                    if line_stripped is not None and len(line_stripped) > 0:
                        parts = line_stripped.replace('<', '').split('>', 2)
                        document[parts[0]] = parts[1]
            if document['TYPE'] in extract_type:
                html_data, html_index = self.extract_tag('<TEXT>', '</TEXT>', 0, data)
                document['TEXT'] = html_data
        return document, char_index

    def update_extract_type(self, extract_type_log, doc_type):
        all_extracted = True
        if doc_type in extract_type_log:
            extract_type_log[doc_type] = True
        for atype in extract_type_log:
            if extract_type_log[atype] == False:
                all_extracted = False
                break
        return all_extracted, extract_type_log
                
    def get_extract_type_log(self, extract_type):
        extract_type_log = {}
        for atype in extract_type:
            extract_type_log[atype] = False
        return extract_type_log
        
    def extract_multiple_documents(self, extract_type):
        content = FileHelper.get_content(self.filename)
        parsed_data = {}
        extract_type_log = self.get_extract_type_log(extract_type)
        if content is not None:
            section_header, char_index = self.extract_sec_header(content)
            if section_header is not None:
                parsed_data['section_header'] = section_header
                parsed_data['document'] = {}
                content_has_data = True
                doc_index = 0
                while content_has_data:            
                    document, char_index = self.extract_single_document(char_index, content, extract_type)
                    if document is not None:
                        parsed_data['document'][doc_index] = document
                        all_extracted, extract_type_log = self.update_extract_type(extract_type_log, document['TYPE'])
                        if all_extracted:
                            content_has_data = False
                        doc_index += 1
                    else:
                        content_has_data = False
        return parsed_data
        
    def parse_html(self, cik, filingdt):
        htmlParser = ParserUtils.HTMLParse(self.filename)
        return htmlParser.parse_html(cik, filingdt)
        
class FormProcessor:
    def __init__(self):
        self.SECDataFolder = SECHelper.SECDataFolder()
        
    def get_forms_list(self, form_type):
        base_folder = self.SECDataFolder.forms_base_folder
        yearfiles = FileHelper.get_files(folder=base_folder, prefix='*')
        #form_list = []
        for each_year in yearfiles:
            year = each_year.replace(base_folder + '/', '') 
            print('...{}'.format(year))
            monthfiles = FileHelper.get_files(folder=each_year, prefix='*')
            for each_month in monthfiles:
                month = each_month.replace(each_year + '/', '') 
                print('......{}'.format(month))
                dayfiles = FileHelper.get_files(folder=each_month, prefix='*')
                for each_day in dayfiles:
                    day = each_day.replace(each_month + '/', '') 
                    print('.........{}'.format(each_day))
                    cikfiles = FileHelper.get_files(folder=each_day, prefix='*')
                    for each_cik in cikfiles:
                        cik = each_cik.replace(each_day + '/', '') 
                        form_files = FileHelper.get_files(folder=each_cik, prefix='*')
                        for each_form in form_files:                            
                            form_filename = each_form.replace(each_cik + '/', '')
                            form_parts = form_filename.split('_', 1)
                            current_form_type = form_parts[0]
                            current_form_filename = form_parts[1]
                            if current_form_type == form_type:
                                each_form_data = {}
                                each_form_data['fullpath'] = each_form
                                each_form_data['form_type'] = form_type
                                each_form_data['form_dt'] = datetime(int(year), int(month), int(day))
                                each_form_data['cik'] = cik
                                each_form_data['form_name'] = current_form_filename
                                #form_list.append(each_form_data)
                                yield each_form_data
        #return form_list
    
    def get_metadata_base_folder(self):
        base_folder = self.SECDataFolder.extract_metadata_folder
        return base_folder
        
    def get_metadata_file(self):
        base_folder = self.get_metadata_base_folder()
        random_uuid = uuid.uuid4()
        target_file = '{}/metadata_{}.json'.format(base_folder, random_uuid)
        return base_folder, target_file

    def get_extract_cik_folder(self, form_type, cik, filing_dt, filename):
        base_folder = '{}/{}'.format(self.SECDataFolder.extract_cik_folder, cik)
        target_file = '{}/{}_{}_{}'.format(base_folder, form_type, filing_dt, filename)
        return base_folder, target_file
    
    def extract_documents(self, form_type, extract_type=['10-K'], metadata=True):
        form_list = self.get_forms_list(form_type)
        metadata_base_folder, metadata_target_file = self.get_metadata_file()
        FileHelper.create_dir_tree(metadata_base_folder)        
        for each_form in form_list:
            print('Processing: {}'.format(each_form['fullpath']))
            filepathname = each_form['fullpath']
            cik = each_form['cik']
            formParser = Form10KParser(filepathname)
            extracted_data = formParser.extract_multiple_documents(extract_type)
            if len(extracted_data) > 0: 
                if metadata:
                    with open(metadata_target_file, mode='a', encoding='utf8') as metaf:
                        out_json = json.dumps(extracted_data['section_header'], separators=(',', ':'), ensure_ascii=False)
                        metaf.write(out_json + "\n")
                filing_dt = extracted_data['section_header']['FORM_DATE']
                folder_created = False
                for doc_index in extracted_data['document']:
                    if 'TEXT' in extracted_data['document'][doc_index]:
                        embeddedfilename = extracted_data['document'][doc_index]['FILENAME']
                        embeddedcontent = extracted_data['document'][doc_index]['TEXT']
                        cik_base_folder, cik_target_file = self.get_extract_cik_folder(form_type, cik, filing_dt, embeddedfilename)
                        if not folder_created:
                            FileHelper.create_dir_tree(cik_base_folder)
                            folder_created = True
                        print('...writing: {}'.format(cik_target_file))
                        with open(cik_target_file, mode='w', encoding='utf8') as cikf:
                            cikf.write(embeddedcontent.lstrip())
            else:
                print('...document empty: {}'.format(each_form['fullpath']))
            print('...done'.format(each_form['fullpath']))

    def get_extracted_documents_list(self, form_type):
        base_folder = self.SECDataFolder.extract_cik_folder
        cikfiles = FileHelper.get_files(folder=base_folder, prefix='*')
        for each_cik in cikfiles:
            cik = each_cik.replace(base_folder + '/', '')
            doc_files = FileHelper.get_files(folder=each_cik, prefix='*')
            for each_doc in doc_files:                            
                doc_filename = each_doc.replace(each_cik + '/', '')
                doc_parts = doc_filename.split('_', 3)
                current_doc_type = doc_parts[0]
                current_doc_filingdt = doc_parts[1]
                current_doc_filename = doc_parts[2]
                if current_doc_type == form_type:
                    each_doc_data = {}
                    each_doc_data['fullpath'] = each_doc
                    each_doc_data['form_type'] = current_doc_type
                    each_doc_data['filing_dt'] = current_doc_filingdt
                    each_doc_data['cik'] = cik
                    each_doc_data['form_name'] = current_doc_filename
                    yield each_doc_data            
        
    def extract_text(self, form_type):
        doc_list = self.get_extracted_documents_list(form_type)
        json_base_folder = self.SECDataFolder.extract_json_folder
        FileHelper.create_dir_tree(json_base_folder)        
        for each_doc in doc_list:
            filepathname = each_doc['fullpath']
            cik = each_doc['cik']
            filingdt = each_doc['filing_dt']
            json_filename = '{}/{}-{}.json'.format(json_base_folder, filingdt, cik)
            print('Processing: {}'.format(filepathname))
            if not FileHelper.does_file_exists(json_filename):
                formParser = Form10KParser(filepathname)
                parsed_data = formParser.parse_html(cik, filingdt)
                with open(json_filename, mode='w', encoding='utf8') as jf:
                    out_json = json.dumps(parsed_data, separators=(',', ':'), ensure_ascii=False)
                    jf.write(out_json + "\n")
    
    def write_metadata_to_csv(self, csvMetadataFileWriter, csvNameChangeFileWriter, metadataFilePathName):
        with open(metadataFilePathName, mode='r', encoding='utf8') as jf:
            for line in jf:
                objJson = json.loads(line)
                data = {}
                filing_dt = objJson['FORM_DATE']
                if filing_dt is None:
                    filing_dt = '20170101'
                data['dt_file'] = datetime(int(filing_dt[0:4]), int(filing_dt[4:6]), int(filing_dt[6:8]))
                data['cik'] = objJson['COMPANY_CIK']
                data['name'] = objJson['COMPANY_NAME'].strip().replace('\\', '').replace('/', '')
                data['sic'] = objJson['COMPANY_SIC']
                data['irs'] = objJson['COMPANY_IRS']
                data['stateofinc'] = objJson['COMPANY_STATEOFINC']
                data['business_street'] = objJson['BUSINESS_STREET']
                data['business_city'] = objJson['BUSINESS_CITY']
                data['business_state'] = objJson['BUSINESS_STATE']
                data['business_zip'] = objJson['BUSINESS_ZIP']
                data['business_phone'] = objJson['BUSINESS_PHONE']
                data['mail_street'] = objJson['MAIL_STREET']
                data['mail_city'] = objJson['MAIL_CITY']
                data['mail_state'] = objJson['MAIL_STATE']
                data['mail_zip'] = objJson['MAIL_ZIP']
                csvMetadataFileWriter.writerow(data)
                for each_namechange in objJson['NAME_CHANGES']:
                    nm_data = {}
                    nm_data['dt_file'] = data['dt_file'] 
                    nm_data['cik'] = data['cik']
                    nm_data['name'] = each_namechange.strip().replace('\\', '').replace('/', '')
                    nm_dt = objJson['NAME_CHANGES'][each_namechange]
                    nm_data['dt_change'] = datetime(int(nm_dt[0:4]), int(nm_dt[4:6]), int(nm_dt[6:8]))
                    csvNameChangeFileWriter.writerow(nm_data)
        
    def convert_metadata_to_csv(self):
        metadata_base_folder = self.get_metadata_base_folder()
        metadata_tmp_folder = '{}/temp'.format(metadata_base_folder)
        FileHelper.create_dir_tree(metadata_tmp_folder)
        csvMetadataFile = '{}/metadata.csv'.format(metadata_tmp_folder)
        csvNameChangesFile = '{}/company_name_changes.csv'.format(metadata_tmp_folder)
        fMetadataFileWriter = open(csvMetadataFile, 'w', encoding="utf-8")
        metadata_keys = ['dt_file','cik','name','sic','irs','stateofinc' \
                         ,'business_street','business_city','business_state','business_zip','business_phone' \
                         ,'mail_street','mail_city','mail_state','mail_zip']
        csvMetadataFileWriter = csv.DictWriter(fMetadataFileWriter, metadata_keys)
        csvMetadataFileWriter.writeheader()
        fNameChangeFileWriter = open(csvNameChangesFile, 'w', encoding="utf-8")
        namechange_keys = ['dt_file','cik','name','dt_change']
        csvNameChangeFileWriter = csv.DictWriter(fNameChangeFileWriter, namechange_keys)
        csvNameChangeFileWriter.writeheader()
        metadatafiles = FileHelper.get_files(folder=metadata_base_folder, prefix='*.json')
        for each_file in metadatafiles:
            print('...processing: {}'.format(each_file))
            self.write_metadata_to_csv(csvMetadataFileWriter, csvNameChangeFileWriter, each_file)        
            print('......done')
        fMetadataFileWriter.close()
        fNameChangeFileWriter.close()
               
        