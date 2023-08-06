from .xls import xls
from datetime import date
import pandas as pd

class project(xls):
    
    def __init__(self, code):
        super().__init__(code)
        self.list_file = self.root_folder + '/record/record.xlsx'
        self.record_file = self.folder + '/' + code + '.xlsx'

    def __repr__(self):
        return "{}({},{}):{} started from {} with a status of {}".format(type(self).__name__, self.record['code'], self.record['mode'], self.record['title'], self.record['start'], self.record['status'])
         
    def create_project(self):
        if super().create_case() == True:
            if self.create_folder(self.folder) is False:
                print("A folder named " + self.folder + " already exists.")
            self.status['code'] = 'Proj_created'
            self.status['status'] = 'close'
            self.status['owner'] = self.researcher
            self.status['note'] ='Project created.'
            self.status['issue'] = 'No issues'
            self.status['start'] = date.today().strftime("%d/%m/%Y")
            # Create the record file
            self.create_case(file=self.record_file, sheet="updates", fields=self.sfields,record=self.status)
    
    def close_proj(self):
        self.status['code'] = 'Proj_closed'
        self.status['status'] = 'close'
        self.status['owner'] = self.researcher
        self.status['note'] ='Project closed.'
        self.status['issue'] = 'No issues'
        self.status['end'] = date.today().strftime("%d/%m/%Y")
        # Update the record file
        self.update_case(file=self.record_file, sheet="updates", fields=self.sfields,record=self.status)
        # Update the list file
        self.close_case()
        
        
