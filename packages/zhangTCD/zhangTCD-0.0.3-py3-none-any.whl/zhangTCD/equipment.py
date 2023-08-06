from zhangTCD import record
from datetime import date

class equipment(record):

    def __init__(self, code):
        super().__init__(code)
        self.folder = self.root_folder +'/equipment/' + code 
        self.file = self.root_folder + '/record/record.xlsx'
        self.proj_file = self.folder + '/' + code + '.xlsx'
        self.sfields, self.status = self.init_records(item='proj_update')

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
            self.create_case(file=self.proj_file, sheet="updates", fields=self.sfields,record=self.status)
    
    def get_proj_status(self):
        all_records, this_record = self.get_records(file=self.proj_file, sheet="updates", fields=self.sfields, record=self.status)
        display(all_records)
    
    def update_proj_status(self):
        self.update_case(file=self.proj_file, sheet="updates", fields=self.sfields,record=self.status)
    
    def close_proj(self):
        self.status['code'] = 'Proj_closed'
        self.status['status'] = 'close'
        self.status['owner'] = self.researcher
        self.status['note'] ='Project closed.'
        self.status['issue'] = 'No issues'
        self.status['end'] = date.today().strftime("%d/%m/%Y")
        self.update_case(file=self.proj_file, sheet="updates", fields=self.sfields,record=self.status)
        self.close_case()