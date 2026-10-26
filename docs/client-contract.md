# 最小CLIとファイル入出力の契約

文書版0.2 / **コマンドは提案、未実装**。言語・SDKはQ-07で選定する。RESTの独自routeや注文板の実装は必須にしない。

## 境界

codec・公開署名検証はネットワーク接続なしで実行できること。鍵を必要とする操作はcreate/signに限定し、announceは完成した公開payloadだけを受け取る。秘密鍵は引数・環境変数・JSON成果物・ログへ書かず、対話入力または明示したsigner入力経路を使う。test-only公開seedを実運用鍵と混同しない。

署名・送信時には、案、network identifier、generation hash seed、epoch、通貨mosaic、ABI設定digestを含む固定profileを選択する。nodeから返されたseedでprofileを自動上書きしない。未知型番号、未記入profile、seed相違は処理を停止する。

## 提案操作

| 操作 | 入力 | 出力 | 接続 |
|---|---|---|---|
| `intent-order create` | profile、資産・整数数量、validUntil、maker signer | order136B、maker署名、orderId | 不要 |
| `intent-order inspect/verify` | 公開order envelope、profile | decoded値、署名結果、orderId | 不要 |
| `intent-settle build` | 公開order、solver signer、外側期限/MaxFee | 署名済Settlement bytes、tx hash | 不要 |
| `intent-cancel build` | canonical order、maker signer、外側期限/MaxFee | 署名済Cancel bytes、tx hash | 不要 |
| `atomic-order inspect/verify` | 原本legacy bytes、profile | legacy hash、当事者、数量、tip、期限、署名結果 | 不要 |
| `atomic-bundle build` | 原本legacy、inventory/P signer、外側期限/MaxFee | 三frame、root、四署名を持つBundle bytes | 不要 |
| 各取引の`announce` | 完成payload、profile、明示endpoint | 送信結果、tx hash | 私設網のみ |
| `intent-status` / `atomic-status` | 注文／tx識別子、profile、ブロック参照 | 観測ブロックと状態、可否理由 | 私設網または試験用cache reader |

buildは残高を推測して「約定可能」と表示しない。価格・利益を保証しない。後段でnodeが最新状態を再検査する。buildとannounceを自動で連続実行しない。

## JSON envelope案

将来の交換ファイルは`schema`、`schemaVersion`、`networkProfileDigest`、`payloadHex`、`payloadSha3_256`を持つ。Intent orderはさらに`makerSignatureHex`と`orderId`を持つ。Atomic原本は`legacyTransactionHash`を持つ。これらはwireへの追加フィールドではない。

- `payloadHex`の意味をschemaごとに固定する。orderなら136B、legacyなら完全な原本Aggregate、完成取引ならheaderを含む全bytes。
- envelopeのhash・ID・表示fieldは読込時に再計算し、不一致を拒否する。digestは認証の代替ではない。
- hexは出力時に小文字・prefixなし・偶数長へ正規化。入力も同規則で受理する。数量とu64時刻は先頭ゼロのない10進文字列（ゼロは`"0"`）。数量0の業務拒否は別に行う。
- JSON重複key、未知schemaVersion、未知field、桁あふれ、符号、指数表記、小数を拒否する。bytesと表示値の二重管理で署名内容を取り違えない。
- JSON文字列そのものに署名しない。envelope形式の確定はQ-07で行い、既存fixture JSONの形式を無断で変えない。

## 状態表示

送信ライフサイクルと注文状態を別fieldにする。

| 種類 | 値 | 意味 |
|---|---|---|
| 送信 | BUILT | ローカル生成のみ |
| 送信 | ANNOUNCED | endpointに送信した。収録の保証なし |
| 送信 | UNCONFIRMED | 未承認poolで観測 |
| 送信 | CONFIRMED | 特定height/block hashで収録を観測 |
| 送信 | FINALIZED | そのblockのfinalizationを観測 |
| 送信 | REJECTED / UNKNOWN | nodeの拒否／現在の結果不明 |
| Intent注文 | FILLED / CANCELLED | 専用cacheの保存状態 |
| Intent注文 | OPEN / EXPIRED | 完全orderとBlockTimeから導出 |
| Intent注文 | UNKNOWN | orderIdだけで保存recordなし等 |
| Atomic注文 | consumed観測／UNKNOWN | native検証・HashCache照会の範囲。架空RESTを前提にしない |

応答は`observedHeight`、`observedBlockHash`、`observedBlockTime`、取得元、finalization観測を含める。ブロックを固定した読取りが提供できない経路では整合したsnapshotと主張せず、試験用readerを用意する。reorgでCONFIRMEDから未収録へ戻り得る。送信タイムアウトは失敗確定ではなくUNKNOWNとし、tx hash照会後に同一bytesの再送を検討する。期限延長や新しい外側署名を自動生成しない。

## エラー出力案

stdoutは構造化結果、stderrは診断。成功exit=0、入力/encoding=2、署名/profile=3、通信/照会不能=4、node拒否=5をCLI案とする。これはnative failure codeではない。`stage`、論理`code`、`nativeCode`（存在時）、説明、tx hash（計算できた場合）を記録する。timeoutをnode拒否と同一視しない。Q-07/Q-11で実装規約へ合わせて確定する。
