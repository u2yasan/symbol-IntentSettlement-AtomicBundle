# IntentSettlement / IntentCancel ABI台帳

文書版0.2 / wire version 1 / **設計値。native照合はNOT_RUN**。
正本: [基本設計3〜6章](../../intent-settlement-design.md)。同じ値を再定義する別プロトコルではない。

## 登録番号

| 項目 | 値 | 決定方法 |
|---|---|---|
| IntentSettlement EntityType | 未割当 | Q-01、既存enumと両案を照合 |
| IntentCancel EntityType | 未割当 | 同上 |
| FacilityCode、通知ID | 未割当 | native登録規約を確認 |
| consumption cache ID | 未割当 | nemgen・node共通の登録表へ追加 |
| header / order version | 1 / 1 | v1設計値 |
| flags / reserved | 全byte 0 | 将来用途を先取りしない |

未割当は0ではない。実装用schemaへ未割当番号を書き出してはならない。

## wire領域

区間は開始含む・終了含まない。LEはunsigned little endian。native headerの内部offsetはM0で再確認する。

| 型 | バイト区間 | 内容 |
|---|---|---|
| Settlement | `[0,128)` | native Transaction header、署名者solver |
| Settlement | `[128,264)` | canonicalOrder |
| Settlement | `[264,328)` | makerSignature、64B |
| Cancel | `[0,128)` | native Transaction header、署名者maker |
| Cancel | `[128,264)` | canonicalOrder、追加署名なし |

`Size`はSettlement=328、Cancel=264に厳密一致。余剰footer、alias、未知version、embeddingを拒否する。両型とも`embeddedCount=0`、DeepCount=1。

| order内offset | 長さ | 内容 |
|---:|---:|---|
| 0 | 1 | version=1 |
| 1 | 1 | network |
| 2 | 2 | flags=0 |
| 4 | 4 | reserved=0 |
| 8 | 32 | makerPublicKey |
| 40 | 24 | maker自身のrecipientAddress |
| 64 | 8 | giveMosaicId、LE |
| 72 | 8 | giveAmount、LE、正の整数 |
| 80 | 8 | getMosaicId、LE、giveと異なる |
| 88 | 8 | getAmount、LE、正の整数 |
| 96 | 8 | validUntil、network epochからのms |
| 104 | 32 | nonce |

## 認証対象

| 認証 | 署名・hash対象 | 注意 |
|---|---|---|
| maker条件署名 | SHA3-256(domain文字列)32B + seed32B + order136B = 200B | 200Bに直接Ed25519署名。orderIdへの署名ではない |
| orderId | 上記200BのSHA3-256 | makerSignature、外側headerを含めない |
| solver Settlement署名 | native署名対象header部分＋本文200B | native replay protectionを維持 |
| maker Cancel署名 | native署名対象header部分＋本文136B | outer signerとorder maker一致 |

domainはUTF-8の`SYMBOL_INTENT_ORDER_V1`。改行・NULなし。maker条件署名を既存通知で検証する場合だけseed二重付加を避ける。外側のnative署名までreplay protectionを無効にしてはならない。

## cache value

keyはorderId32B。valueは80Bで、offset 0=status1B、1=reserved7B、8=makerAddress24B、32=validUntil8B、40=consumedHeight8B、48=outerTransactionHash32B。statusは1=FILLED、2=CANCELLED。未知status、非ゼロreserved、余剰byteを拒否する。

構造体のメモリ表現をそのまま保存・hashしない。native Patricia leafでkey/valueをどのようにhashするかはQ-10で実装に合わせて記録する。80Bのvalue仕様だけでStateHash計算方式が確定したとは扱わない。

## 数値境界

- 金額、ID、期限、heightはu64。JSONでは10進文字列または規定長hex。
- `validUntil > BlockTime`を先に検査し、その後差が21,600,000以下であることを確認する。
- 口座・モザイク単位の必要額合算、受取残高への加算、fee乗算をchecked arithmeticで扱う。
- `getMosaicId == currencyId`ならsolver必要額は`getAmount + MaxFee`。giveがcurrencyの場合でも将来の受取で事前fee条件を満たした扱いにはしない。

## 実装へ渡す必須ベクトル

既存[Intent fixture](../../../fixtures/intent-order-v1.json)はcanonical orderと署名だけ。追加が必要なのはnative outer headerを含むSettlement/Cancel、全fieldの改変、cache80B、非ゼロfee、最大値合算、全zero nonce、余剰byte、失敗コード優先順位である。native照合が済むまで番号・署名・実行互換性は確定しない。
