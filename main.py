import random
from datetime import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import math
from dateutil.relativedelta import relativedelta

crypto_prices = pd.read_csv('./crypto_data_updated_27_august.csv')  # max 1753 days
traders = {"Marcin": {'trader_id': 1}, "Krzysztof": {'trader_id': 2}, "Gabriela": {'trader_id': 3}}
money_to_invest = 100000


def convert_date_format(date):
    day = date.day
    month = date.month
    year = date.year
    if day < 10:
        day = f"0{day}"
    if month < 10:
        month = f"0{month}"
    date = f"{day}/{month}/{year}"
    return date


def reformat_crypto_dataframe():
    to_delete = ['Volume (BNB)', 'Volume (BTC)', 'Volume (ETH)', 'Volume (USDT)']
    to_change = ['Adj Close (BNB)', 'Adj Close (BTC)', 'Adj Close (ETH)', 'Adj Close (USDT)']
    change_to = ['BNB', 'BTC', 'ETH', 'USDT']

    for x in range(4):
        crypto_prices.drop(to_delete[x], inplace=True, axis=1)
        crypto_prices.rename(columns={to_change[x]: change_to[x]}, inplace=True)


def made_date_timeline(number_of_days):
    date_timeline = []
    support_trader_id = 1
    today = datetime(2022, 8, 27).date()
    while support_trader_id <= number_of_days:
        date_timeline.append(today)
        today -= relativedelta(days=1)
        support_trader_id += 1
    return date_timeline[::-1]


def dollar_bank_account(number_of_traders, start_money):
    dollar_bank_map = {}
    for trader_id in range(1, number_of_traders + 1):
        dollar_bank_map[trader_id] = start_money
    return dollar_bank_map


def crypto_bank_account(number_of_traders):
    crypto_bank_map = {name: {asset: 0 for asset in crypto_prices.columns[1:]} for name in
                       range(1, number_of_traders + 1)}
    return crypto_bank_map


def buy_or_sell_crypto(trader, dollar_bank, crypto_bank, date):
    side = random.choice(('buy', 'sell'))
    asset = random.choice(crypto_prices.columns[1:])
    value_of_asset = crypto_prices[asset][crypto_prices.index[crypto_prices['Date'] == date].tolist()].values.astype(
        int)
    if value_of_asset == 0:
        value_of_asset = 1
    if side == "buy":
        how_many_available = int(dollar_bank[trader] / value_of_asset)
        if how_many_available > 0:
            amount = random.randint(1, how_many_available)
            crypto_bank[trader][asset] += amount
            dollar_bank[trader] -= int(value_of_asset * amount)
            return {'asset': asset, 'amount': amount, 'side': side}
        else:
            return buy_or_sell_crypto(trader, dollar_bank, crypto_bank, date)
    else:
        crypto_amount = crypto_bank[trader][asset]
        if crypto_amount > 0:
            amount = random.randint(1, crypto_amount)
            crypto_bank[trader][asset] -= amount
            dollar_bank[trader] += int(value_of_asset * amount)
            return {'asset': asset, 'amount': amount, 'side': side}
        else:
            return buy_or_sell_crypto(trader, dollar_bank, crypto_bank, date)


def randomize_trades(number_of_trades, number_of_traders, number_of_days, start_money):
    crypto_bank_history = []
    dollar_bank_history = []
    list_of_trades = []
    support_trader_id = 1
    dollar_bank = dollar_bank_account(number_of_traders, start_money)
    crypto_bank = crypto_bank_account(number_of_traders)
    for date in made_date_timeline(number_of_days):
        for trade_number in range(number_of_trades * number_of_traders):
            if support_trader_id == number_of_traders + 1:
                support_trader_id = 1
            info = buy_or_sell_crypto(support_trader_id, dollar_bank, crypto_bank, convert_date_format(date))
            list_of_trades.append(
                {
                    'date': date,
                    'asset': info['asset'],
                    'qty': info['amount'],
                    'trader_id': support_trader_id,
                    'side': info['side']

                })
            crypto_bank_history.append(
                {'date': date,
                 'trader_id': support_trader_id,
                 'BNB': crypto_bank[support_trader_id]['BNB'],
                 'BTC': crypto_bank[support_trader_id]['BTC'],
                 'ETH': crypto_bank[support_trader_id]['ETH'],
                 'USDT': crypto_bank[support_trader_id]['USDT'],
                 })

            dollar_bank_history.append({
                'date': date,
                'trader_id': support_trader_id,
                'amount': int(dollar_bank[support_trader_id])

            })
            support_trader_id += 1
    all_data_dictionary = {
        'trades': pd.DataFrame(list_of_trades),
        'crypto_bank': crypto_bank,
        'dollar_bank': dollar_bank,
        'crypto_history': pd.DataFrame(crypto_bank_history),
        'dollar_history': pd.DataFrame(dollar_bank_history)
    }
    return all_data_dictionary


def info_about_exactly_trader(trader, data):
    exactly_trader_data_dictionary = []
    for result in data:
        if isinstance(data[result], dict):
            exactly_trader_data_dictionary.append(data[result][trader])
        else:
            exactly_trader_data_dictionary.append(
                data[result].loc[data[result]['trader_id'] == trader])
    return exactly_trader_data_dictionary


