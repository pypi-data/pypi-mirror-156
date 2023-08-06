# zhangTCD - Zhang lab research manage system

Maintain lab records and provide a range of data analysis tools

## Instructions
1. Install:
```
pip install zhangTCD
```
2. SharePoint folder:
```python
from zhangTCD import xls, record, raman
xls.researcher = 'HZZ'

# Set up root folder
xls.root_folder = '/Users/hongzhouzhang/Library/CloudStorage/OneDrive-SharedLibraries-TCDUD.onmicrosoft.com/TCDGroup-Zhang_Group - General' # HZ Mac
# xls.root_folder = 'E:\TCDUD.onmicrosoft.com\TCDGroup-Zhang_Group - General' # HZ Office PC
```
3. Data analysis:
```python
r1 = raman('S14-FORD-B6', 'MoS2', 532.0)
r1.smooth_baseline()
r1.find_peaks()
r1.process_peaks();
r1.peaks
```