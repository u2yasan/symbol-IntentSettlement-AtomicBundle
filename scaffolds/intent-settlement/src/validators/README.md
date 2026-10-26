# 形式・認可・実行条件・消費の検査

状態: DESIGN_ONLY。ソースは未実装。

状態はnative contextから参照。残高やcacheを変更しない。Cancelで対象資産残高を要求しない。失敗はnative結果へ対応し、未知番号を仮定しない。

予定ファイル（新設候補）:

- `IntentFormatValidator.cpp`
- `IntentAuthorizationValidator.cpp`
- `IntentEligibilityValidator.cpp`
- `IntentConsumptionValidator.cpp`
- `Results.h`

受入試験: IS-03〜13。具体的な検査・期待結果はdocsの基本仕様、詳細仕様、受入表を参照する。

実装開始時にnative APIとtest fixtureの対応を記録し、成功するだけのstubや疑似署名を置かない。
