# wire model・通知・消費record

状態: DESIGN_ONLY。ソースは未実装。

入力は正規bytes。明示的な長さとLEで解釈し、暗黙paddingに依存しない。通知は非所有bufferの寿命をnative publisher実行期間に合わせ、外部I/Oを含めない。

予定ファイル（新設候補）:

- `IntentOrder.h`
- `IntentSettlementTransaction.h`
- `IntentCancelTransaction.h`
- `IntentNotifications.h`
- `IntentConsumption.h`

受入試験: IS-01〜04。具体的な検査・期待結果はdocsの基本仕様、詳細仕様、受入表を参照する。

実装開始時にnative APIとtest fixtureの対応を記録し、成功するだけのstubや疑似署名を置かない。
