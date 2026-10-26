# consumptionのCommit/Rollback

状態: DESIGN_ONLY。ソースは未実装。

入力は認可済み消費通知。未登録から終端recordを挿入し、Rollbackでは作成取引との一致を確認して除去。残高は既存observerへ任せる。

予定ファイル（新設候補）:

- `IntentConsumptionObserver.cpp`

受入試験: IS-12〜17。具体的な検査・期待結果はdocsの基本仕様、詳細仕様、受入表を参照する。

実装開始時にnative APIとtest fixtureの対応を記録し、成功するだけのstubや疑似署名を置かない。
