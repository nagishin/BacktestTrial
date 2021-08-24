# Backtest Trial
【評価版】BacktestAssist & ChartCreator<br>
Bybit WSOT 2021期間中(～2021/9/17)は各ツールを公開します。<br>
（ツール全機能を使用可能ですが、評価版ではソースコード非公開となりますのでご了承ください。）<br>
<br>
各ツールの詳細は以下のnoteを参照してください。
* [バックテスト補助ツール「BacktestAssistant」](https://note.com/nagi7692/n/n0c874a0cf2b2)
* [時系列データ可視化ツール「ChartCreator」](https://note.com/nagi7692/n/n401a95653ad0)<br>
<br>

## 【使用方法】
## 1. リポジトリをクローンして使用する
### 1-1. リポジトリクローン
```
git clone https://github.com/nagishin/BacktestTrial.git
```
<br>

### 1-2. 必要パッケージのインストール
ツールを使用するために必要なパッケージをインストールします。<br>
また、テストデータの取得や加工に便利な以下のツールもインストールします。<br>
* [テストデータ取得＆加工ツール【DataUtility】](https://gist.github.com/nagishin/1677ffa401476e9e98191a04012ac189)
```
cd BacktestTrial
pip install -U -r requirements.txt
```
<br>

### 1-3. 使用環境のdistを解凍
<b>【Linux環境】</b>
* python3.7 -> dist_for_linux_py37.zip
* python3.8 -> dist_for_linux_py38.zip
* python3.9 -> dist_for_linux_py39.zip
<br>
<br>

<b>【Windows環境】</b>
* python3.7 -> dist_for_windows_py37.zip
* python3.8 -> dist_for_windows_py38.zip
* python3.9 -> dist_for_windows_py39.zip
<br>
<br>

解凍すると<b>dist</b>ディレクトリが作成されます。<br>
以下の構造となるように配置してください。<br>
<br>
【構築するディレクトリ/ファイル構造】
```
./trial_check.py (ライセンス有効期限確認)
./backtest_sample.py (バックテストサンプル スクリプト)
./dist (解凍するとできるディレクトリ)
   ∟__init__.py
   ∟backtest_assistant.py
   ∟chart_creator.py
   ∟/pytransform
      ∟__init__.py
      ∟_pytransform.so
```
<br>

### 1-4. 評価版ライセンス 有効期限チェック (任意)
<b>trial_check.py</b>を実行することでライセンスの有効日数を確認できます。
```
cd BacktestTrial
python trial_check.py
-> This license for lic_for_wsot will be expired in 23 days
```
<br>

### 1-5. サンプルバックテスト実行
<b>backtest_sample.py</b>を実行することでサンプルロジックのバックテストを行います。<br>

<b>ロジック</b><br>
* RSIから売買過熱を判断して逆張りする<br>
* RSIが20未満で買いエントリー / 80より大きいと売りエントリー
* RSIが50に到達したらイグジット

<b>対象データ</b>
* tickデータ ：　BitMEX 1h OHLCV

<b>対象期間</b>
* 2020/08/01 ～ 2020/08/31 (JST)

```
cd BacktestTrial
python backtest_sample.py
```

<b>バックテスト 実行結果</b>
```
[Result]
  [Time    ] 2020/08/01 09:00:00 - 2020/08/31 08:00:00
  [Balance ] 1.0 -> 1.0201 (+2.01%)  Sharpe Ratio:-0.0463
  [Orders  ] Total:28 (Open:0  Executed:28  Canceled:0)
  [Position] Max Long:10,000.0  Max Short:-10,000.0  Min Margin:11115.76%

[Execution statistics]  PF:1.58
  [Total   ] Count:28(Size:280,000)  PnL:+0.0354  Avr:+0.0013  Price Range:+497.5
  [Profit  ] Count:6(42.86%)  Sum:+0.096  Avr:+0.016  Max:+0.0388  MaxLen:2(+0.0464)
  [Loss    ] Count:8(57.14%)  Sum:-0.0607  Avr:-0.0076  Max:-0.0181  MaxLen:3(-0.0261)
  [Fee     ] Trade:0.018  Funding:-0.0027
  [Max risk]
    Drawdown       :-2.79%(-0.0293) 2020/08/31 00:00:00
    Unrealised loss:-4.28%(-0.0449) 2020/08/12 15:30:00

[Fiat balance]
  [Start ] 11,361.0 (Balance:1.0 Price:11361.0)
  [End   ] 11,860.7 (Balance:1.0201 Price:11627.0)
  [Result] 499.7 (+4.40%)  Sharpe Ratio:-0.2182

[Fiat execution statistics]  PF:1.08
  [Total   ] Count:28(Size:0)  PnL:+179  Avr:+6.0  Price Range:+0
  [Profit  ] Count:11(42.31%)  Sum:+2,481  Avr:+226.0  Max:+678  MaxLen:3(+176)
  [Loss    ] Count:15(57.69%)  Sum:-2,302  Avr:-153.0  Max:-939  MaxLen:3(-520)
  [Fee     ] Trade:0  Funding:0
  [Max risk]
    Drawdown       :-8.87%(-1,138) 2020/08/26 14:00:00
    Unrealised loss:-4.28%(-497) 2020/08/12 15:30:00
```
<br>

<b>結果チャート</b>
![結果チャート](https://user-images.githubusercontent.com/37642101/130594782-ee7bfc24-7f5f-433c-8208-17c5a4f99e46.png)
<br>
<br>
<br>

## 2. Google Colabで使用する
以下のnotebookより、Google Colabリンクを開いてください。<br>

[< GitHub Gist >【評価版】BacktestAssist & ChartCreator](https://gist.github.com/nagishin/3f6dade186a11719e33da19632b9ef9c)
<br>
<br>
<br>

## 3. 公開ロジックのバックテスト
* [平均様 バックテスト](https://gist.github.com/nagishin/06edb1244ca10d44041ad2c2c8d9a8ab)<br>
【参考】[れたすさん著 【BTC自動取引bot】HEIKIN_ORACLE_ver2.0](https://note.com/letasun/n/n9366d3055824)<br>
<br>

* [時刻アノマリー バックテスト](https://gist.github.com/nagishin/e79ec81cdef8a9b1dafed7eb65383fc1)<br>
【参考】[Hohetoさん著 ビットコイン価格における時刻アノマリーの存在](https://note.com/hht/n/nc0caf98477db)<br>
<br>

* [ドテンくん バックテスト](https://gist.github.com/nagishin/5804a8c07a21e7f4914e0f2389be513c)<br>
【参考】[ビットコイン自動売買bot「ドテンくん」の特徴と評判](https://jitekineko.com/investment-trade-bitcoin-dotenkun/)<br>
<br>

* [バブル相場用の回転ボット バックテスト](https://gist.github.com/nagishin/5a96bb2480d37582c33263f00c6f0717)<br>
【参考】[Hohetoさん著 バブル相場用の回転ボットのコンセプトとQuantZoneロジック](https://note.com/hht/n/n63022edc4610)<br>
<br>

* [養分ロングbot バックテスト](https://gist.github.com/nagishin/9f5fda6485d5d2f3c1d134e7028c4d0e)<br>
【参考】[ともいさん著 養分ロングbot【bybit用】](https://note.com/tomoiyuma/n/n35018ec09b4f)<br>
<br>
