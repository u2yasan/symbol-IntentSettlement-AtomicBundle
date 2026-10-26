# native単体・pipeline試験

状態: DESIGN_ONLY。ソースは未実装。

入力は固定fixtureとnative cache context。codec、認可、状態、undoを層ごとに確認。fixture-onlyの成功を3ノード成功へ読み替えない。

予定ファイル（新設候補）:

- `model/IntentCodecTests.cpp`
- `validators/IntentValidationTests.cpp`
- `observers/IntentConsumptionObserverTests.cpp`
- `cache/IntentConsumptionCacheTests.cpp`
- `integration/IntentPipelineTests.cpp`

受入試験: IS-01〜20。具体的な検査・期待結果はdocsの基本仕様、詳細仕様、受入表を参照する。

実装開始時にnative APIとtest fixtureの対応を記録し、成功するだけのstubや疑似署名を置かない。
