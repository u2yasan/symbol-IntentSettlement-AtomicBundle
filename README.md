# Symbol IntentSettlement / AtomicBundle PoC Design Kit

作成日: 2026-10-25（日本時間） / 更新日: 2026-10-26 / 文書版: 0.2（wire version 1）

Symbolの新しいトランザクション型を、C++ catapultのプラグインとして試作するための設計書とCodex作業指示書です。**この一式は設計・実装指示の成果物です。ノードプラグインの実装、コンパイル、私設ネットワークでの実行はまだ行っていません。**

## 現在の段階: 仕様詳細化・雛形作成

詳細実装はまだ開始しません。`scaffolds/`に責務・予定ソースファイルを記したディレクトリ雛形を配置し、`clients/`、`networks/private/`、`tests/scenarios/`、`artifacts/poc/`に契約や記録テンプレートを用意しています。C++、CMake、SDK、ノード起動の実装はありません。

最初に[ディレクトリ・ファイル構成](docs/repository-layout.md)を読み、次に各案の基本設計と詳細仕様を参照してください。

| 詳細資料 | 内容 |
|---|---|
| [Intent ABI](docs/poc/intent-settlement/protocol-abi.md) / [実行仕様](docs/poc/intent-settlement/execution-spec.md) | wire・署名・状態遷移・検証・undo |
| [Atomic ABI](docs/poc/atomic-bundle/protocol-abi.md) / [実行仕様](docs/poc/atomic-bundle/execution-spec.md) | frame・四署名・adapter・共有消費・fee・source |
| [CLI入出力契約](docs/client-contract.md) | 公開ファイル・鍵入力・buildと送信・状態表示 |
| [私設網仕様](docs/private-network-spec.md) | manifest・genesis・三ノード・証跡 |
| [受入試験表](docs/acceptance-matrix.md) | IS 20件、AB 18件、追加境界15件。native試験は全て未実行 |
| [判断・未決事項](docs/decisions.md) | 型番号、native API、署名照合、SDK、設定などの確認条件 |

型番号などの未決値を仮の数値で埋めていません。JSON内の`null`は未決です。既存の参照ベクトルは保持し、PDFは文書版0.1の保存資料として残しています。0.2の正本はMarkdownです。

## まず読むもの

| 目的 | ファイル |
| --- | --- |
| 2案の境界、共通ルール、根拠 | [共通仕様](docs/00-common-spec.md) |
| Pを使わない専用交換を実装 | [IntentSettlement設計](docs/intent-settlement-design.md) |
| 署名済みAggregateを含む限定チャンクを実装 | [AtomicBundle設計](docs/atomic-bundle-design.md) |
| Codexでの共通作業ルール | [共通指示書](codex/00-common-instructions.md) |
| IntentSettlementの実装タスク | [IntentSettlement指示書](codex/intent-settlement-task.md) |
| AtomicBundleの実装タスク | [AtomicBundle指示書](codex/atomic-bundle-task.md) |
| 署名・バイト列の検算 | [参照ベクトル](fixtures/README.md) |
| IntentSettlementをPDFで通読 | [設計・共通仕様・実装指示の統合PDF](output/pdf/intent-settlement-poc.pdf) |
| AtomicBundleをPDFで通読 | [設計・共通仕様・実装指示の統合PDF](output/pdf/atomic-bundle-poc.pdf) |

図の編集用ソースは `diagrams/*.mmd`、完成した図は `diagrams/*.svg` と `diagrams/*.png` にあります。各PDFには、文書版0.1時点の共通仕様・設計書・Codex指示書を収録しています。今回追加した詳細仕様は未収録です。機械的な仕様比較・実装時の正本はMarkdownです。

## 2案の役割

