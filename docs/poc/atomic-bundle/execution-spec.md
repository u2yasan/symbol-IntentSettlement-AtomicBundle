# AtomicBundle実行契約

文書版0.2 / 設計段階。[基本設計](../../atomic-bundle-design.md)の限定adapterの責務を具体化する。native接続点・channel・undo順はQ-04で確認する。

## 認可表

| 主体 | 必要な認証 | 操作許可 |
|---|---|---|
| inventory | 外側主署名 | AtomicBundle、fundingのoutgoing Transfer |
| maker | legacy主署名 | AggregateComplete、give/tipのoutgoing Transfer |
| P | legacy連署＋outer連署 | get/sweepのoutgoing Transfer |

三者は異なる通常単一鍵口座。全五Transferで住所・mosaic制限、存続期間、transferability、残高等をnative同等に検査する。外側P連署が正しいだけでは、inventory資金の移動認可にならない。

## adapterの入力・出力

入力: 原本legacy bytes、外側のcontext、検証済み固定形の当事者、処理中のnative cache delta、source管理context。
出力: legacyの標準検証・通知列を同じdeltaへ接続する。原本bytes、主署名、連署、MaxFee、Deadlineを修正しない。

| 通知責務 | 保持する値・処理 | 禁止する省略・副作用 |
|---|---|---|
| AccountPublicKey / Entity | maker・native entity検証 | outer inventoryでmakerを代用 |
| Transaction | legacy hash・Deadline・maker・Aggregate型 | 子のHashCache検索／消費の省略 |
| Deadline | legacyのnative期限・最大寿命 | outer期限だけで代用 |
| Fee | 子のactual fee=0、signed MaxFee維持 | 子MaxFee仮徴収・子fee debit/receipt |
| maker signature | 原本に対するnative replay protection | custom publisherだけで済ませる |
| Aggregate固有 | TransactionsHash、内部3 Transfer、P連署 | 署名数・順序・型の緩和 |
| Source | primaryは外側のまま | childをtop-levelとして数える |

これは新設adapterへの要件表で、同名APIの存在を保証しない。Fee通知とfee debit observerの分離が基準APIでできない場合は、必要な最小コア変更を記録する。検証を削ってプラグイン内だけに収めない。

## 実行順と残高

give=(A,a)、get=(B,b)、currency=C、tip=t、実手数料=F。次はfee以外の適用順である。

| 順 | 操作 | 差分 |
|---:|---|---|
| 1 | funding | inventory:-bB、P:+bB |
| 2 | legacy give | maker:-aA、P:+aA |
| 3 | legacy get | P:-bB、maker:+bB |
| 4 | legacy tip | maker:-tC、P:+tC |
| 5 | sweep | P:-(aA+tC)、inventory:+(aA+tC) |
| 6 | outer fee | inventory:-FC、native分配 |

先に全体の正規形式・四署名・権限を確認し、その後native pipelineへ渡す。残高・制限は各操作時点のdeltaで評価する。Intentの「全支払＋MaxFeeを適用前に保持」という独自条件を持ち込まない。

例: Aが非currency、B=C、a=50、b=1000、t=10、F=3。makerはlegacy getで1000Cを受け取った後に10Cのtipを支払う。inventoryの取引差分はA:+50、C:-993、Pは全資産差分0となる。makerのtip事前保有を独自に必須化しない。一方、inventoryはfunding実行時点で1000C必要である。UTがMaxFeeを使う経路と実ブロックでFを使う経路は別に試験する。

A=Cの場合はgiveとtipを同じmosaicへchecked additionし、sweepに1要素だけを入れる。A≠Cなら2要素をID順で入れる。A=Bは禁止。P dustは初期値を保持し、既存残高をsweep額に加えない。適用中のP受取がoverflowする場合も全体を拒否する。

## sourceと注文消費

| 処理 | secondary | primary |
|---|---:|---|
| outer | 0 | 外側index |
| funding | 1 | 同じ |
| legacy container | 2 | 同じ |
| legacy give / get / tip | 3 / 4 / 5 | 同じ |
| sweep | 6 | 同じ |
| outerへ復帰 | 0 | 同じ |

成功だけでなく検証失敗・undo時にもsource contextを漏らさない。復帰の実装方式はnative通知機構に合わせる。C++のscope guardだけでreceiptのundoまで済むと仮定しない。

注文消費はlegacy Transaction通知から既存HashCacheへつなぐ。同一blockの先行deltaを後続へ見せ、通常→通常、通常→Bundle、Bundle→通常、Bundle→Bundleを同一・別blockで検証する。outerのhash/signature/deadlineを変えてもlegacy identityは変わらない。

## 失敗分類と後始末

| 論理ラベル（数値未割当） | 条件 | 試験 |
|---|---|---|
| InvalidFrame / ActionsRootMismatch | 長さ、順序、count、padding、root不正 | AB-01 |
| InvalidOuterAuthorization | inventory署名、outer P連署不正 | AB-02 |
| InvalidLegacyOrder | 原本認証、TransactionsHash、native期限・構造不正 | AB-03 |
| UnsupportedShape | Bonded、再帰、alias、message等 | AB-08 |
| ParticipantOrPermissionMismatch | 三者不一致／同一化、認可・制限違反 | AB-07 |
| InvalidFundingOrSweep | 固定数量・宛先違い、P dust消費 | AB-06 |
| DuplicateLegacyOrder | 共有HashCacheで消費済み | AB-09〜12 |
| NativeBalanceOrFeeFailure | 各脚残高、overflow、outer fee失敗 | AB-05/07/13 |

全ての失敗でこのBundle由来のfunding・legacy・sweep・消費・fee・receipt・公開鍵登録を残さない。候補では全undo、受信blockでは全block拒否。rollbackで子消費を戻してから新枝を再検証し、native保持規則とlegacy Deadlineに従って再起動・pruneの振る舞いを検証する。

専用cacheの追加や外側期限による早期削除で解決しない。P不変条件は差分式の確認に加え、give/get/currency/無関係資産のdustを与えた実試験で確認する。StateHash一致だけを子消費維持の証拠にはしない。
