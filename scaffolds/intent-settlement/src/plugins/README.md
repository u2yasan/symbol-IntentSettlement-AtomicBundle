# 取引型登録と通知の構築

状態: DESIGN_ONLY。ソースは未実装。

入力はnative transaction/context、出力は認可・Transfer相当・消費通知。偽のTransaction通知でmaker制限を代用しない。型登録と取引publisherを分ける。

予定ファイル（新設候補）:

- `IntentSettlementPlugin.cpp`
- `IntentSettlementTransactionPlugin.cpp`
- `IntentCancelTransactionPlugin.cpp`

受入試験: IS-09/14/15/18。具体的な検査・期待結果はdocsの基本仕様、詳細仕様、受入表を参照する。

実装開始時にnative APIとtest fixtureの対応を記録し、成功するだけのstubや疑似署名を置かない。
