# 受入試験と証跡の対応表

文書版0.2 / 2026-10-26。**native試験は全てNOT_RUN**。既存fixtureのPython検算は独立した補助確認であり、以下のC++／私設網試験のPASSではない。

基本仕様のIS-01〜20、AB-01〜18を保持する。1つのIDに複数経路・境界がある場合、ケースを分割し全て実行してからID全体をPASSにする。

- model: 正規bytes、署名、hash、サイズ。
- validators: 認可、期限、制限、残高。
- pipeline: 実native通知、cache delta、observer、undo、source。
- private-net: 三プロセスでの収録、拒否、分岐、再起動。

各行の証跡は[結果雛形](../artifacts/poc/result.template.json)と[シナリオ雛形](../tests/scenarios/README.md)で記録する。実行前のリンクを成功証拠として扱わない。

## intent-settlement

[基本設計](intent-settlement-design.md) / [実行仕様](poc/intent-settlement/execution-spec.md)

| ID | 試験 | 必須観測・期待結果 | 結果 |
|---|---|---|---|
| IS-01 | serializerの全offset、136/200/328/264B | 完全一致、余剰byte拒否 | NOT_RUN |
| IS-02 | fixtureをC++と独立ツールで署名・検証 | 同じmessage/orderId、標準C++で署名検証成功 | NOT_RUN |
| IS-03 | field改変、wrong seed/network、domain、二重seed | すべて拒否。署名にIDだけを使う実装も不一致 | NOT_RUN |
| IS-04 | flags/reserved、0 amount、同mosaic、alias | 拒否 | NOT_RUN |
| IS-05 | expiryの前1ms・同値・後1ms、6h境界 | 規定のstrict expiryとupper capに一致 | NOT_RUN |
| IS-06 | fee倍率非ゼロ、give/getそれぞれがXYM | maker数量は固定、solverだけ実fee1回 | NOT_RUN |
| IS-07 | maker/solver残高不足、MaxFee合算overflow | 全体拒否、全状態不変 | NOT_RUN |
| IS-08 | maker/solverの実行直前multisig化 | 両方拒否。単なる他口座cosigner登録と区別 | NOT_RUN |
| IS-09 | 両者のTransfer/Settlement操作制限 | どの拒否条件も迂回不可 | NOT_RUN |
| IS-10 | 住所制限、受取mosaic制限、mosaic global/address制限 | 通常Transferと同じ可否 | NOT_RUN |
| IS-11 | 存在しない／期限切れ／非transferable mosaic | 前2者は拒否。非transferableはownerが送受信者かによる例外を含め通常Transferと同じ可否 | NOT_RUN |
| IS-12 | 2ソルバーが同注文を同block／別blockで実行 | 1回のみ。外側hash違いで再実行不可 | NOT_RUN |
| IS-13 | cancel/settleの両順、再取消、他人のCancel | 包含順の先行だけ成立、他人は拒否 | NOT_RUN |
| IS-14 | 1脚目適用後の後段validator失敗 | C++ pipeline試験で1脚目observe後に失敗を注入し、UT undoで全資産・cache・receiptが元通り。integrationでも無効注文の前後不変を確認 | NOT_RUN |
| IS-15 | 不正Settlementを含む受信block | block全体拒否、先行正当txの状態もcommitしない | NOT_RUN |
| IS-16 | 非finalized blockのrollbackと別枝で再約定 | consumption削除・資産復元・再実行が一致 | NOT_RUN |
| IS-17 | FILLED/CANCELLED後に全ノード再起動 | 状態維持、再消費拒否、root一致 | NOT_RUN |
| IS-18 | fresh genesisと全nodeのstateHash構成 | 新cache含めroot構成・genesis一致 | NOT_RUN |
| IS-19 | プラグインなしの隔離ノードへ新型を渡す | 受理不可を確認。既存網互換と誤認しない | NOT_RUN |
| IS-20 | 取引取り出し・並べ替え・再包装 | 署名済み単独fundingとして再利用不能 | NOT_RUN |

## atomic-bundle

[基本設計](atomic-bundle-design.md) / [実行仕様](poc/atomic-bundle/execution-spec.md)

