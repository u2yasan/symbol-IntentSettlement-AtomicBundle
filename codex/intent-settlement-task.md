# Codex実装指示書: IntentSettlement PoC

> 現在の段階（2026-10-26）: 仕様詳細化と雛形作成のみ。以下は将来、実装を依頼された段階の指示であり、今すぐclone・C++実装・ノード起動を行う指示ではない。先に[構成](../docs/repository-layout.md)、[判断一覧](../docs/decisions.md)、[受入表](../docs/acceptance-matrix.md)を読む。

この指示書を、共通資料と設計書を参照できるCodexの作業環境へ渡してください。以下は実装を依頼するための文章です。現在の成果物は設計であり、プラグインやテストが完成したことを意味しません。

---

## 依頼

Symbolの署名済み注文を1回だけ原子的に決済する、**実物のC++ Catapultプラグイン**を実装してください。対象baselineは`symbol/symbol`の`6c04695555230c89a6ffa2ac4d41774dcac77ae3`です。モデルコードだけで終了せず、対応genesisから起動した3ノードprivate-netで相互運用、非ゼロ手数料、取消、二重実行、rollbackを検証してください。

最初に、次の順で読んでください。

1. 作業repo内の適用対象`AGENTS.md`、build/test/developmentの実在する指示。
2. `docs/00-common-spec.md` と `codex/00-common-instructions.md`。
3. `docs/intent-settlement-design.md`。
4. `fixtures/README.md`、`fixtures/intent-order-v1.json`、`fixtures/generate_reference_vectors.py`。
5. 設計書の固定commitへの一次資料と、対応する既存unit/integration tests。

このキットをsource repoへコピーする場合は、相対参照を追える場所に配置してください。他PoCのAtomicBundleとは独立したbranch/worktreeまたは独立した設定で進め、競合するtype/cache割当を勝手に混在させないでください。

## 1. 最終成果物

- 新しい最上位`IntentSettlement`と`IntentCancel`のschema、C++モデル、TransactionPlugin、登録処理。
- 正規注文codec、maker条件署名、orderId生成、solver外側署名、取消を生成するCLI。
- stateless/stateful validatorsと既存のTransfer検証経路に従う資産移動。
- 永続化とMerkle root計算に対応したconsumption sub-cache、commit/undo。
- 基準fixtureに対するC++検証と独立ツールのcodec照合。
- 同じplugin・設定・genesisを使う3ノードの再現可能な統合環境。
- 正常・失敗・取消競争・reorg・再起動の試験証跡。
- 実際のbuild/実行コマンド、制限、未実装項目を記したREADMEと最終報告。

RESTの独自routeは必須ではありません。CLIと統合試験で必要な状態を確認できれば先に進めてください。未実装routeを既存機能のように文書化してはいけません。

## 2. 変更してはいけないv1の条件

メイカー1名、ソルバー1名、異なるliteral mosaic IDを2つ、正の整数数量、全量1回の決済です。maker/solverは異なる単一署名口座とし、実行時にmultisig口座になっていれば拒否します。recipientはmakerのaddressに固定します。namespace alias、部分約定、複数maker、注文報酬、公開秘密鍵P、独立したfunding/sweep、任意の通常取引の内包、Aggregateへのembeddingは実装しません。

決済時の資産移動は次の2本だけです。

```
maker -> solver: giveMosaicId / giveAmount
solver -> maker: getMosaicId  / getAmount
```

Settlementのfeeはsolverが外側取引で1回払います。Cancelの通常feeはmakerが払います。決済時のmakerのgetAmountをfeeや報酬の名目で減らさないでください。PoCでは両者に実行前の資産を要求し、solverはgetAmountに加えてouter.MaxFeeを事前に賄うものとします。口座別・mosaic別mapへ必要額を加算し、同一通貨の合算はoverflowを検査してください。このMaxFee事前残高要件はPoC独自の保守的な制約です。実際のfee引き落としは標準処理だけで行います。

