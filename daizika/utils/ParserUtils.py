import re
from bs4 import BeautifulSoup
from bs4 import Comment

def get_tag_index(tag_name, start_index, content):
    bFound = False
    iter_char = start_index
    iter_char_end = len(content)
    tag_pointer_start = 0
    tag_pointer_end = len(tag_name)
    state = 0
    start_index = -1
    while iter_char < iter_char_end:
        if state == 0:
            if tag_name[tag_pointer_start] == content[iter_char]:
                tag_pointer_start = 1
                state = 1
        elif state == 1:
            if tag_name[tag_pointer_start] == content[iter_char]:
                tag_pointer_start += 1
                if tag_pointer_start == tag_pointer_end:
                    bFound = True
                    break
            else:
                tag_pointer_start = 0
                state = 0    
        iter_char += 1
    return bFound, iter_char - tag_pointer_end, iter_char + 1

class HTMLParse:
    def __init__(self, filename):
        self.filename = filename
        self.tags_to_skip =  []
        self.tags_to_consolidate = ['a', 'b', 'font', 'div'] 
        self.consolidated_name = 'X'
        
    def parse_children(self, parent_tag, root_key, html_parts, tag):
        if tag.name is not None and tag.name not in self.tags_to_skip and tag.contents is not None:
            child_tag = parent_tag
            if tag.name not in self.tags_to_consolidate:
                child_tag += tag.name + "/"
                root_key += 1
            #print('[{}:{}]: {}'.format(root_key, child_tag, "has_children"))
            for children in tag.contents:
                if not isinstance(children, Comment):
                    root_key = self.parse_children(child_tag, root_key, html_parts, children)
        else:
            if tag.string is not None and len(tag.string.strip()) > 0:
                #print('[{}:{}]: {}'.format(root_key, parent_tag, tag.string.strip()))
                data = tag.string.strip()
                if root_key not in html_parts:
                    html_parts[root_key] = {}
                if parent_tag not in html_parts[root_key]:
                    html_parts[root_key][parent_tag] = data
                else:
                    html_parts[root_key][parent_tag] += ' ' + data
        return root_key

    def get_html_parts(self):
        html_parts = {}
        with open(self.filename) as fp:
            soup = BeautifulSoup(fp, "html5lib")   
            root_key = 0
            for tag in soup.body.contents: 
                if tag.name is not None and tag.contents is not None:
                    #print('[{}:{}]: {}'.format(root_key, tag.name, "has_children"))
                    root_key = self.parse_children('/', root_key, html_parts, tag)
                    root_key += 1
        return html_parts

    def remove_nonascii_string(self, s):
        return re.sub(r'[^\x00-\x7f]',r' ', s)
    
    def get_cleaned_string(self, s):
        toRet = self.remove_nonascii_string(s).replace('\n', ' ').lower().strip()
        if toRet.startswith('i tem '):
            toRet = toRet.replace('i tem ', 'item ')
        return toRet
    
    def get_form_parts(self, html_parts):
        form_parts = {}
        part_key = ''
        item_key = ''
        for key in html_parts:
            for tag in html_parts[key]:
                data = html_parts[key][tag]
                cleaned_data = self.get_cleaned_string(data)
                #print('[{}:{}]: #{}#'.format(key, tag, cleaned_data[0:10]))
                if cleaned_data.startswith('part '):
                    part_key = cleaned_data
                    item_key = ''
                    form_parts[part_key] = {}
                elif cleaned_data.startswith('item '):
                    if part_key == '' and cleaned_data.startswith('item 1'):
                        part_key = "PART_INS"
                        form_parts[part_key] = {}
                    if part_key != '':
                        item_key = cleaned_data
                        form_parts[part_key][item_key] = []
                else:
                    if part_key != '' and item_key != '':
                        if part_key in form_parts and item_key in form_parts[part_key]:
                            form_parts[part_key][item_key].append(self.remove_nonascii_string(data))
        return form_parts
    
    def parse_html(self, cik, filingdt):
        print('...parsing: {}'.format(self.filename))
        parsed_data = {}
        parsed_data['cik'] = cik
        parsed_data['filingdt'] = filingdt        
        parsed_data['fullpath'] = self.filename   
        html_parts = self.get_html_parts()
        form_parts = self.get_form_parts(html_parts)                            
        parsed_data['text'] = form_parts        
        return parsed_data
