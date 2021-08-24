# coding: utf-8
from datetime import datetime
import numpy as np
import pandas as pd

'''
【サンプルロジック】
　RSIから売買過熱を判断して逆張りする
　対象データ    ：BitMEX OHLCV (1h)
　テスト期間    ：2020/08/01～2020/08/31 (JST)
　ロジック概要
　　・RSIが20未満で買いエントリー / 80より大きいと売りエントリー
　　・RSIが50に到達したらイグジット
'''

#テスト期間
TEST_START = '2020/08/01 09:00:00+0900'
TEST_END   = '2020/08/31 09:00:00+0900'


#-------------------------------------------------------------------------------
# テスト前準備
#-------------------------------------------------------------------------------
import DataUtility as du

# テスト期間の日付文字列をUnix Timeに変換
start_ut = int(du.Time(TEST_START).unixtime()) # テスト開始時刻 (UnixTime)
end_ut   = int(du.Time(TEST_END).unixtime())   # テスト終了時刻 (UnixTime)

# DataUtilityを使用してBitMEX OHLCVを取得
df_ohlcv = du.Tool.get_ohlcv_from_bitmex(
                    start_ut         = start_ut - 3600 * 24,  # 取得開始(UnixTime)
                    end_ut           = end_ut,                # 取得終了(UnixTime)
                    period           = 60,                    # 時間足期間(分)
                    csv_path         = './data/ohlcv_1h.csv', # 取得結果保存先(CSVパス)
                    request_interval = 1.0)                   # RESTリクエスト待機時間(秒)

# RSI計算
rsi_term = 12
diff = df_ohlcv['close'].diff()
diff = diff[1:]
up, down = diff.copy(), diff.copy()
up[up < 0] = 0
down[down > 0] = 0
up_sma = up.rolling(window=rsi_term, center=False).mean()
down_sma = down.abs().rolling(window=rsi_term, center=False).mean()
rs = up_sma / down_sma
df_ohlcv['rsi'] = 100.0 - (100.0 / (1.0 + rs))

# OHLCVをテスト期間でfiltering
df_ohlcv = df_ohlcv[((df_ohlcv['unixtime'] >= start_ut) & (df_ohlcv['unixtime'] <= end_ut))]

# テストメインループ用のUnixTime・RSI配列
np_ut = df_ohlcv['unixtime'].values
np_rsi = df_ohlcv['rsi'].values


#-------------------------------------------------------------------------------
# テスト実行
#-------------------------------------------------------------------------------
from dist import BacktestAssistant

start_balance = 1.0   # テスト開始時の残高(BTC)
leverage      = 0     # 取引時のレバレッジ(0:クロスマージン, 1～:分離マージン)
lot           = 10000 # 取引ロットサイズ($)
rsi_line      = 20    # RSI閾値

# BacktestAssistant生成
# (BitMEX/bybit : BTC/USD設定)
test = BacktestAssistant(
       balance           = start_balance, # 初期証拠金
       trade_leverage    = leverage       # 取引 レバレッジ (0:クロスマージン, 1～:分離マージン)
       #max_leverage      = 100,          # 取引所 最大レバレッジ
       #losscut           = 50,           # 最低証拠金維持率(%) ロスカットライン
       #taker             = 0.075,        # テイカー手数料(%)
       #maker             = -0.025,       # メイカー手数料(%)
       #tick_mode         = 'ltp',        # ティックモード ('ltp' or 'bidask')
       #take_cost         = 0.5,          # 'ltp'の場合のみ 成行注文時の取引コスト(スプレッド)
       #contract_type     = 'inverse',    # 契約タイプ (inverse:BTC/USD, linear:BTC/JPY etc.)
       #trans_digits      = 8,            # 取引通貨 小数桁数 (BTC:8桁)
       #settle_digits     = 1,            # 決済通貨 小数桁数 (USD:1桁)
       #sharpe_ratio_unit = 86400         # シャープレシオ期間単位 (秒)
)
# コメントアウトは初期値 (必要に応じて設定変更する)

# Funding Rate設定
test.set_funding_rate(rate = 0.01)

# 出力オプション設定 (進捗率表示ON)
test.set_output_option(disp_progress = True)

# 出力オプション設定
test.set_output_option(
        disp_progress = True    # 進捗表示
        #tick_csv      = False, # tick履歴csv出力
        #order_csv     = True,  # 注文履歴csv出力
        #execution_csv = True,  # 約定履歴csv出力
        #position_csv  = True,  # ポジション履歴csv出力
        #balance_csv   = True,  # 残高履歴csv出力
        #chart_data    = True   # チャート連携データ出力
)
# コメントアウトは初期値 (履歴csvが不要ならFalseを設定)

# tickデータ設定 (1時間足OHLCVのopen, high, low, close価格をtickデータに展開)
test.preset_ltp_ticks_from_ohlcv_df(df_ohlcv)

# 初期処理 (テスト開始時刻を設定)
test.initialize(start_time = start_ut)

