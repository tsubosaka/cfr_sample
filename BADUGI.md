
# Badugiの1局面についての近似CFR解

## シチュエーション

* OOPのプレイヤーがopen, BTNが3bet, 他は降りて、OOPが4bet, BTNがcall
* OOP pat, BTN 1 change
* OOP bet, BTN call
* OOP pat, BTN 1 change
* OOP : 何かしらのBadugi
* BTN : A23
* pot size: 11.5 bb
* bet size: 2bb
* チェンジラウンドは残り1回とする

Badugiをやってると比較的よくあるシチュエーションかと思われる。(チェンジラウンドを残り2回ではなく、
1回にしたのは2回だと計算が終わらなかったため)
こちらのシチュエーションを近似したゲームとしたゲームとして、以下のようなゲームを考える

* OOP : 4-Kまでの数字が初手のBadugiの確率に比例した割合で配られる
* IP : 4-Kがそれぞれ1枚ずつ, 残りは仮想的に14が39枚配られるとする
* 勝敗: 数が小さい方が勝利する。同じ数字の時はIPが台が良いのでIPが勝つとする

### 注意点

* ブロッカーについては一旦無視する
    * 本来途中のドローでK,Qを1,2回見ると相手のBadugiのレンジは強くなる
    * 逆にローカードを複数見ると相手のBadugiのレンジは弱くなるはず
* 相手はpatブラフはしない、および一度できてるpatは崩さないものとする

## 1st roundの戦略

### OOP

* 全ハンドでbet

### IP

* 4-Jはraise, Qは3% call、残り97%はraise, Kは20% call, 残り80%はraise
* badugiできなかった場合は96% call, 4% raise
* badugiができる確率は約20%, できない確率は80%なので、raiseした場合 value 86%, bluff 14%くらいの構成となっている

### OOP (bet->2bet)

* 4-7はraiseとcallの混合戦略
* 8-Qは100% call
* Kは18% fold, 79% call, 3% raise

### IP (bet->2bet->3bet)

* 4-Jはraise or call
* Qが100% call
* Kは90% call, 10%はraiseに回す
* badugiできてない場合は82% call, 18%はraise

### OOP (bet->2bet->3bet->4bet)

4bet capでやってるのでcall or fold
* 4-7はcall
* Kは31% fold, 69% call

## change roundの戦略

### betにcallした場合

4-Jはraiseしてるので、ここでの選択肢はない

* Qは100% pat
* Kは10% change
* badugiできてなかったら100% change

### betにraiseしてcallされた場合

* 4-Kは100% pat
* badugiできてなくても35%はpatする (snowing)、残り65%はchange

### betにraiseして3betされてcallした場合

* 4-Qは100% pat
* Kは48%change, badugiできてない場合は64%change

### betにraise,3betで4betしてcallされた場合

Qで4betはしないのでここでは考えなくて良い
* 4-Jは100% pat
* Kは15% change, badugiできてない場合は54% change

## 2nd roundの戦略

この後のchange roundはないとしている

### OOP 
