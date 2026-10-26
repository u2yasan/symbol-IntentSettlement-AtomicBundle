# 登録・三操作publish・計数

状態: DESIGN_ONLY。ソースは未実装。

入力はouterとnative context。三操作を固定順に同じdeltaへ接続し、embeddedCount=6、DeepCount=7とする。通常Aggregateのembeddingを一般的に許可しない。

予定ファイル（新設候補）:

- `AtomicBundlePlugin.cpp`
- `AtomicBundleTransactionPlugin.cpp`

受入試験: AB-04/05/13/18。具体的な検査・期待結果はdocsの基本仕様、詳細仕様、受入表を参照する。

実装開始時にnative APIとtest fixtureの対応を記録し、成功するだけのstubや疑似署名を置かない。