# テストループ
for i, t in enumerate(np_ut):

    # 指定時刻まで進める
    if test.time() < t:
        test.sleep_to_time(t)

    # 直前足RSI
    rsi = np_rsi[i-1] if i > 0 else 50

    # データ取得
    price   = test.get_price()       # 現在価格       : {ltp, bid, ask}
    pos     = test.get_position()    # 現在建玉       : {size, avr_entry, margin, etc.}
    orders  = test.get_open_orders() # アクティブ注文 : [{id, timestamp, status, etc.}, {},...]
    balance = test.get_balance()     # 現在残高       : float

    # ノーポジション
    if pos['size'] == 0:
        # 買われ過ぎ
        if rsi > 100 - rsi_line:
            res = test.market_order('Sell', lot) # 売りでエントリー
            if res['status_code'] == 400:
                print(res['message'])
        # 売られ過ぎ
        elif rsi < rsi_line:
            res = test.market_order('Buy', lot)  # 買いでエントリー
            if res['status_code'] == 400:
                print(res['message'])

    # ロングポジション
    elif pos['size'] > 0:
        # 売られ過ぎ解消
        if rsi > 50:
            res = test.market_order('Sell', abs(pos['size'])) # 売りでイグジット
            if res['status_code'] == 400:
                print(res['message'])

    # ショートポジション
    elif pos['size'] < 0:
        # 買われ過ぎ解消
        if rsi < 50:
            res = test.market_order('Buy', abs(pos['size'])) # 買いでイグジット
            if res['status_code'] == 400:
                print(res['message'])

# 建玉があればクローズ
pos = test.get_position()
if pos['size'] < 0:
    test.market_order('Buy', abs(pos['size']))
elif pos['size'] > 0:
    test.market_order('Sell', abs(pos['size']))

# 終了処理
results = test.terminate()

# 結果チャート出力
#file_path = 'result_chart.png'
#test.save_result_chart(file_path, tick_unit=3600, result_type='pnl',
#                       show_price=True, price_type='ohlcv', show_pos=True, show_fiat=True)


#-------------------------------------------------------------------------------
# 結果チャート作成
#-------------------------------------------------------------------------------
from dist import ChartCreator as cc

dict_data = results['data']
dict_statistics = results['statistics']
dict_chart = results['chart']

# レイアウトカスタマイズ
cc.initialize()
cc.settings['title'] = 'Result chart'

# X軸設定
cc.set_xaxis(start=0, end=0, is_unixtime=True)

# メインチャート(ax:0)
cc.add_subchart(ax=0, label="USD", grid=True)

# ローソクバー設定(OHLCV)
cc.set_ohlcv_df(df_ohlcv)

# 買い注文ポイント設定
cc.set_marker(dict_chart['buy']['timestamp'], dict_chart['buy']['price'], ax=0, color='blue', size=30.0, mark='^', name='Buy')

# 売り注文ポイント設定
cc.set_marker(dict_chart['sell']['timestamp'], dict_chart['sell']['price'], ax=0, color='red', size=30.0, mark='v', name='Sell')

# 清算注文ポイント設定
if len(dict_chart['liquid']['timestamp']) > 0:
    cc.set_marker(dict_chart['liquid']['timestamp'], dict_chart['liquid']['price'], ax=0, color='magenta', size=30.0, mark='D', name='Liquidation')

# RSIサブチャート(ax:1)
cc.add_subchart(ax=1, label="RSI", grid=True)

# RSI設定
cc.set_line(np_ut, np_rsi, ax=1, color='green', width=1.0, name='RSI')
cc.set_line([np_ut[0], np_ut[-1]], [rsi_line, rsi_line], ax=1, color='red', width=1.0, name='RSI_20')
cc.set_line([np_ut[0], np_ut[-1]], [100-rsi_line, 100-rsi_line], ax=1, color='blue', width=1.0, name='RSI_80')

# ポジション推移サブチャート(ax:2)
cc.add_subchart(ax=2, label="Position", grid=True)

# ポジション設定
cc.set_band(dict_chart['position']['unixtime'], dict_chart['position']['size'], dict_chart['position']['zero'], ax=2, up_color='blue', down_color='red',
            alpha=0.5, edge_width=1.0, edge_color='dimgray', line_mode='hv', name='Position')

# 損益推移サブチャート(ax:3)
cc.add_subchart(ax=3, label='PnL', grid=True)

# 損益設定
cc.set_line(dict_chart['pnl']['unixtime'], dict_chart['pnl']['unrealised_pnl'], ax=3, color='green', width=0.8, name='Unrealised')
cc.set_band(dict_chart['pnl']['unixtime'], dict_chart['pnl']['pnl'], dict_chart['pnl']['zero'], ax=3, up_color='skyblue', down_color='red',
           alpha=0.2, edge_width=1.0, edge_color='dimgray', name='PL')

# フィアット損益推移サブチャート(ax:4)
cc.add_subchart(ax=4, label='Fiat PnL', grid=True)

# フィアット損益設定
fiat_blc = dict_chart['pnl']['balance'] * dict_chart['pnl']['price']
fiat_start = fiat_blc[0]
fiat_blc = fiat_blc - fiat_start
fiat_unrel_blc = dict_chart['pnl']['unrealised_balance'] * dict_chart['pnl']['price']
fiat_unrel_blc = fiat_unrel_blc - fiat_start
cc.set_line(dict_chart['pnl']['unixtime'], fiat_unrel_blc, ax=4, color='green', width=0.8, name='Include unrealised')
cc.set_band(dict_chart['pnl']['unixtime'], fiat_blc, dict_chart['pnl']['zero'],
            ax=4, up_color='orange', down_color='red',
            alpha=0.2, edge_width=1.0, edge_color='dimgray', name='Balance')

# チャート生成
file_path = './result/result_chart'
cc.create_chart(file_path + ".png", "png")
cc.create_chart(file_path + ".html", "html")
