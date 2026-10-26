# 形式・四署名・固定形・権限

状態: DESIGN_ONLY。ソースは未実装。

三者の一致関係、Transfer五本の許可、dustを含めた固定sweep額を検査。専用のIntent型事前MaxFee gateを追加しない。

予定ファイル（新設候補）:

- `AtomicBundleFormatValidator.cpp`
- `AtomicBundleAuthorizationValidator.cpp`
- `AtomicBundleShapeValidator.cpp`
- `AtomicBundlePermissionValidator.cpp`
- `Results.h`

受入試験: AB-01〜08。具体的な検査・期待結果はdocsの基本仕様、詳細仕様、受入表を参照する。

実装開始時にnative APIとtest fixtureの対応を記録し、成功するだけのstubや疑似署名を置かない。
