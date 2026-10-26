# Intent実行契約

文書版0.2 / 設計段階。[基本設計](../../intent-settlement-design.md)の処理責務を分解する。以下の論理段階をnative通知の実行順だと仮定しない。channelと標準署名・feeの位置はM0で対応表を作る。

## 入力と出力

入力は正規transaction bytes、固定network profile、処理中ブロックのheight/time、native cache delta、標準検証context。出力は成功／検証失敗とnative pipeline内の状態差分である。validatorが独自に永続化・HTTP照会・資産移動してはならない。

| 責務 | Settlement | Cancel | 状態変更 |
|---|---|---|---|
| format | 328B、order136B、literal ID、正数量、異資産 | 264B、同じorder構造 | なし |
| authorization | outer solver署名、maker条件署名、maker≠solver | outer maker署名、order maker一致 | なし |
| eligibility | 期限、両口座認可、両脚制限、適用前残高 | 期限、通常のCancel認可・fee | なし |
| consumption検査 | 未登録であること | 同左 | なし |
| 公開鍵・address登録 | 認可済み当事者 | native規則による | native cache delta |
| transfer通知 | give→getの固定2脚 | 発行しない | native残高delta |
| consumption通知 | FILLEDを挿入、挿入直前に再検査 | CANCELLEDを挿入 | 専用cache delta |
| 外側fee | solverから標準実額 | makerから標準実額 | 標準処理のみ |

Cancelにはgive資産の保有やmosaicの現在の存在を要求しない。orderの構造が正しいことと、現在その交換を実行できることは別である。Cancelにmaker条件署名を追加要求しない。

## 状態遷移

| 保存状態 | 入力 | 条件 | 成功後 |
|---|---|---|---|
| 未登録 | Settlement | 期限内・全条件成立 | FILLED |
| 未登録 | Cancel | 期限内・本人の取消・fee可 | CANCELLED |
| FILLED | Settlement / Cancel | 任意 | 拒否、変更なし |
| CANCELLED | Settlement / Cancel | 任意 | 拒否、変更なし |
| 未登録・期限切れ | Settlement / Cancel | `BlockTime >= validUntil` | 拒否、保存なし |
| FILLED / CANCELLED | 正当なrollback | orderId/status/height/outerHashが適用取引と一致 | 未登録へ復元 |

OPEN/EXPIREDは保存値ではない。注文bytesがあるときだけ未登録を時刻から解釈する。orderIdしかない照会ではUNKNOWN。FILLED/CANCELLEDは期限後も保持する。reorg後に未登録となっても、現ブロックの期限・残高・制限を再検査してから再約定する。

## 認可・残高の具体例

makerがAを50、solverがBを1000交換する場合、feeを除く期待差分はmaker=`A:-50,B:+1000`、solver=`A:+50,B:-1000`。fee Fはsolverのcurrencyから一度だけ引く。Bがcurrencyならsolverは適用前に`1000+MaxFee`を持つ必要があり、実引落額は`1000+F`。MaxFeeを全額実引落しない。

チェック対象はmaker/solverの自口座multisig状態、双方のTransferとSettlement outgoing許可、住所・mosaicの送受信制限、存続期間、transferabilityとowner例外。単なる他口座のcosigner登録は自口座のmultisig化ではない。

## 失敗分類

以下は文書上の論理ラベルであり、native failure codeはQ-11で割り当てる。外側署名・deadline・feeなど既存の失敗はnativeコードを保持する。

| ラベル | 発生条件 | 参照試験 |
|---|---|---|
| InvalidEncoding | size、予約領域、version、ID形式、数量不正 | IS-01/04 |
| InvalidOrderAuthorization | maker署名、recipient、seed不一致、他者Cancel | IS-02/03/13 |
| InvalidParticipants | maker=solver、認可されない口座状態 | IS-08 |
| Expired / ExpiryTooFar | 注文期限外 | IS-05 |
| AlreadyFilled / AlreadyCancelled | consumption既存 | IS-12/13 |
| RestrictedOperation | 操作・住所・mosaic制限 | IS-09〜11 |
| InsufficientInitialBalance / AmountOverflow | 事前必要額不足／合算不能 | IS-06/07 |

複数違反が同時にあるときの最初のコードはnative通知順の確定後に固定する。クライアントの事前検査結果と一致する前提を置かない。rollback整合性違反は通常の無効注文として無視せず、適用処理の異常としてnative経路で扱う。

## undoの観測対象

残高2脚だけでなく、公開鍵登録、order cache、Merkle root、fee、receipt、sourceを含める。失敗直前に実際にobserverが実行された証拠を残す。署名不正で最初から何も変更されなかった試験だけではundoを証明できない。

| 経路 | 必須動作 |
|---|---|
| UT／採掘候補 | この取引の変更を全てundoして候補から除外 |
| 受信block | block全体を拒否し、同blockの先行有効取引もcommitしない |
| 正当なreorg | 旧枝の状態・receiptを戻し、新枝を順番に再適用 |
| 再起動 | FILLED/CANCELLEDを復元し、再消費拒否を再確認 |

fault injectionはtest harnessだけ。公開鍵登録後、give適用後、consumption挿入後、outer fee前を個別に観測する。公開鍵・receiptの実際のundo方法とsource割当はQ-09/Q-10で確認する。
