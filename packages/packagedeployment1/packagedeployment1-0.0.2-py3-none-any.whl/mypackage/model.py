import pandas as pd

class CsvOperations:

    def read_csv(filepath):
        df = pd.read_csv(filename)
        print(df.to_string())
        
    def write_to_csv(filepath):
        
        df = pd.DataFrame({'name': ['Raphael', 'Donatello'],
                   'mask': ['red', 'purple'],
                   'weapon': ['sai', 'bo staff']})
        df.to_csv(filepath)
        
      