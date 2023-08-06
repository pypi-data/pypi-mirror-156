from importlib import resources
import io
import os
import numpy as np
import pandas as pd
from datetime import date

import webbrowser

from IPython.display import HTML, Latex, display, clear_output
import ipywidgets as widgets

class xls():
    researcher = ''  # The researcher's code, e.g. HZZ, this should be defined
    root_folder = '' # The folder (on the researcher's own computer) of the TEAM SharePoint 
    
    # The quantities below are selected by xls.search() function
    sheet_selected = ''
    file_type_selected =''
    record_selected = {}
    tmp_selected = pd.DataFrame()
    
    # The record below used for xls.update() function  
    tmp_record = {}
    
    def __init__(self, code, sheet, sheet_type, file_type, file_path):
        """
        code: the code, unique identifier for each record in the spreadsheet file, which should be an integer
        sheet: the sheet name
        
        The paras below is to extract the fields in the setup.xlsx file
        sheet_type: this is the sheet_name when the spreadsheet is not a reference type; For reference-type file, it must be reference.
        file_type: this is the class name of the record, e.g. record, member, project
        file_path: the full path to the spreadsheet - this should be a class variable for each child class.
        """
        # Set up the path of the record file
        if xls.root_folder == '':
            print('Warning: please set the full path of the TEAM/Projects folder: record.root_folder = your_folder_path')
            return None
        self.file_path = file_path 
        self.file_type = file_type 
        self.sheet = sheet 
        self.sheet_type = sheet_type 
        
        # Initiate the records: 
        # self.fields is a list, which lists the fields of the spreadsheet (self.sheet)
        # self.record is a dict, which saves the current record - only 1 record
        self.fields, self.record = self.init_records(code)  #self.record is the record of this instance (i.e. one row in the sheet)
        
        # Read the record from the spreadsheet
        # self.records_on_sheet is a dataFrame, which contains all the records on self.sheet.
        # If the code already exists, self.record is updated to the existing record.
        self.records_on_sheet, self.record = self.get_records()
        
        # Set the modified status
        self.record['modifiedby'] = self.researcher
        self.record['modifiedon'] = date.today().strftime("%d/%m/%Y")

    def __repr__(self):
        return "\033[1mcode\033[0m={}, \033[1msheet\033[0m={}, \033[1msheet type\033[0m={}, \033[1mfile type\033[0m={}\n\033[1mfile path\033[0m={}.".format(self.record['code'], self.sheet, self.sheet_type, self.file_type, self.file_path)

    # Initiate the fields and records
    def init_records(self, code):
        # Get the fields of the spreadsheet from /record/.utilities/setup.xlsx
        fields = xls.get_fields(self.file_type, self.sheet_type)
        
        # initilise the values for each field and convert it into a dictionary
        values = [None] * len(fields)        
        record = dict(zip(fields, values))
        record['code'] = code
        return fields, record
    
    @staticmethod
    def get_fields(file_type, sheet_type):
        # Get the fields of the spreadsheet: this ensures the proper path being generated.
        with resources.open_binary('zhangTCD', 'setup.xlsx') as fp:
            file = fp.read()
        io.BytesIO(file)
        try:
            setup = pd.read_excel(io.BytesIO(file), engine='openpyxl', names=["file_type", "sheet_type", "fields"]) # setup reads in all the fields in the setup.xlsx file
            this = setup[(setup['file_type']==file_type) & (setup['sheet_type']==sheet_type)] # this extract the record that is specified for the instance
            fields = this['fields'].to_list()[0].replace(" ", "") # Convert to list and remove space from the records 
            fields = ['code'] + ([] if fields == 'As_defined' else fields.split(","))+ ['modifiedby','modifiedon'] # add three universial fields: code, modifiedby, modifiedon
            return fields
        except:
            print('Check your inputs. No field can be extracted from the setup.xlsx.')
            return []
    
    @staticmethod
    def list_records(sheet, sheet_type, file_type, file):
        fields = xls.get_fields(file_type, sheet_type)
        if len(fields) == 0:
            return pd.DataFrame()
        try:
            record_on_sheet = pd.read_excel(file, engine='openpyxl', sheet_name=sheet, names = fields)
            return record_on_sheet
        except:
            print("No record found.")
            return pd.DataFrame()
    
    @staticmethod
    def search(sheet, sheet_name, sheet_type, file_type, file_type_name, file_path):
        xls.sheet_selected =''
        fields = xls.get_fields(file_type, sheet_type)
        if len(fields) == 0:
            print('Check file_type and sheet_type (setup.xlsx)')
            return False

        txt_sheet = widgets.Text(value=sheet, placeholder='sheet', description=sheet_name,
                                 disabled=False, continuous_update=True, orientation='horizontal',readout=True, readout_format='.1f',
                                 style = {'description_width': 'initial'}, layout=widgets.Layout(width='90%', height='100%'))
        txt_file_type = widgets.Text(value=file_type, placeholder='file type name', description=file_type_name,
                                 disabled=False, continuous_update=True, orientation='horizontal',readout=True, readout_format='.1f',
                                 style = {'description_width': 'initial'}, layout=widgets.Layout(width='90%', height='100%'))
        ck_openDOI = widgets.Checkbox(value=False,description='Open DOI (if applicable)', disabled=False,
                                      layout=widgets.Layout(width='100%', height='80%'), align_items='left')
        # critera for search database
        dp_c=[]
        txt_c=[]
        num_c = 3
        for i in range(num_c):
            dp_c.append(widgets.Dropdown(placeholder='criterion ' + str(i),options=fields, value=fields[0],
                                       description='criterion ' + str(i) + ':',
                                       disabled=False, continuous_update=True, orientation='horizontal',readout=True, readout_format='.1f',
                                       style = {'description_width': 'initial'}, layout=widgets.Layout(width='90%', height='90%')))
            txt_c.append(widgets.Text(value=None, placeholder='', description=' ',
                                 disabled=False, continuous_update=True, orientation='horizontal',readout=True, readout_format='.1f',
                                 style = {'description_width': 'initial'}, layout=widgets.Layout(width='100%', height='100%')))
        
        btn_select = widgets.Button(description='select record', disabled=False, 
                                    button_style='', tooltip='Click me', layout=widgets.Layout(width='60%', height='80%'), align_items='center')
            
        controls = widgets.interactive(xls.found, sheet=txt_sheet, sheet_type=sheet_type, file_type=txt_file_type, file =file_path,
                                       dc0=dp_c[0], c0 = txt_c[0], dc1=dp_c[1], c1 = txt_c[1],
                                       dc2=dp_c[2], c2 = txt_c[2]);
        
        output = controls.children[-1]
        grid =  widgets.GridspecLayout(2+num_c, 5)
        grid[0, :1]=txt_sheet
        grid[0, 1:2]=txt_file_type
        grid[0, 2]=ck_openDOI
        grid[0, 3]=btn_select
        for i in range(num_c):
            grid[i+1, :1] = dp_c[i]
            grid[i+1, 1:2] = txt_c[i]
        display(grid)
        display(widgets.VBox([output]))
        
        def on_btn_clicked_select(b):
            clear_output(wait=True)
            with output:
                if len(xls.tmp_selected.index) ==1:
                    xls.record_selected = xls.tmp_selected.to_dict('records')[0]
                    xls.sheet_selected = txt_sheet.value
                    xls.file_type_selected = txt_file_type.value
                    xls.record_selected['code'] = int(xls.record_selected['code'])
                    print("record selected (.record_selected).")
                    if ('doi' in xls.record_selected) and (ck_openDOI.value is True):
                        webbrowser.open('https://doi.org/' +  xls.record_selected['doi'], new=2)
                else:
                    print("Please select 1 record.")
        btn_select.on_click(on_btn_clicked_select)
    
    @staticmethod
    def found(sheet, sheet_type, file_type, file, dc0, c0, dc1, c1, dc2, c2):
        xls.tmp_selected = xls.list_records(sheet=sheet, sheet_type=sheet_type, file_type=file_type, file=file)
        if len(xls.tmp_selected.index) !=0:
            records = xls.tmp_selected.applymap(str)
            c = [c0, c1, c2]
            dc = [dc0, dc1, dc2]
            for i in range(len(c)):
                if len(c[i]) !=0:
                    records = records[records[dc[i]].isin([c[i]])]
            if len(records.index) != 0:
                display(HTML(records.to_html(index=False)))  
                xls.tmp_selected = records
            else:
                print("no record is found.")
                xls.tmp_selected = pd.DataFrame()
        else:
            print("no record is found.")
            xls.tmp_selected = pd.DataFrame()

    # update record
    def update(self):
        if self.valid is False:
            print('please select a recored.')
            return False
        fields=[]
        num_fields = len(self.fields)-2
        for i in range(1, num_fields):
            fields.append(widgets.Text(value=str(self.record[self.fields[i]]), placeholder='', description=self.fields[i],
                                 disabled=False, continuous_update=True, orientation='horizontal',readout=True, readout_format='.1f',
                                 style = {'description_width': 'initial'}, layout=widgets.Layout(width='100%', height='100%')))
        
        btn_save = widgets.Button(description='save', disabled=False, 
                                    button_style='', tooltip='Click me', layout=widgets.Layout(width='60%', height='80%'), align_items='center')
        btn_delete = widgets.Button(description='delete', disabled=False, 
                                    button_style='', tooltip='Click me', layout=widgets.Layout(width='60%', height='80%'), align_items='center')
   
        grid =  widgets.GridspecLayout(2+num_fields, 4)
        grid[0, :1] = widgets.HTMLMath(value=r"<b>Update the record:<b>",placeholder='title',description='')
        grid[0, 1] = btn_save
        grid[1, 1] = btn_delete
        for i in range(1, num_fields):
            grid[i, :1] = fields[i-1]
        display(grid)
        
        #Buttons operations: Save and delete
        def on_btn_clicked_save(b):
            self.record = xls.tmp_record
            self.save()
        btn_save.on_click(on_btn_clicked_save)
        
        def on_btn_clicked_delete(b):
            self.delete()       
        btn_delete.on_click(on_btn_clicked_delete)
        
        # Text field operations: Update fields
        def callback(wdgt):
            # replace by something useful
            xls.tmp_record[wdgt.description] = wdgt.value
        def on_change(change):
            if change["new"]!= change["old"]:
                xls.tmp_record[change["owner"].description] = change["new"]  
        for i in range(1, num_fields):
            fields[i-1].on_submit(callback)
            fields[i-1].observe(on_change, names =["value"])

    # Show current record, not saved yet
    def current(self):
        display(HTML(pd.DataFrame(self.record, index=[0]).to_html(index=False)))  

    # Get sheet from the file
    def get_records(self):
        try:
            record_on_sheet = pd.read_excel(self.file_path, engine='openpyxl', sheet_name=self.sheet, names = self.fields)
            if self.record['code'] in record_on_sheet.code.tolist():
                # Get the record from the file, and update self.record
                return record_on_sheet, record_on_sheet.loc[record_on_sheet['code'] == self.record['code']].to_dict('records')[0] # Convert the record into dict
            else:
                #print(record['code'])
                #print(record['code'] + " is a new record.")
                return record_on_sheet, self.record
        except:
            #print("This is a new record and I cannot find the datafile")
            return pd.DataFrame(self.record, index=[0]), self.record # No file can be found and/or no record on the sheet, create the sheet record

    def create(self):
        newdata = pd.DataFrame(self.record, index =[0]); 
        # Read the record from the spreadsheet
        try:
            self.records_on_sheet = pd.read_excel(self.file_path, engine='openpyxl', sheet_name=self.sheet, names = self.fields)
            if self.record['code'] in self.records_on_sheet.code.tolist():
                print("A record with the same code is on record. Please choose a new code if you wish to create a new record.")
                return False
            else:
                pass
        except:
            self.records_on_sheet = newdata
        self.save()
        
    def save(self):
        newdata = pd.DataFrame(self.record, index =[0]); 
        # Read the record from the spreadsheet
        try:
            self.records_on_sheet = pd.read_excel(self.file_path, engine='openpyxl', sheet_name=self.sheet, names = self.fields)
        except:
            self.records_on_sheet = newdata    
        
        self.records_on_sheet = pd.concat([self.records_on_sheet, newdata]).drop_duplicates(['code'], keep='last') #.sort_values(self.record['start'][0])
        self.records_on_sheet.reset_index(drop=True)
        
        try:
            writer = pd.ExcelWriter(self.file_path, engine='openpyxl', mode='a', if_sheet_exists='replace' )
        except:
            writer = pd.ExcelWriter(self.file_path)
        self.records_on_sheet.to_excel(writer, sheet_name=self.sheet, index=False)
        writer.save()
        print("We have saved the record: ")
        display(HTML(newdata.to_html(index=False)))
    
    def delete(self):
        # Read the record from the spreadsheet
        self.records_on_sheet, self.record = self.get_records()
        self.records_on_sheet = self.records_on_sheet[~self.records_on_sheet['code'].isin([self.record['code']])]
        try:
            writer = pd.ExcelWriter(self.file_path, engine='openpyxl', mode='a', if_sheet_exists='replace' )
        except:
            writer = pd.ExcelWriter(self.file_path)
        self.records_on_sheet.to_excel(writer, sheet_name=self.sheet, index=False)
        writer.save()
        print("The record is deleted")
        
        # Read the record from the spreadsheet
        self.all_records, self.record = self.get_records()
        

