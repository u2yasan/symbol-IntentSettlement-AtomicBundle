# 私設網構成の雛形

[私設網仕様](../../docs/private-network-spec.md)に対応する設計メモ。JSONはnative node設定でも起動manifestでもない。nullを含むため起動に利用できない。

実装段階で各案に別genesis・seed・data directoryを用意する。秘密鍵や動作未確認のDocker Composeをこの段階で作らない。実際のport・image・起動停止コマンドはM0/M4の記録に追加する。
