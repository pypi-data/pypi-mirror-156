from .xls import xls
from datetime import date
import pandas as pd

from IPython.display import HTML, Latex, display, clear_output
import ipywidgets as widgets

class reference(xls):
    file_path = ''
    method = ''
    def __init__(self, material=None, method=None, update = None):
        # set temperary code as 'tmp'
        if material is None:
            if xls.sheet_selected == '':
                print('Please use reference.search() and select 1 reference. Alternatively define material and method.')
                self.valid = False
                return None
            else:
                use_selected = True
                self.valid = True
                code = xls.record_selected['code']
                sheet = xls.sheet_selected
                file_type = xls.file_type_selected
        else:
            use_selected = False
            self.valid = True
            code = 0
            sheet = material
            file_type = method
            
        reference.file_path = xls.root_folder + "/reference/" + file_type + ".xlsx"
        reference.method = file_type
        
        super().__init__(code = code, sheet = sheet, sheet_type = 'reference', file_type = file_type, file_path = reference.file_path)
        if use_selected is False:
            self.record['code'] = self.records_on_sheet.shape[0] + 1
            xls.tmp_record = self.record
        else:
            xls.tmp_record = xls.record_selected
        if update is None:
            #self.update()
            pass
    
    @staticmethod
    def search():
        material = 'MoS2'
        method = 'raman'
        xls.search(material, 'material', 'reference', method, 'method', xls.root_folder + "/reference/" + method + ".xlsx")

    @staticmethod
    def list_records(sheet, sheet_type, file_type, file):
        fields = xls.get_fields(file_type, sheet_type)
        if len(fields) == 0:
            return pd.DataFrame()
        try:
            record_on_sheet = pd.read_excel(file, engine='openpyxl', sheet_name=sheet, names = fields)
            record_on_sheet.insert(loc=0, column = 'material', value= sheet)
            return record_on_sheet
        except:
            print("No record found.")
            return pd.DataFrame()
    
    @staticmethod
    def all_records():
        xl = pd.ExcelFile(reference.file_path)
        data = pd.concat([reference.list_records(sheet, 'reference', reference.method, reference.file_path) for sheet in xl.sheet_names])
        return data
    
    def get_peak(self, code):
        data = self.records_on_sheet[self.records_on_sheet['code'] == code]
        display(data)
        data = data.iloc[0]
        return {'label': data['label'], 'cen': float(data['cen']), 'wid': float(data['wid']), 'amp': float(data['amp'])}

        

         