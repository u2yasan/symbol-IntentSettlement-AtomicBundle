# 実行証跡の保存先

現時点で実行証跡はない。`result.template.json`はNOT_RUNの記録雛形である。

将来の配置は`<案>/<run-id>/<test-id>/`。[私設網仕様](../../docs/private-network-spec.md)に従う。

PASSは対象層の実コマンド・期待値・実測・exit code・証跡参照が揃った場合だけ。NOT_RUNのreasonには未実装、環境不足、依存する設計未決等を区別して書く。failureの期待された拒否はnative試験のassertionが成功した場合に限りPASSとする。

秘密鍵、DB、大量raw logsを無差別に配布しない。選別前のrun出力はignore対象。共有する小さい証跡は確認して明示的に追加する。
