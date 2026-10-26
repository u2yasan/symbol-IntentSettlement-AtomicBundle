# 正規order・Settlement・Cancelのschema

状態: DESIGN_ONLY。ソースは未実装。

order136B、Settlement328B、Cancel264Bの定義。入力はABI台帳、出力は将来のcatbuffer生成物。未割当EntityTypeを埋めて生成しない。

予定ファイル（新設候補）:

- `intent_order.cats`
- `intent_settlement.cats`
- `intent_cancel.cats`

受入試験: IS-01〜04。具体的な検査・期待結果はdocsの基本仕様、詳細仕様、受入表を参照する。

実装開始時にnative APIとtest fixtureの対応を記録し、成功するだけのstubや疑似署名を置かない。