| | IntentSettlement v1 | AtomicBundle v1 |
| --- | --- | --- |
| 主目的 | 事前署名された交換条件を1取引で決済 | 既存の署名済み交換Aggregateと前後操作を一体化 |
| メイカーの署名 | 専用の条件データ | 既存AggregateComplete V3 |
| ソルバーの署名 | 完成したSettlement全体 | 完成したBundle全体 |
| 公開鍵P | 不要 | 使用。外側のP連署も別途必須 |
| 在庫投入の切り出し | 独立した投入取引を作らない | 投入は内部操作で、単独Transfer署名を作らない |
| 注文状態 | 新しいFILLED/CANCELLED状態を管理 | 元AggregateのHashCacheを通常経路と共有 |
| ネットワーク手数料 | 外側ソルバーが1回支払う | 外側在庫アカウントが1回支払う |
| v1の範囲 | 1注文、2資産、固定額、全量約定 | 投入、限定Legacy注文、回収の3操作固定 |
| 推奨する開始順 | 先に着手 | Intentと別ブランチで比較検証 |

## 将来、実装を開始する手順

以下の入力例と`codex/`配下の実装指示は、ユーザーが実装を依頼した段階で使用します。今回の仕様詳細化から自動的に実装へ進む指示ではありません。

1. このフォルダを、Codexが読める作業領域へ展開します。Symbolリポジトリそのものは含まれていません。
2. 実装先の `symbol/symbol` リポジトリをCodexへ開かせます。既存の作業内容を保持したまま、各案を別の作業ツリー／ブランチで進めさせます。
3. 下記のいずれかをCodexに渡します。両案を同じ作業ツリーで同時編集しないでください。

### IntentSettlementを開始する入力

```text
添付または展開した symbol-poc-design-kit を仕様として、IntentSettlement v1のPoCを実装してください。
最初に README.md、docs/00-common-spec.md、codex/00-common-instructions.md、
docs/intent-settlement-design.md、codex/intent-settlement-task.md を読んでください。
実装先リポジトリのAGENTS.mdとビルド手順を確認し、独立した作業ツリーでM0から着手してください。
計画の提示だけで終了せず、実装・対象テスト・隔離した私設ネットワーク検証まで進めてください。
実行できない検証は未実施として記録し、モックや設計だけをPoC完成と報告しないでください。
```

### AtomicBundleを開始する入力

```text
添付または展開した symbol-poc-design-kit を仕様として、AtomicBundle v1のPoCを実装してください。
最初に README.md、docs/00-common-spec.md、codex/00-common-instructions.md、
docs/atomic-bundle-design.md、codex/atomic-bundle-task.md を読んでください。
実装先リポジトリのAGENTS.mdとビルド手順を確認し、IntentSettlementとは別の作業ツリーでM0から着手してください。
資金投入を通常の署名済みTransferにする代替実装は禁止です。
Legacy Aggregateの単独実行とBundle内実行をまたぐ二重約定防止、外側P連署、巻き戻しを検証してください。
実行できない検証は未実施として記録し、モックや設計だけをPoC完成と報告しないでください。
```

## 成果物の読み方

- **MUST / 必須:** v1の受け入れ条件です。勝手に緩和しないでください。
- **提案した名前・配置:** リポジトリで未実装です。M0で既存API・命名規則を確認し、実装名を決定してください。
- **参照ベクトル:** この文書のバイナリ規則を確認するためのデータです。catapultの相互運用成功を意味しません。
- **検証結果:** 本キットの作成時点では文書・参照ベクトル・PDFの検算のみです。C++実装のテスト結果を含みません。

両PoCは新しい合意ルールを持つ**隔離した私設チェーン**を対象とします。現行Symbolメインネットへの導入、公開ネットワークとのブリッジ、利用者資金の取り扱いはこの作業に含みません。

## ローカル資料の確認

```bash
shasum -a 256 -c CHECKSUMS.sha256
python3 fixtures/generate_reference_vectors.py --check
```

後者はPython 3.10以上と`cryptography`が必要です。fixture一致はnative実装や私設網での実行成功を意味しません。`CHECKSUMS.sha256`は配布資料の内容整合性を確認する一覧で、署名付きの真正性証明ではありません。実行時に生成するDB・鍵・ログは対象外です。
