# 私設ネットワークと検証証跡の仕様

文書版0.2 / 設定・手順の案。**起動構成、鍵、genesis、runnerは未作成**。

## 分離

Intent / Atomicは別profile、別generation seed、別genesis、別data directoryで試験する。それぞれ独立したCatapultプロセス3つ以上を起動する。1台のホスト上でもプロセス・データ・peer接続を分離する。実port、image/build方法、鍵生成、起動コマンドはM0/M4で実環境に合わせる。

公開peer discovery・seedを取り込まず、peer allowlistを私設ノードに限定する。APIは必要なローカル範囲へbindする。実ウォレットをコピーしない。fork試験用ハーベスター鍵も使い捨てにする。

## manifestを埋める条件

[Intent雛形](../networks/private/intent-settlement/manifest.template.json)と[Atomic雛形](../networks/private/atomic-bundle/manifest.template.json)はJSONとして読める設計メモで、native設定ではない。`null`は未決、`DRAFT_NOT_RUN`は未起動を表す。自動的にnative設定へ変換するloaderは存在しない。

| 項目 | 確定時の内容 |
|---|---|
| ソース | upstream baseline、実装commit、差分digest、toolchain/dependency版 |
| network | ID、generation seed、epoch、currency ID、genesis hash、許可peer |
| plugin | 型・facility・notification/cache ID、plugin一覧、binary digest |
| fork | 三forkの実設定キー、設定値、実測通知順、V3受理結果 |
| ノード | node名、公開ID、peer/API endpoint、data directory、設定digest |
| 合意設定 | block時間、lifetime、fee、DeepCount上限、finalization・rollback範囲 |

activation=2と三fork=1、Atomic 4096B/2048B/2hは提案値。nativeキーの表記をこのJSONのfield名から推定しない。Intent新cacheはnemgenと全ノードに同じ構成で読み込ませる。Atomicには新しいMerkle cacheを追加しない。

## 将来の実行手順

1. baseline buildと既存Transfer/Aggregateの試験を保存する。
2. M0の未確認点を閉じ、案ごとのprofileとmanifestを確定する。
3. 同一plugin/configでfresh genesisを生成し、3ノードを起動する。
4. genesis、同じheightのblock/state/receipts hashを比較する。
5. activation境界、新型の正常系と拒否系、非ゼロfeeを検証する。Atomicは単独Aggregate V3成功を先に確認する。
6. UT候補undoと、故意に無効取引を含めた受信block拒否を別ケースとして実施する。
7. 同一親から有効な未finalized競合枝を作り、nativeの採用条件を満たして枝切替を観測する。
8. finalized blockの置換拒否、再起動、1ノードの再同期、二重実行拒否を確認する。
9. 各試験の証跡と実コマンドを保存して停止する。データ破棄は検証結果保存後、対象run directoryに限る。

これらは実行済み手順ではない。単にtimestampを書き換えた不正blockをfork成功と扱わない。nativeのVRF・hit・difficulty・scoreとfinalizationに従う。

## 証跡の単位

`artifacts/poc/<案>/<run-id>/<test-id>/`を将来の生成先とする。テンプレートをコピーしただけでは実行証跡にならない。

各caseで、設定/実装digest、コマンド、exit code、期待結果、実測結果、raw log、公開payload、tx/legacy hash、親・前後block hash、高さ、時刻、残高差分、consumption観測、state/receipts hash、finalization状態を記録する。wall-clock時刻は試験ログに使用できるが、合意判定の時刻として使わない。

秘密鍵を保存しない。公開済みfixture鍵以外の鍵はrun外の明示したローカル鍵保管領域で扱う。巨大ログ・DB・build出力は配布checksum対象から外す。証拠を共有する際は、サマリーと必要な公開入力を選別する。
