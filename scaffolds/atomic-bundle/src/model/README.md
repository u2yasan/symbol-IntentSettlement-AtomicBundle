# containerと認可データ

状態: DESIGN_ONLY。ソースは未実装。

frame16B、8B alignment、kind/index、rootを定義。長さ検査後に領域を読む。outerとlegacyのhash・署名を混同しない。

予定ファイル（新設候補）:

- `AtomicBundleTransaction.h`
- `AtomicAction.h`
- `AtomicBundleNotifications.h`

受入試験: AB-01〜03/18。具体的な検査・期待結果はdocsの基本仕様、詳細仕様、受入表を参照する。

実装開始時にnative APIとtest fixtureの対応を記録し、成功するだけのstubや疑似署名を置かない。
