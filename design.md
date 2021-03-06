=== 設計 ===
大きく正規化と税金計算に分ける。

正規化処理のやる事は分かりやすい。
形式の定義に少し考える程度。

税金計算は一発で終わるわけではなくて継続的な処理になるだろう。
正規化済みファイルのインポートでも、取引所やタイミング別に複数ファイルになるし。
計算は取引所まとめても良いが、取引所残高の一致も見たいから独立に計算した方がいいかな。

あとは API から自動的に取り込む機能とかも付けたいところだ。
外部から相場データを取ってくる必要もある。これは一回取ったら保存しとくべきだろう。
永続状態を保管して、それをメンテする感じの構造がよさそうである。
相場データも保存。

あと重複処理も必要だな。
各取引所に取引ID あるだろうからそれを使う。
無ければハッシュ値を使うか。

税金計算は、総平均法を使うなら二段階になる。さらに、年で区切らないとならない。
年で計算法が変わる可能性もあるので、年終わり時点で原価と保有コインはまとめとくべきだろうな。
で、翌年の計算はそこから始める。

# 正規化
buy や withdrawal などの種別で必要な要素が少し違う。
JSON にすると楽だけども、テーブルに取り込みたい需要もありそうなので CSV にしとこう。
フィールドは最小公倍数にして、各タイプで使わないフィールドは空欄にする。

まず各取引所の取引データから項目を列挙してみる。
 * BitFlyer
   全てダブルクォート括り。
  - 取引日時: YYYY/MM/DD HH:MM:SS
  - 通貨: 売買は "通貨1/通貨2"
  - 取引種別: 証拠金引出、証拠金預入、外部送付、買い、入金、手数料、受取、売り
  - 取引価格: 通貨2単位の通貨1価格。売買以外はゼロ。
  - 通貨1:
  - 通貨1数量:
  - 手数料:
  - 通貨1の対円レート
  - 通貨2
  - 通貨2数量
  - 自己・媒介
  - 注文 ID
  - 備考

 * bitfinex
   全てクォート無し
  - #: 数値。取引番号であろう。
  - PAIR: ETH/USD など。
  - PRICE: PAIR そのままの割り算形式.
  - FEE
  - FEE PERC
  - FEE CURRENCY
  - DATE: DD-MM-YY HH:MM:SS
  - ORDER ID

 * binance
   Remark 以外はクォート無し。Remark はダブルクォート。
  - UTC_TIME: YYYY-MM-DD HH:MM:SS
  - Account: Spot
  - Operation: Deposit, Buy, Sell, Fee, Withdraw
  - Coin: トレード通貨のみ。一回の取引で通貨ペアの buy/sell 2つのレコードが作られるようだ。あと fee 一つ。
    一回の注文で複数のトレードに分かれることがあり、さらにその各トレード中のbuy,sell,fee の順序は不定のようだ。
    ただ、一回のトレードで fee,sell,buy は各一回、さらに fee,sell,buy が一回ずつ出てから次のトレード情報が来る。
  - Change: Coin の差分かな

 * poloniex
   クォートなし。
  - Date: YYYY-MM-DD HH:MM:SS
  - Market: 通貨1/通貨2
  - Category: Exchange
  - Type: Buy/Sell. たぶん 通貨1視点。
  - Price: 通貨1の通貨2単位での価格
  - Amount: 通貨1の数量
  - Total:  通貨2の数量
  - Fee: %付き数値
  - Order Number
  - Base Total Less Fee: total の数値を、buy なら負に、sell なら正のままにした値
  - Quote Total Less Fee: amount の数値を、buy なら正のまま、sell なら負にした値
  - Fee Currency: buy なら通貨1、sell なら通貨2. 取得した通貨かな。
  - Fee Total: total * fee のようだ。実際には fee currency が引かれる?

 * bitmex
  全フィールドダブルクォート付き。
  - transactTime: yyyy/m/d h:mm:ss  //ゼロパディング有り無し混じってる
  - symbol: 通貨1通貨2。区切り文字無しで通貨ペアを連結したもの。ADAH20 とかもあるな。20日先物か。
  - execType: Trade, Funding
  - side: Buy, Sell, 空文字
  - lastQty:
  - lastPx: 価格ぽい。buy/sell で単位変わらず。
  - execCost: 単位は satoshi? symbol であまり差異はなさそう。
  - commision: 少数第四位以下ばかり。
  - execComm: 執行手数料?
  - ordType: vLimit
  - orderQty
  - leavesQty:
  - price:
  - text: Trace だと "Submission from www.bitmex.com", Funding だと 'pjoFundingg"
  よく分からん

取引レコードを一個にまとめるか、binance 風に分割するかが一つ考えどころ。
データ構造的には分割した方がすっきりしそうだけど、取引処理ではワンセットで扱う場面あるだろうから一つの方が便利か。
統合するより分割する方が楽だしね。

あと、売買量には手数料は含めない。
都度の取引で損益に経費を含めるのではなく、
損益計算では手数料で引かれる前の価格で計算し、手数料は別にまとめて後で経費として利益から引く、という計算が会計的。

というわけで正規化は binance 方式にしておこう。
binance は取引IDが振られてないので振っておく。同じ取引データを入れた場合の重複排除は諦めるか。
どっかで残高がマイナスになって失敗するだろうから、手動で重複無くすようにインポートし直してもらおう。