共通仕様に従いprivate-netの`TotalVotingBalanceCalculationFix`を`Height(1)`へ設定します。設定表記と受理をM0で確認し、通常ブロックではcustom通知の後にfeeが引かれることをassertしてください。feeが先に引かれる古いpresetを使い、専用validatorで再びMaxFeeを要求する二重計上は不可です。

## 3. binaryと署名を厳密に固定する

canonical orderは設計書のoffset表どおり**136byte**です。

```
version:u8=1 | network:u8 | flags:u16LE=0 | reserved:u32LE=0
makerPublicKey:32 | recipientAddress:24
giveMosaicId:u64LE | giveAmount:u64LE
getMosaicId:u64LE  | getAmount:u64LE
validUntil:u64LE | nonce:32
```

署名・識別は以下を変更せず実装してください。

```
domainHash = SHA3_256(UTF8("SYMBOL_INTENT_ORDER_V1"))
message = domainHash || networkGenerationHashSeed || canonicalOrder
orderId = SHA3_256(message)
makerSignature = SymbolEd25519.Sign(makerPrivateKey, message)
```

messageは200byteです。NUL・改行・BOM、JSON、hex文字列、orderIdだけを署名してはいけません。Keccak-256へ置き換えないでください。orderIdにmakerSignatureを含めないでください。

baselineの`crypto::Sign` / `crypto::Verify`を使うか、その標準互換性をfixtureで証明してください。`SignatureNotification`を流用する場合、messageにseedが既にあるため`ReplayProtectionMode::Disabled`を指定します。Enabledによるseed二重prependを必ず拒否テストへ入れてください。

Settlementは標準128B header＋order136B＋maker署名64B＝**328B**。Cancelは標準128B header＋order136B＝**264B**。外側署名はそれぞれsolver/makerで、本文全体を署名対象にします。Cancelは外側署名者とorder.makerPublicKeyの一致を要求し、orderIdを再計算します。orderId単体だけで取消を認可しないでください。

最上位のみを許可し、`supportsEmbedding=false`、`embeddedCount=0`とします。新規type/facility/cacheの数値を推測で固定せず、M0で登録済み値・既存実験規約を調べ、私設用の衝突しない値をschemaと実装で共有してください。

## 4. 検証と通知の注意

外側標準の署名・deadline・fee検証を保持したまま、専用認可通知でmakerの条件署名、期限、未消費、口座、初期残高を検査してください。実行可能期限は厳密に次の式です。

```
BlockTime < validUntil <= BlockTime + 21_600_000
```

加算overflowを避け、上下関係検査後の差で比較してください。validUntilと同時刻でEXPIREDです。外側deadlineの標準規則とは別です。注文に作成時刻がないため、遠い将来の期限は最初ExpiryTooFarでも、時間が進むと受理可能になります。これを「署名から6時間」と表示しないでください。

以下の制限迂回を防いでください。

- multisig判定は「その口座のcosignatoryAddressesが空でないか」に相当する既存規則を確認します。単なる他口座のcosignerであるだけのエントリを理由に拒否しません。
- makerとsolver双方でTransfer型とIntentSettlement型のoutgoing操作許可を要求します。外側の標準TransactionNotificationはsolverにしか適用されないので、makerも専用validatorで確認します。
- 既存のAccountPublicKey/AccountAddress、AddressInteraction、BalanceTransfer通知を適切な順で発行し、住所制限、mosaic受取制限、global/address restriction、transferability、残高検査を通します。
- Balance cacheへ直接書き込んで既存制限を省かないでください。
- makerの操作制限検証のために偽のTransactionNotificationを発行してはいけません。HashCache observer等まで誤って発火します。
- Cancelは通常の外側認可と期限・未消費を要求し、対象資産の現在残高や存在を取消条件にしません。

2脚目または標準feeの処理が失敗した場合に、1脚目・公開鍵登録・consumption・receiptが残らないことを検証してください。単純な「前段で全部チェックしたから安全」という推測でundo試験を省略してはいけません。

