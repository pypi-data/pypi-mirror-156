from .xls import xls
from datetime import date
import pandas as pd

class record(xls):
    file_path = ''

    def __init__(self, record_type=None):
        record.file_path = xls.root_folder + '/record/record.xlsx'
        if record_type is None: # this is to deal with a selected record
            if xls.sheet_selected == '':
                print('Please use record.search() and select 1 record. Alternatively define code and record_type.')
                self.valid = False
                return None
            else:
                use_selected = True
                code = xls.record_selected['code']
                sheet = xls.sheet_selected
                self.valid = True
        else:
            use_selected = False
            code = 0
            sheet = record_type
            self.valid = True
        
        # For record, the sheet_type is the same as the sheet name
        super().__init__(code = code, sheet = sheet, sheet_type = sheet, file_type='record', file_path = record.file_path)
        
        if use_selected is True:
            xls.tmp_record = xls.record_selected
        else:
            self.record['code'] = self.records_on_sheet.shape[0] + 1
            xls.tmp_record = self.record
           
        self.update()
    
    @staticmethod
    def search(sheet):
        xls.search(sheet, 'record type', sheet, 'record', 'file', record.file_path)