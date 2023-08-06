import pandas as pd
import os

class CsvOperations:

    def read_csv():
        print(os.path.isfile("f/fm_crf.xlsx"))
        
    def write_to_csv(self,filepath):
        
        df = pd.DataFrame({'name': ['Raphael', 'Donatello'],
                   'mask': ['red', 'purple'],
                   'weapon': ['sai', 'bo staff']})
        df.to_csv(filepath)
        
      