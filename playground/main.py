#https://github.com/phoehne/EconoMetrics
import pandas.io.data as web
import EconoMetrics.transformers as trans
import EconoMetrics.charts as charts
import matplotlib.pyplot as plt

if __name__ == "__main__":
    dataframe = web.get_data_yahoo("MSFT", "09/01/2011", "09/01/2012")

    print dataframe[0:3]

    et = trans.EMATransformer()
    et.transform(dataframe)

    print dataframe[0:3]


    fig = plt.figure(figsize=(4,4))
    ax = fig.add_axes([0.1, 0.1, 0.8, 0.8])
    charts.highlow(ax, dataframe, width=0.6)
    #charts.candlestick(ax, dataframe, width=0.6)
    #plt.plot(dataframe["Close_EMA_5"])

    plt.show()
