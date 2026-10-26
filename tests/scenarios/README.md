# シナリオ記述の雛形

[受入表](../../docs/acceptance-matrix.md)の各IDについて、実装段階で以下を埋める。現状runnerはない。

```text
ID / scheme / purpose:
層: codec / C++ unit / native pipeline / 3-node
前提: source/config/fixture digest、親block、height/time、当事者状態
入力: 公開payload、署名、期限、MaxFee、重複取引の順
操作: 実際のコマンドと送信順、故障注入点（test harnessのみ）
期待: 受理/拒否単位、前後残高、消費状態、fee、receipt/source
実測: tx/block/state/receipts hash、全nodeの同一height比較
後始末: node停止、run固有データの処理、証跡保存
結果: PASS / FAIL / NOT_RUN、未実施理由、artifactへの参照
```

成功するstub、空のテスト関数、モック台帳は置かない。署名の前段拒否と途中適用後undo、UT拒否と受信block拒否を別ケースにする。再起動前後の同一入力拒否も観測する。
