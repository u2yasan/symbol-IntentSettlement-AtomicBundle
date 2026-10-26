# 限定legacy接続とsource管理

状態: DESIGN_ONLY。ソースは未実装。

原本legacy bytesを保持してnative共通認証・deadline・HashCacheとAggregate固有通知へ接続。actual child fee=0、primaryは外側、secondaryは2〜5。sourceをouterへ復帰する。

予定ファイル（新設候補）:

- `LegacyOrderAdapter.h`
- `LegacyOrderAdapter.cpp`
- `BundleSourceScope.h`

受入試験: AB-03/09〜13/17/18。具体的な検査・期待結果はdocsの基本仕様、詳細仕様、受入表を参照する。

実装開始時にnative APIとtest fixtureの対応を記録し、成功するだけのstubや疑似署名を置かない。
