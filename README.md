# cfr_sample
Counterfactual Regret Minimaization (CFR)のサンプル実装

leduc pokerのナッシュ均衡解が探してもなかったのでCFRで計算するプログラムを作成してみた
実装にあたっては
* https://justinsermeno.com/posts/cfr/
のものを参考にした

## leduc pokerのルールについて

前提: limit holdemの知識はあるものとする。
デッキにはJ,Q,Kがそれぞれ2枚づつ存在する。
各プレイヤーはanteを$1支払う。pre-flopはSmall betが$2で2回のみレイズ可能、flopは1枚のみカードが落ちる。
flopラウンドではBig Betが$4で2回のみレイズ可能。
ハンドランクはpairが一番強く、他はキッカーで決める。
holdem同様、pre-flopはBTN=>BB, flopはBB=>BTNの順序で行う

## 解の一部について

ナッシュ均衡解が載ってない理由として、単純に場合が複雑だからということがわかった。
持ってるハンドとアクション、flopの場合で288通りのパターンに対する戦略が存在する。

### pre-flop戦略

以降 10/20/70と書いたときfold 10%, call/check 20%, bet/raise 70%と表す 
#### BTN

ハンドによるファーストアクション
* J : 0/81/19
* Q : 0/19/81
* K : 0/21/79

チェックして, betで回ってきた場合
* J : 93/5/11
* Q : 0/66/34
* K : 0/40/60

betして, raiseされた場合 (raiseは2回のみなのでcallのみ)
* J/Q/K : 0/100/0

#### BB
チェックできた場合
* J : 0/75/25
* Q : 0/19/81
* K : 0/0/100
betできた場合
* J : 84/8/8
* Q : 26/53/21
* K : 0/19/81
betしたら, raiseされた場合
* J/Q/K : 0/100/0

### flop戦略

いくつか抜粋

#### preflop check-checkの場合

この場合BBのレンジにはKはない (preflop checkに対して100% betするため)


##### Jが落ちた場合

基本はお互いnutsがないと打たないし、打たれたら降りる

BB
* J : 0/72/28
* Q : 0/100/0
BTN
* betできた場合
    * J : 0/0/100
    * Q/K: 100/0/0
* checkできた場合
    * J : 0/0/100
    * Q/K : 0/100/0 

##### Kが落ちた場合

BBはQのチョップでもBTNからほぼ打たれるので、Qはcheck-callよりにする。
BTNのJでbetは7%だが、pre-flopの戦略(J 81% check, Q/K 20% check)から向こうがJでbetしてる場合がそれなりにある。

BB
* J,Q : 0/100/0
BTN
* J : 0/93/7
* Q : 0/5/95
* K : 0/0/100
BB
* J : 100/0/0
* Q : 28/72/0

#### preflop bet-raise-callの場合

##### Kが落ちた場合

potにすでに$10入ってる状態。

BB
ほぼ全ての場合でbetする。
* J : 0/0/100
* Q : 0/8/92
* K : 0/1/99

BTN

betに対してもJである程度raiseして、Qを降ろしにいく
* betできた場合
    * J 68/0/32
    * Q 71/29/0
    * K 0/0/100
* checkできた場合
    * J 19/20/60
    * Q 0/84/16
    * K 0/0/100

BB
* betしてraiseされた場合
    * J,Q : fold
    * K : call
* checkしてbetされた場合
    * J : 33/33/33
    * Q : 36/64/0
    * K : raise