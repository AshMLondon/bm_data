#Balancing Mechanism.... trying to do something with raw_data

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import pandas as pd
import requests, json, os

from datetime import date,timedelta


class Model():

    def __init__(self):
        self.data_filename="data_stored.json"
        self.raw_data=[]
        if os.path.isfile(self.data_filename):
            print("FILE EXISTS!")
            self.load()
        else:
            self.save_data_from_elexon()

        self.df = pd.DataFrame(self.raw_data)

    def save_data_from_elexon(self):
        print("NO FILE - HAVING TO LOAD FROM ELEXON")
        base_url="https://data.elexon.co.uk/bmrs/api/v1/balancing/settlement/system-prices/"
        start_date=date.fromisoformat("2023-11-01")
        # end_date=date.fromisoformat("2024-01-31")
        end_date = date.fromisoformat("2024-10-31")

        keep_data=[]   #this is where we're going to store everything

        d=start_date

        while d<=end_date:
            print(d)

            full_url=base_url+date.isoformat(d)
            # print(full_url)

            response = requests.get(full_url)
            if response.status_code!=200:
                print(response.status_code)
                print ("************PROBLEM!*************")
                quit()


            # print(response.json())
            returned_data=response.json()["data"]
            # print(returned_data)
            useful_fields=['settlementDate','settlementPeriod', 'systemSellPrice', 'systemBuyPrice','netImbalanceVolume']
            for datapoint in returned_data:
                line=""
                data_to_keep={}
                for useful_field in useful_fields:
                    line+=useful_field+": "+str(datapoint[useful_field])+"   "
                    data_to_keep[useful_field]=datapoint[useful_field]

                keep_data.append(data_to_keep)
                #print(line)

                # setl_date=datapoint["settlementDate"]
                # setl_period=datapoint[""]

            d += timedelta(days=1)

        with open(self.data_filename, 'w') as file:
            json.dump(keep_data, file, indent=2)
            # json.dump(description,file,indent=2)

        self.raw_data=keep_data


        # print(keep_data)
        # df=pd.DataFrame(keep_data)
        # print(df)
        # print(df.describe())

    def load(self):
        with open(self.data_filename, 'r') as file:
            self.raw_data = json.load(file)




# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    model=Model()
    # model.get_data_from_elexon()
    # model.load()
    print(model.df.describe())

    #let's try picking only a certain period
    new_df=model.df.loc[model.df['settlementPeriod']==1]
    print(new_df)
    print(new_df.describe())



# See PyCharm help at https://www.jetbrains.com/help/pycharm/
