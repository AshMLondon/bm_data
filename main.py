#Balancing Mechanism.... trying to do something with raw_data

import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import requests, json, os

import altair as alt




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


    def load(self):
        with open(self.data_filename, 'r') as file:
            self.raw_data = json.load(file)



    def streamlit_display(self):

        first_date = date.fromisoformat(date.isoformat(model.df.min()["settlementDate"]))
        last_date = date.fromisoformat(date.isoformat(model.df.max()["settlementDate"]))

        values = st.sidebar.slider('Date range', first_date, last_date, (first_date, last_date), format="DD-MMM-YYYY")

        lower_date_select = values[0]  # date.isoformat(values[0])
        upper_date_select = values[1]  # date.isoformat(values[1])


        model.df = model.df.set_index(['settlementDate'])

        selected = model.df.loc[lower_date_select:upper_date_select]

        # now split by long and short
        # SHORT -- NIV is positive

        short = selected.loc[selected['netImbalanceVolume'] >= 0]
        long = selected.loc[selected['netImbalanceVolume'] < 0]

        #use a slider to set a threshold value to display
        short_low = round(short.min()["systemBuyPrice"] - 1)
        short_hi = min(500,round(short.max()["systemBuyPrice"] + 1))
        short_min = st.sidebar.slider("Min price when short", short_low, short_hi)


        #do some calcs to dispaly numbers / percentage above threshold
        short_all_len = short.shape[0]
        short_above = short.loc[short['systemBuyPrice'] >= short_min]
        short_filtered = short_above.shape[0]
        #set values below threshold to the threshold (gives a neat 'floor' for the graph)
        short.loc[short['systemBuyPrice'] < short_min, 'systemBuyPrice'] = short_min


        #now do it all again, but inverted, for 'long' data
        long_all_len = long.shape[0]
        long_low = round(long.min()["systemBuyPrice"] - 1)
        long_hi = max(150,round(long.max()["systemBuyPrice"] + 1))
        long_max = st.sidebar.slider("Max price when long", long_low, long_hi, long_hi)

        long_below = long.loc[long['systemBuyPrice'] <= long_max]
        long_filtered = long_below.shape[0]
        long.loc[long['systemBuyPrice'] >long_max, 'systemBuyPrice'] = long_max

        axis_override=st.sidebar.checkbox("Shrink Axes",value=False)



        st.write(
            f"SYSTEM SHORT {short_filtered} periods out of {short_all_len} price >={short_min}  = {round(short_filtered / short_all_len * 100, 1)}%")
        #st.line_chart(short, y="systemBuyPrice")

        y_choice = alt.Y('systemBuyPrice')
        if axis_override:
            y_choice = alt.Y('systemBuyPrice', scale=alt.Scale(domain=(50, 300), clamp=True))
        #TODO - could make the axes limits user defined


        chart=alt.Chart(short.reset_index()).mark_line().encode(
            y=y_choice,
            x=alt.X('settlementDate')
        )
        st.altair_chart(chart, use_container_width=True)






        st.write(
            f"SYSTEM LONG {long_filtered} periods out of {long_all_len} price <={long_max}  = {round(long_filtered / long_all_len * 100, 1)}%")
        #st.line_chart(long, y="systemBuyPrice")

        y_choice2 = alt.Y('systemBuyPrice')
        if axis_override:
            y_choice2 = alt.Y('systemBuyPrice', scale=alt.Scale(domain=(-100, 150), clamp=True))


        chart2=alt.Chart(long.reset_index()).mark_line().encode(
            y=y_choice2,
            x=alt.X('settlementDate')
        )
        st.altair_chart(chart2, use_container_width=True)




    def altair_chart_complicated(self):


        source = self.df
        threshold = 50

        bars = alt.Chart(source).mark_bar(color="steelblue").encode(
            x="Day:O",
            y="Value:Q",
        )

        highlight = bars.mark_bar(color="#e45755").encode(
            y2=alt.Y2(datum=threshold)
        ).transform_filter(
            alt.datum.Value > threshold
        )

        rule = alt.Chart().mark_rule().encode(
            y=alt.Y(datum=threshold)
        )

        label = rule.mark_text(
            x="width",
            dx=-2,
            align="right",
            baseline="bottom",
            text="hazardous"
        )

        combo=bars + highlight + rule + label
        combo.show()

    def altair_easy(self):

        '''
        chart=alt.Chart(model.df).mark_bar().encode(
            y=alt.Y('systemBuyPrice' ),
            x=alt.X('settlementDate')
        )
        '''


        scale_override=False

        y_choice=alt.Y('systemBuyPrice')
        if scale_override:
            y_choice = alt.Y('systemBuyPrice', scale=alt.Scale(domain=(0, 400), clamp=True))

        chart=alt.Chart(model.df).mark_line().encode(
            y=y_choice,
            x=alt.X('settlementDate')
        )



        #.scale(domain=(-200, 200))

        st.altair_chart(chart,use_container_width=True)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    model=Model()
    # print(model.df.describe())
    model.streamlit_display()

    # model.get_BOA_data_from_elexon()

    #model.altair_easy()




# See PyCharm help at https://www.jetbrains.com/help/pycharm/
