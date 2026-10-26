# ディレクトリ・ファイル構成

文書版: 0.2 / 2026-10-26 / 設計用雛形。wire versionは1のまま。

## この作業領域の役割

このフォルダは仕様・参照ベクトル・実装配置案を管理する。Symbol本体を含まず、単独でノードをビルドできない。2026-10-26の仕様整理開始時点ではGit未管理だった。同日の公開依頼によりGit管理を開始し、公開先を`u2yasan/symbol-IntentSettlement-AtomicBundle`とした。Symbol本体の取得、依存追加、ノード起動はまだ行っていない。

`scaffolds/`は責務と予定ファイルを記したREADMEによる雛形である。空のC++関数、架空のCMakeターゲット、動かない起動スクリプトは作らない。下記の「予定ファイル」は実装開始時に対象ソースの規約を確認して作成する。

```text
.
├── README.md                         # 現在の段階と読込順
├── CHECKSUMS.sha256                  # 配布ファイルの整合性。自身と実行生成物を除外
├── docs/
│   ├── 00-common-spec.md             # 両案共通の必須条件 C-01〜10
│   ├── intent-settlement-design.md   # Intent基本仕様 IS-01〜20
│   ├── atomic-bundle-design.md       # Atomic基本仕様 AB-01〜18
│   ├── repository-layout.md          # 本書。実在の雛形と予定ソースの対応
│   ├── client-contract.md            # オフラインCLI・入出力・送信境界
│   ├── private-network-spec.md       # 設定、genesis、fork、証跡の要件
│   ├── decisions.md                  # 未決事項、担当工程、完了条件
│   ├── acceptance-matrix.md          # 全38試験と追加境界試験。現状NOT_RUN
│   ├── adr/0001-design-only.md       # 今回の範囲と両案の分離
│   └── poc/
│       ├── intent-settlement/
│       │   ├── protocol-abi.md       # バイト配置・署名・未割当番号
│       │   └── execution-spec.md     # 検証、状態遷移、失敗、undo
│       └── atomic-bundle/
│           ├── protocol-abi.md
│           └── execution-spec.md
├── scaffolds/
│   ├── intent-settlement/
│   │   ├── README.md
│   │   ├── schemas/README.md
│   │   ├── src/{model,plugins,validators,observers,cache}/README.md
│   │   └── tests/README.md
│   └── atomic-bundle/
│       ├── README.md
│       ├── schemas/README.md
│       ├── src/{model,plugins,validators,adapters}/README.md
│       └── tests/README.md
├── clients/
│   ├── README.md
│   ├── intent-settlement/README.md
│   └── atomic-bundle/README.md
├── networks/private/
│   ├── README.md
│   ├── intent-settlement/manifest.template.json
│   └── atomic-bundle/manifest.template.json
├── tests/scenarios/README.md         # 試験の前提・操作・観測・後始末の雛形
├── artifacts/poc/
│   ├── README.md
│   └── result.template.json          # 未実行の証跡記録雛形
├── fixtures/                        # 既存の参照実装と固定JSON。内容は維持
├── diagrams/                        # 既存の概念図と編集用ソース
├── output/pdf/                      # 0.1時点のPDF。0.2詳細仕様は未収録
└── codex/                           # 将来、実装を依頼したときの作業指示
```

## Symbol実装先への対応案

全て**新設予定名**。基準commitの存在確認済みAPIという意味ではない。M0で既存CMake、schema生成器、テスト登録、永続化規約へ合わせる。

| ローカルの雛形 | 実装先候補 | 責務 |
|---|---|---|
| `scaffolds/intent-settlement/src/` | `client/catapult/plugins/txes/intent_settlement/src/` | 2取引型、認可、注文状態 |
| `scaffolds/atomic-bundle/src/` | `client/catapult/plugins/txes/atomic_bundle/src/` | Bundle、限定adapter、既存HashCache接続 |
| 各`schemas/` | `catbuffer/schemas/symbol/<案名>/` | wire定義と生成モデルの入力 |
| 各`tests/` | 対応pluginの`tests/`とnative integration suite | C++検証、undo、回帰 |
| `clients/<案名>/` | 各案の実装worktree内のツール配置 | 独立codecと最小CLI |
| `networks/private/<案名>/` | 各案専用の私設網構成 | genesis・3プロセス・設定固定 |

### IntentSettlementの予定ソース

```text
schemas/intent_order.cats
schemas/intent_settlement.cats
schemas/intent_cancel.cats
src/model/IntentOrder.h
src/model/IntentSettlementTransaction.h
src/model/IntentCancelTransaction.h
src/model/IntentNotifications.h
src/model/IntentConsumption.h
src/plugins/IntentSettlementPlugin.cpp
src/plugins/IntentSettlementTransactionPlugin.cpp
src/plugins/IntentCancelTransactionPlugin.cpp
src/validators/IntentFormatValidator.cpp
src/validators/IntentAuthorizationValidator.cpp
src/validators/IntentEligibilityValidator.cpp
src/validators/IntentConsumptionValidator.cpp
src/validators/Results.h
src/observers/IntentConsumptionObserver.cpp
src/cache/IntentConsumptionCache.h
src/cache/IntentConsumptionSerializer.cpp
src/cache/IntentConsumptionStorage.cpp
tests/model/IntentCodecTests.cpp
tests/validators/IntentValidationTests.cpp
tests/observers/IntentConsumptionObserverTests.cpp
tests/cache/IntentConsumptionCacheTests.cpp
tests/integration/IntentPipelineTests.cpp
```

### AtomicBundleの予定ソース

```text
schemas/atomic_bundle.cats
schemas/atomic_action.cats
src/model/AtomicBundleTransaction.h
src/model/AtomicAction.h
src/model/AtomicBundleNotifications.h
src/plugins/AtomicBundlePlugin.cpp
src/plugins/AtomicBundleTransactionPlugin.cpp
src/validators/AtomicBundleFormatValidator.cpp
src/validators/AtomicBundleAuthorizationValidator.cpp
src/validators/AtomicBundleShapeValidator.cpp
src/validators/AtomicBundlePermissionValidator.cpp
src/validators/Results.h
src/adapters/LegacyOrderAdapter.h
src/adapters/LegacyOrderAdapter.cpp
src/adapters/BundleSourceScope.h
tests/model/AtomicBundleCodecTests.cpp
tests/validators/AtomicBundleValidationTests.cpp
tests/adapters/LegacyOrderAdapterTests.cpp
tests/integration/AtomicBundlePipelineTests.cpp
```

Atomicに専用consumption cacheや残高を書き換える独自observerを作る予定はない。両案とも既存Transfer相当の検証と資産移動を利用する。必要なコア変更はM0で根拠を示し、別差分に分ける。schema、CMake、登録番号を未確認のまま生成してビルド可能と扱わない。

## 依存方向

`schema/model → validator・observer/cache → plugin登録`とする。CLIは合意状態を変更せず、正規バイト列を生成する。HTTP、鍵保管、壁時計、乱数を合意処理へ持ち込まない。validatorにはnative context、clientにはnetwork profile・signer・transportを明示して渡す。両案の共通取引エンジンや汎用再帰executorは作らない。

## 正本と変更規則

基本仕様の固定条件を詳細仕様で暗黙に変更しない。不一致は[判断一覧](decisions.md)へ記録し、双方を修正してから実装する。文書版0.2は説明の詳細化であり、wire version変更ではない。既存PDFは0.1の保存資料として残す。現在の仕様はMarkdownを読む。
