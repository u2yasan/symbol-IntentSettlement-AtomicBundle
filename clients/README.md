# 最小クライアント

設計用ディレクトリ。独立codecの相互運用検証を担当する。現時点で実行コマンドやSDK依存はない。

- [CLI契約](../docs/client-contract.md)
- [Intent](intent-settlement/README.md)
- [Atomic](atomic-bundle/README.md)

両案を共通の汎用executorへまとめない。HTTP/鍵入力等の共有は実装が安定した後に別変更で判断する。
