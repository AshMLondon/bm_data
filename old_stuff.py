#OLD STUFF / ARCHIVE
#doesn't make sense on it's own - needs importing -- or putting back in main.py


def streamlit_display_OLD(self):
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


def get_BOA_data_from_elexon(self):
    # BidOffers first
    BO_url = "https://data.elexon.co.uk/bmrs/api/v1/balancing/bid-offer/all"
    BOA_url = "https://data.elexon.co.uk/bmrs/api/v1/balancing/acceptances/all"

    start_date = date.fromisoformat("2023-11-01")
    # end_date=date.fromisoformat("2024-01-31")
    # end_date = date.fromisoformat("2024-10-31")
    end_date = start_date

    keep_data = []  # this is where we're going to store everything

    d = start_date

    while d <= end_date:
        print(d)
        period = 1
        query = f"?settlementDate={date.isoformat(d)}&settlementPeriod={period}"

        # BOA first
        response = requests.get(BOA_url + query)
        if response.status_code != 200:
            print(response.status_code)
            print(response.json())
            print("************PROBLEM!*************")
            quit()
        # print(response.json())
        boa_data = response.json()["data"]
        print(boa_data)

        # now BidOffers
        response = requests.get(BO_url + query)
        if response.status_code != 200:
            print(response.status_code)
            print(response.json())
            print("************PROBLEM!*************")
            quit()
        # print(response.json())
        bidoffer_data = response.json()["data"]
        # print(bidoffer_data)
