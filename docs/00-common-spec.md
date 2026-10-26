# 両PoCの共通仕様と検証条件

文書版: 0.2 / 2026-10-26 / ステータス: 実装前のPoC仕様

## 1. 対象と結論

IntentSettlementは、メイカーの条件署名とソルバーの決済署名を検証する交換専用取引を追加します。AtomicBundleは、限定された既存署名済みAggregateと、その前後の内部操作を一体で実行する取引を追加します。

共通する目標は、**ハーベスターの善意や取引の並べ方に依存せず、支払認可と資産移動の不可分性を検証規則で強制すること**です。外側の箱を作るだけでは、独立に有効な通常Transferの署名を失効させられません。

2案は独立した比較対象です。IntentのコードをAtomicへ自動的に取り込まず、共通化は両方の最小仕様が安定してから別変更で行います。

## 2. 固定した一次資料

| 資料 | 確認対象 |
| --- | --- |
| symbol/symbol | `6c04695555230c89a6ffa2ac4d41774dcac77ae3` |
| heikaの元の交換例 | `891a2cb17a0d52c85ed85594d8283c844481a6cb` |
| 公式プラグイン説明 | https://docs.symbol.dev/concepts/plugin.html |
| 公式Aggregate説明 | https://docs.symbol.dev/concepts/aggregate-transaction.html |

以下のAPI名は固定コミットで確認した実在の拡張点です。新しい取引型名・通知名・キャッシュ名は各設計書の提案であり、既存APIではありません。

