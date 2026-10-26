# atomic-bundle CLI雛形

未実装。言語・SDK・package manifestはM0で選定する。

原本legacy検証、三操作構築、inventory署名、outer P連署、状態照会。原本Aggregateの再署名・書換えをしない。

予定モジュールはcodec、公開署名検証、構築コマンド、signer入力、明示announce、状態表示。合意処理の代用台帳は作らない。

[入出力契約](../../docs/client-contract.md)に従い、profile・signer・transportを分離して渡す。buildはオフライン、announceは別操作。
