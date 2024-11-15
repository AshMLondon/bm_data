#Balancing Mechanism.... trying to do something with raw_data

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import requests, json, os


from datetime import date,timedelta


class Model():

    def __init__(self):
        self.data_filename="data_stored3.json"
        self.raw_data=[]
        if os.path.isfile(self.data_filename):
            print("FILE EXISTS!")
            self.load()
        else:
            self.save_data_from_elexon()

        self.df = pd.DataFrame(self.raw_data)
        self.df['settlementDate'] = pd.to_datetime(self.df['settlementDate'])

        self.df.drop("systemSellPrice",axis=1)

    def save_data_from_elexon(self):
        print("NO FILE - HAVING TO LOAD FROM ELEXON")
        base_url="https://data.elexon.co.uk/bmrs/api/v1/balancing/settlement/system-prices/"
        start_date=date.fromisoformat("2022-10-01")
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
        # print(df.describe())def save_data_from_elexon(self):



    def get_BOA_data_from_elexon(self):
        #BidOffers first
        BO_url="https://data.elexon.co.uk/bmrs/api/v1/balancing/bid-offer/all"
        BOA_url="https://data.elexon.co.uk/bmrs/api/v1/balancing/acceptances/all"

        start_date=date.fromisoformat("2023-11-01")
        # end_date=date.fromisoformat("2024-01-31")
        #end_date = date.fromisoformat("2024-10-31")
        end_date=start_date

        keep_data=[]   #this is where we're going to store everything

        d=start_date

        while d<=end_date:
            print(d)
            period=0
            query=f"?settlementDate={date.isoformat(d)}&settlementPeriod={period}"

            #BOA first
            response = requests.get(BOA_url+query)
            if response.status_code!=200:
                print(response.status_code)
                print ("************PROBLEM!*************")
                quit()

            # print(response.json())
            returned_data=response.json()["data"]
            # print(returned_data)
            useful_fields=['settlementDate','settlementPeriod', 'systemSellPrice', 'bmUnit', 'levelFrom','levelTo']
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

        # with open(self.data_filename, 'w') as file:
        #     json.dump(keep_data, file, indent=2)
        #     # json.dump(description,file,indent=2)
        #
        # self.raw_data=keep_data


        # print(keep_data)
        # df=pd.DataFrame(keep_data)
        # print(df)
        # print(df.describe())def save_data_from_elexon(self):


    def load(self):
        with open(self.data_filename, 'r') as file:
            self.raw_data = json.load(file)

    def streamlit_display(self):

        first_date = date.fromisoformat(date.isoformat(model.df.min()["settlementDate"]))
        last_date = date.fromisoformat(date.isoformat(model.df.max()["settlementDate"]))

        values = st.sidebar.slider('Date range', first_date, last_date, (first_date, last_date), format="DD-MMM-YYYY")
        # st.write(values)
        # print(values)
        lower_date_select = values[0]  # date.isoformat(values[0])
        upper_date_select = values[1]  # date.isoformat(values[1])
        # st.write(lower_date_select,upper_date_select)

        # d1=date.fromisoformat("2024-02-01")
        # d2=date.fromisoformat("2024-03-01")
        # selected = model.df.loc[d1:d2]

        model.df = model.df.set_index(['settlementDate'])

        selected = model.df.loc[lower_date_select:upper_date_select]
        # print(selected.describe)

        # now split by long and short
        # SHORT -- NIV is positive

        short = selected.loc[selected['netImbalanceVolume'] >= 0]
        long = selected.loc[selected['netImbalanceVolume'] < 0]

        short_low = round(short.min()["systemBuyPrice"] - 1)
        short_hi = round(short.max()["systemBuyPrice"] + 1)
        # st.write(short_low,short_hi)
        # short_min=140
        short_min = st.sidebar.slider("Min price when short", short_low, short_hi)

        short_all_len = short.shape[0]
        short = short.loc[short['systemBuyPrice'] >= short_min]
        short_filtered = short.shape[0]

        long_all_len = long.shape[0]
        long_low = round(long.min()["systemBuyPrice"] - 1)
        long_hi = round(long.max()["systemBuyPrice"] + 1)
        long_max = st.sidebar.slider("Max price when long", long_low, long_hi, long_hi)

        long = long.loc[long['systemBuyPrice'] <= long_max]
        long_filtered = long.shape[0]

        st.write(
            f"SYSTEM SHORT {short_filtered} periods out of {short_all_len} price >={short_min}  = {round(short_filtered / short_all_len * 100, 1)}%")
        st.line_chart(short, y="systemBuyPrice")
        st.write(
            f"SYSTEM LONG {long_filtered} periods out of {long_all_len} price <={long_max}  = {round(long_filtered / long_all_len * 100, 1)}%")
        st.line_chart(long, y="systemBuyPrice")

        # selected=model.df.loc[lower_date_select<model.df['settlementDate']<=upper_date_select]
        # selected=model.df.loc[2<=int(model.df['settlementPeriod'])<=6]

        # selected=model.df.loc[lower_date_select:upper_date_select]

        # print(selected.describe())

        # st.line_chart(selected,y="systemSellPrice")

        # model.df.to_csv('data_out.csv')

        # quit()
        # model.df.plot()
        # plt.show()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    model=Model()


    print(model.df.describe())
    model.streamlit_display()





# See PyCharm help at https://www.jetbrains.com/help/pycharm/