- [PluginManager](https://github.com/symbol/symbol/blob/6c04695555230c89a6ffa2ac4d41774dcac77ae3/client/catapult/src/catapult/plugins/PluginManager.h): 取引型、validator、observer、cacheの登録。
- [TransactionPlugin](https://github.com/symbol/symbol/blob/6c04695555230c89a6ffa2ac4d41774dcac77ae3/client/catapult/src/catapult/model/TransactionPlugin.h): 署名対象、追加Merkleデータ、embedded件数、top-level可否。
- [AggregateTransactionPlugin](https://github.com/symbol/symbol/blob/6c04695555230c89a6ffa2ac4d41774dcac77ae3/client/catapult/plugins/txes/aggregate/src/plugins/AggregateTransactionPlugin.cpp): Aggregateはembedded不可。子の固有通知と共通の取引処理は別。
- [NotificationPublisher](https://github.com/symbol/symbol/blob/6c04695555230c89a6ffa2ac4d41774dcac77ae3/client/catapult/src/catapult/model/NotificationPublisher.cpp): 期限、手数料、通常署名、取引ハッシュ通知の共通経路。
- [HarvestingUtFacadeFactory](https://github.com/symbol/symbol/blob/6c04695555230c89a6ffa2ac4d41774dcac77ae3/client/catapult/extensions/harvesting/src/HarvestingUtFacadeFactory.cpp): 候補取引への適用と失敗時undo。
- [UniqueTransactionHashValidator](https://github.com/symbol/symbol/blob/6c04695555230c89a6ffa2ac4d41774dcac77ae3/client/catapult/plugins/services/hashcache/src/validators/UniqueTransactionHashValidator.cpp) と [TransactionHashObserver](https://github.com/symbol/symbol/blob/6c04695555230c89a6ffa2ac4d41774dcac77ae3/client/catapult/plugins/services/hashcache/src/observers/TransactionHashObserver.cpp): 既存取引ハッシュの重複防止とrollback。
- [CatapultCache](https://github.com/symbol/symbol/blob/6c04695555230c89a6ffa2ac4d41774dcac77ae3/client/catapult/src/catapult/cache/CatapultCache.cpp): サブキャッシュrootから全体StateHashを計算。

## 3. ネットワーク境界

### 3.1 私設ネットワークのみ

公式C++ catapultを対象とし、同一バイナリ・同一設定の独立した3プロセス以上で検証します。RESTだけのモデルやメモリ上の独自台帳は補助資料です。プラグインのロード、ブロック受け入れ、状態更新、別プロセスへの伝播を確認して初めてネットワーク試験が成立します。

公開mainnet/testnetのseedノードを接続先に使いません。鍵と資金は使い捨ての私設ネットワーク専用とし、既存ウォレットの秘密鍵を入力しません。ネットワーク識別子だけで環境を区別せず、私設チェーン固有のgeneration hash seedで署名を分離します。

### 3.2 新しい状態rootとgenesis

新しいMerkle対応サブキャッシュは、空であってもStateHashの構成に影響し得ます。Intentの新キャッシュを、既存チェーンのスナップショットへ単に後付けしてはいけません。nemgen側と全検証ノード側が同じプラグインとキャッシュ構成を持つ、fresh private genesisを作ります。

PoCの検証有効化高さは `2` を初期案とします。これは全ノードが初めから新プラグインを持つ私設ネットワーク内の境界試験です。既存メインネットへの安全な状態移行や、旧ノードと共存できることを実証する設定ではありません。

旧バイナリへの負試験は、新しい取引型のデコード／検証拒否を確認します。IntentではgenesisのStateHash構成も異なり得るため、旧バイナリが新チェーンの最初のブロックから追従できることを前提にしません。

### 外側feeの通知順を固定する

基準ソースの `NotificationPublisher` は、fork設定によりCustom通知より前にfeeを引く場合と、後に引く場合があります。PoCでは取引型の有効化高さ2以降を**Custom処理 → 外側fee debit**へ固定します。`ForkHeights.TotalVotingBalanceCalculationFix` の私設値を `Height(1)` とする構成を初期案とし、実際の設定キー表記・受理・通知順をM0で確認してください。

古いpresetの大きなfork高さをそのまま流用すると、プラグインが初期残高として「支払額 + MaxFee」を検査する前にfeeが減り、二重にfee資金を要求する不整合が生じます。最大手数料とちょうど同額のfee資金を持つ境界ケースを必須試験にして、この順序を確認します。mainnetのfork設定を変更する指示ではありません。

### 既存Aggregate V3の有効化も揃える

AtomicBundle v1はLegacy AggregateComplete V3を検証します。新しいAtomicBundleだけを高さ2で有効化しても、既存Aggregateのversion validatorがV3を拒否する設定では動きません。私設ネットでは `ForkHeights.StrictAggregateTransactionHash` と `ForkHeights.UniqueAggregateTransactionHash` も `Height(1)` を初期案として設定し、ネイティブの単独V3とBundle内V3の両経路がテスト開始時から同じ版・hash規則を使うことを確認します。キー表記・genesis生成との整合・境界の受理はM0の必須確認です。既存mainnetのfork履歴を変更する意図はありません。

### 3.3 型番号とABI

取引型の数値、FacilityCode、キャッシュ登録番号をこの文書で既存番号へ仮割当しません。CodexはM0で対象コミットのenum・登録処理・予約値を確認し、衝突のないPoC専用値を `protocol-abi.md` に記録します。クライアント、catbuffer、ノードは同じ定義を参照します。

## 4. 共通の安全性条件

| ID | 必須条件 |
| --- | --- |
| C-01 | 認可されていない第三者の残高を減らさない。outer署名で認可される口座と、条件署名で認可される口座を区別する。 |
| C-02 | 交換の片側、資金投入だけ、注文消費だけを確定させない。 |
| C-03 | 同じ注文を同一ブロック・後続ブロック・別の包み方から二重実行できない。 |
| C-04 | reorg時は残高、注文消費、必要なreceiptとcacheを一貫して元へ戻す。 |
| C-05 | ネットワーク、取引型、版、金額、宛先、期限、手数料条件を署名対象と整合させる。 |
| C-06 | マルチシグ、アカウント制限、モザイク制限・存続期間などを迂回しない。v1で非対応の状態は明示的に拒否する。 |
| C-07 | 型付き・長さ付き・順序付きの正規バイト列を使う。JSON文字列表現を署名しない。 |
| C-08 | 全整数計算に上限とoverflow検査を置く。金額にfloatを使わない。 |
| C-09 | 外側の実サイズに基づくネットワーク手数料を1回課金し、ブロックの手数料分配・集計と一致させる。 |
| C-10 | 同じ入力・前状態から全ノードが同じ状態とreceiptを生成する。外部HTTP・壁時計・乱数を合意処理で参照しない。 |

## 5. 原子性の意味

候補ブロックを作る側では、無効な新取引の一時的変更をundoし、候補から除ける必要があります。受信側では、無効な新取引を含むブロック全体を拒否します。受信した署名済みブロックから不正な部分だけを削除して採用する設計ではありません。

署名・形式検査、状態検査、資産移動、注文消費の通知順序を明示し、途中失敗を挿入して最終状態が変化しないことを試験します。observerのCommitとRollbackだけでなく、未承認候補のundoも対象です。

## 6. PoCの完成条件

完成には次の証拠が必要です。

1. 対象コミットと変更差分、ビルド環境、再現用コマンドを記録する。
2. ネイティブのC++プラグインがビルド・ロードできる。
3. 独立したクライアント側codecとC++側codecの固定ベクトルが一致する。
4. 各設計書の必須テストが実行され、出力と結果が保存されている。
5. 3ノードで正常取引を受け入れ、同一高さのblock hash・StateHash・ReceiptsHashが一致する。
6. 未ファイナライズの競合枝への実際の切り替えを起こし、巻き戻し・再適用後の残高と注文状態が一致する。
7. 1ノードを再起動／再同期しても、その状態と重複防止が維持される。
8. 未実施、失敗、実装済みのみ、実行成功を区別した最終報告がある。

PoC完成は、mainnetへの採用可能性や資産保管サービスとしての安全性を保証するものではありません。公開ネットワーク導入には状態移行、費用・DoS、独立レビュー、クライアント互換性など別の設計判断が必要です。

## 7. 実装範囲の優先順位

最初は各案の限定仕様を満たします。任意の再帰、部分約定、価格オラクル、AMM、ブリッジ、外部資産、一般公開UIは含めません。ネットワーク処理と独立したCLIで十分です。REST/Mongo/ウォレットの本格対応は、合意処理のPoCが通った後に進めます。

C++だけに閉じたバイト列の自己検証ではクライアント相互運用を確認できません。一方、単純な参照モデルだけではコンセンサスを確認できません。両者の役割を分けて証拠を残します。

## 8. 詳細仕様と現在の作業段階

現在は仕様詳細化・雛形作成段階であり、M0の実装先ソース確認やnative実装はまだ開始していない。登録番号やSDKを仮定して埋めず、未確認として記録する。

- [構成と予定ファイル](repository-layout.md)
- [Intent ABI](poc/intent-settlement/protocol-abi.md) / [実行契約](poc/intent-settlement/execution-spec.md)
- [Atomic ABI](poc/atomic-bundle/protocol-abi.md) / [実行契約](poc/atomic-bundle/execution-spec.md)
- [CLI入出力](client-contract.md) / [私設網と証跡](private-network-spec.md)
- [未決事項](decisions.md) / [受入表](acceptance-matrix.md)

文書版0.2はwire変更ではない。基本仕様と詳細仕様の不一致は判断一覧へ記録して解決し、実装で黙って補正しない。PDFは0.1時点の保存版であり、現在の仕様の正本はMarkdownである。
