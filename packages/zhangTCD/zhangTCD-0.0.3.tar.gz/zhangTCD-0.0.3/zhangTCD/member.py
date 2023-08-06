import os
import numpy as np
import pandas as pd
from datetime import date
from .xls import xls

class member(xls):
    
    def __init__(self, code, ini_values=None):
            super().__init__(code)
            self.folder = self.root_folder +'/member/' + code
            self.list_file = self.root_folder + '/record/record.xlsx'
            self.record_file = self.folder + '/' + code + '.xlsx'
            # self.sfields, self.status = self.init_records(item='proj_update')
    
    def create_member(self):
        if super().create_case() == True:
            if self.create_folder(self.folder) is False:
                print("A folder named " + self.folder + " already exists.")
            self.status['code'] = 'Member_created'
            self.status['status'] = 'OK'
            self.status['stage'] ='induction'
            self.status['note'] ='Start literature review'
            self.status['project'] = 'TBA'
            self.status['start'] = date.today().strftime("%d/%m/%Y")
            # Create the record file
            self.create_case(file=self.record_file, sheet="updates", fields=self.sfields,record=self.status)
    
    def close_member(self):
        self.status['code'] = 'Member_graduated'
        self.status['status'] = 'OK'
        self.status['stage'] ='alumnus'
        self.status['note'] ='Leave group'
        self.status['project'] = 'NA'
        self.status['end'] = date.today().strftime("%d/%m/%Y")
        # Update the record file
        self.update_case(file=self.record_file, sheet="updates", fields=self.sfields,record=self.status)
        # Update the list file
        self.close_case()


    
        
    
    
        