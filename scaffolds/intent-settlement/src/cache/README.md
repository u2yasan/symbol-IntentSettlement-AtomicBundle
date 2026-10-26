# 80B valueの保存・Merkle・再読込

状態: DESIGN_ONLY。ソースは未実装。

orderId32Bをkeyに80B valueを保存。pruneなし。空root、挿入順に依存しないroot、nemgenとnode共通登録が必要。storage APIはM0で確認する。

予定ファイル（新設候補）:

- `IntentConsumptionCache.h`
- `IntentConsumptionSerializer.cpp`
- `IntentConsumptionStorage.cpp`

受入試験: IS-16〜18。具体的な検査・期待結果はdocsの基本仕様、詳細仕様、受入表を参照する。

実装開始時にnative APIとtest fixtureの対応を記録し、成功するだけのstubや疑似署名を置かない。
