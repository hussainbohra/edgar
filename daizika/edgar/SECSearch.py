import json
from edgar import SECHelper
from utils import FileHelper, RDSHelper

class SECSearchProcessor:
    def __init__(self, rds_config_file):
        self.rdsProcessor = RDSHelper.RDSProcessor(rds_config_file)
        self.SECDataFolder = SECHelper.SECDataFolder()

    def get_search_target_filename(self, batch_id):
        target_folder = self.SECDataFolder.search_base_folder
        target_file = '{}/cloudsearch_{}.json'.format(target_folder, batch_id)
        return target_folder, target_file
        
    def generate_documents(self):
        batch_limit = 50000
        sql_query = 'select distinct cik, name from (select cik, company_name name from edgar.tbl_sec_fillings union all select cik, name from edgar.tbl_sec_metadata union all select cik, name from edgar.tbl_sec_namechanges) a'
        result = self.rdsProcessor.get_query(sql_query)
        cik_data = {}
        for each_record in result:
            cik = int(each_record['cik'])
            name = each_record['name']
            if cik not in cik_data:
                cik_data[cik] = []
            cik_data[cik].append(name)
        cik_json = []
        nrecords = 0
        nbatch = 0
        for cik in cik_data:
            data = {'type':'add', 'id':cik, 'fields': {'cik': cik, 'names': cik_data[cik] }}
            cik_json.append(data)
            nrecords += 1
            if nrecords > batch_limit:
                target_folder, target_file = self.get_search_target_filename(nbatch)
                FileHelper.create_dir_tree(target_folder)
                with open(target_file, 'w', encoding='utf-8') as outfile:
                    json.dump(cik_json, outfile)
                cik_json = []
                nrecords = 0
                nbatch += 1
        target_folder, target_file = self.get_search_target_filename(nbatch)
        FileHelper.create_dir_tree(target_folder)
        with open(target_file, 'w', encoding='utf-8') as outfile:
            json.dump(cik_json, outfile)
        print('...Documents generated: {}'.format(nbatch))
        