def make_trader_id_map(traders_list):
    trader_id_map = {}
    for trader_id in range(1, trades['trader_id'].max() + 1):
        for name in traders_list:
            if traders_list[name]['trader_id'] == trader_id:
                trader_id_map[traders_list[name]['trader_id']] = name
                break
            trader_id_map[trader_id] = f"Unknown{trader_id}"
    return trader_id_map


def crypto_amount_for_each_trader_with_subplot():
    x = 1
    res = data_dictionary['crypto_bank']
    plt.figure(figsize=(8, 6))
    trader_id_map = make_trader_id_map(traders)
    for trader_id in res:
        plt.subplot(math.floor(len(trades.columns) / 2), math.ceil(len(trades.columns) / 2), x)
        plt.title(trader_id_map[trader_id])
        plt.tight_layout()
        plt.bar(res[trader_id].keys(), list(res[trader_id].values()))
        x += 1
    plt.show()


def crypto_amount_for_each_trader_in_one_plot():
    res = data_dictionary['crypto_bank']
    plt.figure(figsize=(8, 6))
    plt.grid()
    bar_width = 0.15
    bars = []
    traders_list = make_trader_id_map(traders)
    for trader_id in res:
        if trader_id == 1:
            bars.append(np.arange(len(list(res[trader_id].values()))))
        else:
            bars.append([i + bar_width for i in bars[trader_id - 2]])
        plt.bar(bars[trader_id - 1], list(res[trader_id].values()), width=bar_width, label=traders_list[trader_id])
    plt.legend()
    plt.xticks(bars[0] + (bar_width + bar_width / 2), list(res[1].keys()))
    plt.show()


def crypto_amount_history_plot_for_each_trader():
    trader_id_map = make_trader_id_map(traders)
    for x in range(1, trades['trader_id'].max() + 1):
        plt.figure(x, figsize=(12, 6))
        nr_of_plot = 1
        for asset in crypto_prices.columns[1:]:
            plt.subplot(3, 2, nr_of_plot)
            trader_trades = trades.loc[trades['trader_id'] == x]
            trader_trades_2 = trader_trades.loc[trader_trades["asset"] == asset]
            plt.plot(trader_trades_2.get('date'), trader_trades_2.get('qty'))
            plt.xticks(fontsize=5)
            plt.title(asset)
            nr_of_plot += 1
        plt.suptitle(trader_id_map[x])
        plt.tight_layout()
    plt.show()


def dollar_history_plot():
    trader_id_map = make_trader_id_map(traders)
    plt.figure(figsize=(12, 6))
    for x in range(1, trades['trader_id'].max() + 1):
        plt.subplot(2, 2, x)
        info = info_about_exactly_trader(x, data_dictionary)[4]
        plt.plot(info.get('date'), info.get('amount'))
        plt.title(trader_id_map[x])
        plt.xticks(fontsize=5)
    plt.suptitle("Bank Account History")
    plt.show()


def sell_all_crypto():
    crypto = data_dictionary['crypto_bank']
    dollar = data_dictionary['dollar_bank']
    last_day = convert_date_format(data_dictionary['trades']['date'].max())
    for trader_id in crypto:
        for asset in crypto[trader_id]:
            value_of_asset = crypto_prices[asset][
                crypto_prices.index[crypto_prices['Date'] == last_day].tolist()].values.astype(
                int)
            dollar[trader_id] += int(value_of_asset * crypto[trader_id][asset])
            crypto[trader_id][asset] -= crypto[trader_id][asset]


def who_win():
    sell_all_crypto()
    res = data_dictionary['dollar_bank']
    plt.figure(figsize=(8, 6))
    trader_id_map = make_trader_id_map(traders)
    plt.bar(list(trader_id_map.values()), list(res.values()))
    plt.suptitle(f'Dollar money on the end\nStart money: {money_to_invest}')
    plt.show()


def crypto_history_prizes():
    plt.figure(figsize=(12, 6))
    for crypto_id in range(1, len(crypto_prices.columns[1:]) + 1):
        plt.subplot(2, 2, crypto_id)
        date = data_dictionary['trades']['date'].min()
        date_index = crypto_prices.index[crypto_prices['Date'] == convert_date_format(date)].tolist()[0]
        plt.plot(crypto_prices.get('Date')[date_index:].values,
                 list(crypto_prices.get(crypto_prices.columns[crypto_id])[date_index:].values))
        plt.title(crypto_prices.columns[crypto_id])
        plt.xticks(fontsize=5)
    plt.suptitle("Crypto prize history")
    plt.show()


reformat_crypto_dataframe()
data_dictionary = randomize_trades(1, 4, 100, money_to_invest)  # max 1753 days
trades = data_dictionary['trades']
crypto_amount_for_each_trader_in_one_plot()
crypto_amount_for_each_trader_with_subplot()
crypto_amount_history_plot_for_each_trader()
dollar_history_plot()
crypto_history_prizes()
who_win()
