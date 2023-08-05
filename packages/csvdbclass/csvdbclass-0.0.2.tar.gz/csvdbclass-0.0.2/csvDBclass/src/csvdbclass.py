import pandas as pd
import os


class csvDB:
    def __init__(self, CSV_name, db=0):
        if db == 0:
            db = pd.DataFrame()
        self.name = CSV_name
        self.db = db
        self.path = str(os.getcwd()) + "/" + self.name
        db.to_csv(CSV_name)
    
    def show(self):
        print(self.name)
        print(self.db)

    def update(self):
        if os.path.exists(self.path):
            self.destroy()
            self.db.to_csv(self.name)
        else:
            raise Exception("CSV path not found, please make sure csv was not moved.")
    def destroy(self):
        os.remove(str(os.getcwd()) + "/" + self.name)