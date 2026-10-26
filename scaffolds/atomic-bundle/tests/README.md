# native単体・adapter・pipeline試験

状態: DESIGN_ONLY。ソースは未実装。

形式・認証と、部分適用後のundoを別々に検証。通常/Bundleのreplay四方向、source trace、fee分配、再起動後の拒否を記録する。

予定ファイル（新設候補）:

- `model/AtomicBundleCodecTests.cpp`
- `validators/AtomicBundleValidationTests.cpp`
- `adapters/LegacyOrderAdapterTests.cpp`
- `integration/AtomicBundlePipelineTests.cpp`

受入試験: AB-01〜18。具体的な検査・期待結果はdocsの基本仕様、詳細仕様、受入表を参照する。

実装開始時にnative APIとtest fixtureの対応を記録し、成功するだけのstubや疑似署名を置かない。