## 5. 消費状態を合意状態にする

keyはorderId32B。valueはstatus1B＋reserved7B＋makerAddress24B＋validUntil8B＋consumedHeight8B＋outerTxHash32B＝**80B**。statusはFILLED/CANCELLEDだけを保存します。未登録はOPEN、期限切れは注文データとblockTimeからEXPIREDを導出します。保存済み終端状態は期限後も保持します。

新しいMerkle対応sub-cacheを登録し、cache serializer、patricia/root、永続化、commit/rollback、再起動を実装してください。ローカルJSON、メモリset、REST照会結果で置き換えないでください。PoCではレコードをpruneしません。両操作は同じcacheを使い、同block内の先行deltaを後行validatorが見られるようにします。

新cacheはstateHash構成に影響します。**nemgenにも同じプラグインを導入してfresh genesisを生成**し、3ノードの設定とcache構成を一致させてください。既存mainnetのgenesisやstate snapshotに後付けして成功扱いにしないでください。mainnet移行の実装は範囲外です。

## 6. 段階的に進める

### M0: ソースと実行環境の確認

baseline commit、適用AGENTS、build/test手順、pluginの登録例、既存cacheのserializerとundo、schema generator、nemgenを確認します。設計書に書かれた提案APIが実在すると仮定せず、実ソースの対応表を作ってください。隔離private-net用設定、chain seed、通貨mosaic、private type/cache割当を記録します。

### M1〜M3: codec、plugin、状態

固定fixtureを最初に通し、その後C++取引型、validators、既存transfer経路、cacheを実装します。新型だけを追加してmaker制限を飛ばす近道は不可です。コア変更が必要なら、理由・最小差分・検証範囲を分離してください。プラグインだけで済んだという見かけを優先しないでください。

### M4〜M5: 実ネットワークと分岐

3ノード全てを実物Catapultと新プラグインで起動します。非ゼロfeeで1件ずつ正当に決済・取消し、全ノードのblock hash、stateHash、receiptsHash、各口座残高、消費状態を比較します。その後、取消競争、重複、無効注文、非finalizedの分岐とrollback、再起動を試します。任意の深いfinalized rollbackを通常プロトコルとして許す変更はしないでください。

ローカル候補の失敗は外側1件をundoして除外します。一方、無効なSettlementが受信blockに入っている場合は**block全体を拒否**します。この2つを別試験にします。

### M6: 再現性と引渡し

設計書のIS-01〜IS-20を1行ずつ報告し、実行済み・失敗・未実行・環境blockを区別します。fixtureだけ通った状態をPoC完成と呼ばないでください。

## 7. 必須の試験と受入判定

少なくとも、署名field改変／wrong seed、expiry境界、alias拒否、maker/solver multisig、双方の操作制限、住所とmosaic制限、第2脚失敗、非ゼロfee、get/giveがXYMの両方向、同block内の二重消費、cancel/settleの両順、他者取消拒否、UT undo、無効受信block、reorg、再起動、genesis/root一致を実行してください。

各試験について、対象commit、実行コマンド、node/plugin設定、exit code、raw log、tx/block hash、前後残高、consumption record、root/hashの比較結果を保存します。syntheticなテスト鍵だけを使い、秘密鍵は成果物ログへ出さないでください。

最終報告では次を分けます。

- 実装済みの機能と実際に通ったC++ unit/integration tests。
- 3ノードで実行できたケースと再現手順。
- NOT RUN、失敗、環境依存、まだ証明していない性質。
- source差分と設計からの変更理由。
- mainnetには導入できない現時点の範囲。

受入は、**C++プラグイン＋3ノードの実行証跡＋失敗・rollback試験**が揃った時点です。ネットワークや依存関係で試験ができない場合も実装・静的確認・実行可能な試験を進め、残るblockを正確に示してください。未実行をPASSへ書き換えてはいけません。