| ID | 試験 | 必須観測・期待結果 | 結果 |
|---|---|---|---|
| AB-01 | canonical codec / root vector | 三種類の長さ、padding、順序、count、root が一致。異常値は拒否 | NOT_RUN |
| AB-02 | outer 認証 | fee / deadline / recipient / amount / kind / root の一ビット改変を拒否。P 連署の欠損・流用・余分な連署も拒否 | NOT_RUN |
| AB-03 | legacy 完全検証 | maker 主署名、P 連署、TransactionsHash、型・version・network・deadline・size の破損を全て拒否 | NOT_RUN |
| AB-04 | 基本約定 | 三ノードで同じ Bundle を収録。maker / inventory の期待差分、P の差分ゼロ、同一 state / receipts / block hash | NOT_RUN |
| AB-05 | 非ゼロ fee | multiplier 0 と非ゼロの双方。outer 一回だけ課金、maker child fee 0、tip 全量、native 分配を含む総額一致 | NOT_RUN |
| AB-06 | P dust | give / get / currency / 無関係モザイクの dust を別々・同時に保持。sweep-all・増量を拒否 | NOT_RUN |
| AB-07 | 残高・制限失敗 | maker 不足、inventory 不足、restricted mosaic、口座送受信・操作制限、P のマルチシグ化を拒否し、全差分なし | NOT_RUN |
| AB-08 | 未対応形 | Bonded、再帰、alias、partial、メッセージ、管理型、複数注文、余分な embedded を拒否 | NOT_RUN |
| AB-09 | 通常→通常 | 既存ハッシュ保護を維持。同一・別ブロック、期限内の二重実行を拒否 | NOT_RUN |
| AB-10 | 通常→Bundle | 先に通常経路で消費した legacy 注文を Bundle へ入れても拒否 | NOT_RUN |
| AB-11 | Bundle→通常 | Bundle が消費した注文を単独 Aggregate として再利用できない | NOT_RUN |
| AB-12 | Bundle→Bundle | outer の signer / deadline / fee / hash が異なっても同じ注文を二重実行できない | NOT_RUN |
| AB-13 | 遅い段階の失敗 | test harness 限定で legacy 適用後・sweep 中・outer fee 前に failure を注入し、funding・消費・fee・receipt が残らない。署名不正は AB-02/03 で別に確認 | NOT_RUN |
| AB-14 | 旧方式の対照実験 | 旧 T1/T2/T3 方式だけで、有効な早い timestamp の競合ブロックに T1 を再収録できる条件を再現しログ化 | NOT_RUN |
| AB-15 | funding 抽出 | 新 funding payload を通常 Transfer として送信・直接収録しても在庫署名がなく拒否。元外側署名の流用も失敗 | NOT_RUN |
| AB-16 | fork / replay | 未 finalized の同一親から競合枝を作成。全 Bundle 再収録なら全額一緒、除外なら全額なし。再署名せず改変した Bundle は拒否 | NOT_RUN |
| AB-17 | rollback / restart / prune | 消費キーを旧枝で undo、新枝で再検証。未消費・期限内なら inventory と P が正しく再署名した別 wrapper は受理。restart 後も消費を保護し、outer expiry で子キーを早期削除しない | NOT_RUN |
| AB-18 | source / DeepCount / limits | secondary 1〜6 と復帰 0、DeepCount 7、cap 境界、native receipt hash を全ノードで一致 | NOT_RUN |

## 追加で分割する境界ケース

既存IDの受入条件を具体化する。新しい実装機能を追加するものではない。

| ID | 対応 | 前提と操作 | 必須結果 | 結果 |
|---|---|---|---|---|
| DX-01 | IS-05/13 | validUntilがBlockTime+6h+1msの注文をCancel | ExpiryTooFar、消費なし。6h境界で本人Cancelは他条件成立時に受理 | NOT_RUN |
| DX-02 | IS-06/07 | solver初期currency=getAmount+MaxFeeちょうど、actualFee≤MaxFee | 二重fee要求せず成立、1単位不足なら拒否。giveがcurrencyの逆方向も確認 | NOT_RUN |
| DX-03 | IS-13 | 構造が正しいorderだがgive残高0／対象mosaicが失効、本人Cancel | 通常feeと認可等を満たせば取消。Settlementは拒否 | NOT_RUN |
| DX-04 | IS-14/15 | 公開鍵登録後、give後、消費後、fee前の故障を別々に注入 | 残高だけでなく登録・消費・receiptも復元 | NOT_RUN |
| DX-05 | IS-17/18 | 異なる挿入順から同じ消費集合、再起動・再同期 | cache内容・rootが一致、FILLED/CANCELLEDの再消費拒否 | NOT_RUN |
| DX-06 | AB-05/07 | B=currency、maker初期currency=0、get受取後のtipで成立する数量 | native逐次残高で判定し、独自のtip事前保有gateを追加しない | NOT_RUN |
| DX-07 | AB-05/13 | inventoryがfunding全量を持ち、sweep後にだけfee資金を満たす | UT MaxFeeと実block actual feeの各結果を記録、二重課金なし | NOT_RUN |
| DX-08 | AB-06 | A=currencyでgive+tip合算、またはP受取残高overflow | 正常時はsweep1要素、overflow時は全体拒否、dust保持 | NOT_RUN |
| DX-09 | AB-09〜12 | 四方向replay×同一/別block×UT/受信block | 後行の重複拒否。無効受信blockは先行txもcommitしない | NOT_RUN |
| DX-10 | AB-13/18 | 子処理の失敗後、次の有効取引を候補適用 | sourceが漏れずprimary/secondaryとreceipt hashが一致 | NOT_RUN |
| DX-11 | AB-17 | outer期限切れ後、legacy期限内に別wrapper、さらに再起動 | 子消費済みなら拒否。正当なrollbackで未消費に戻った場合のみ再検証 | NOT_RUN |
| DX-12 | AB-01/18 | 宣言長overflow、上限前後、不足pad、余剰連署 | parse境界で拒否。有効固定形と両立しないサイズを成功入力にしない | NOT_RUN |
| DX-13 | 共通C-08 | 必要額加算、受取credit、size×multiplierの上限 | overflow/underflowを拒否、wrapやfloat丸めなし | NOT_RUN |
| DX-14 | 共通3章 | 新型activation直前/当日、native V3とfee fork設定 | 全ノード・nemgen設定一致。通知順の実測、未有効な新型は拒否 | NOT_RUN |
| DX-15 | CLI | JSON重複key、2^53超数量、wrong profile、送信timeout | 不正入力拒否、整数精度維持、timeoutはUNKNOWN、再署名しない | NOT_RUN |

## 仕様レビューの完了とPoC完成を分離する

今回の完了条件は、責務・配置・契約・未決事項・受入条件を読める形で揃え、ローカル参照と雛形データが整合すること。PoC完成条件は[共通仕様6章](00-common-spec.md)のC++・三ノード・rollback・再起動の実測証拠であり、今回まだ満たしていない。
