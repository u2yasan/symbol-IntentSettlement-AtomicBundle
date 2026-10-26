# Bundle・frame schema

状態: DESIGN_ONLY。ソースは未実装。

入力はABI台帳。外側48B固定body、可変stream、P連署104Bを区別する。native embedded payloadをopaqueなまま実行しない。

予定ファイル（新設候補）:

- `atomic_bundle.cats`
- `atomic_action.cats`

受入試験: AB-01〜03。具体的な検査・期待結果はdocsの基本仕様、詳細仕様、受入表を参照する。

実装開始時にnative APIとtest fixtureの対応を記録し、成功するだけのstubや疑似署名を置かない。
