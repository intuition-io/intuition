{
    "strategie":
    {
        "debug": 1,
        "save": 1,
        "rebalance_period": 15,
        "refresh_period": 1,
        "window_length": 60,
        "stddev_window": 9,
        "vwap_window": 5,
        "long_window" : 30,
        "short_window" : 25,
        "threshold" : 0,
        "ignored": ["volume", "pouet"],
        "gradient_iterations": 5,
        "signal_frontier": 0.5,
        "decision_frontier": 0.5
    },
    "manager": {
        "name": "dokku-xav",
        "load_backup": 0,
        "connected": 0,
        "android": 0,
        "loopback": 60,
        "source": "mysql",
        "perc_sell": 1.0,
        "max_weight": 0.3,
        "sell_scale": 100,
        "buy_scale": 150
    },
    "components": [
        {
            "algorithm": "BuyAndHold",
            "source": "CSVSource",
            "manager": "Constant"
        }
    ],
    "truefx": {
        "user": "",
        "password": ""
    },
    "quandl": {
        "apikey": ""
    },
    "notifymyandroid": {
        "url_notify": "http://www.notifymyandroid.com/publicapi/notify",
        "url_check": "http://www.notifymyandroid.com/publicapi/verify",
        "apikey": ""
    },
    "twitter": {
        "user": "",
        "password": ""
    },
    "rss": {
        "rbloggers": "feeds.feedburner.com/RBloggers",
        "quantopian": "https://www.quantopian.com/feed",
        "unix": "http://www.unixgarden.com/index.php/feed",
        "reuters": "http://feeds.reuters.com/reuters/financialsNews",
        "news": "http://economie.trader-finance.fr/rss.php",
    }
}
