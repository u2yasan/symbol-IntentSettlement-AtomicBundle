# intent-settlement CLI雛形

未実装。言語・SDK・package manifestはM0で選定する。

注文生成・検証、決済、取消、状態照会。order136Bとmessage200Bを独立codecで扱う。

予定モジュールはcodec、公開署名検証、構築コマンド、signer入力、明示announce、状態表示。合意処理の代用台帳は作らない。

[入出力契約](../../docs/client-contract.md)に従い、profile・signer・transportを分離して渡す。buildはオフライン、announceは別操作。
