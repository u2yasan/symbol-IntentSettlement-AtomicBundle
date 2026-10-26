# バイナリと署名の参照ベクトル

このフォルダは文書の正規化規則を固定するための小さい参照実装です。**C++プラグイン、catapultノード、実行可能な交換取引を含みません。**

## 使い方

Python 3.10以上と `cryptography` が必要です。公開済みの使い捨て鍵だけを使い、ネットワークへ接続しません。

```bash
python fixtures/generate_reference_vectors.py --check
```

保存済みJSONと生成結果がバイト単位で一致すること、Ed25519署名が検証できること、金額を1byte変えると署名が通らないことを確認します。JSONを再生成する場合は `--check` を省略します。設計の変更なしに、実装へ合わせるためだけに期待値を書き換えないでください。

## IntentSettlement

`intent-order-v1.json` には次が入っています。

- 136byteのcanonical order、200byteの署名メッセージ、そのSHA3-256であるorderId。
- 公開テスト秘密seed、公開鍵、24byteのSymbol形式address。
- 標準Ed25519で200byteそのものへ付けた64byteの署名。
- 2の53乗を超える数量を含む、64bit精度確認用の追加ケース。

すべての数量はJSONでは10進文字列です。network identifierはテスト形式の `0x98`、generation hash seedは合成値であり、公開Symbol testnetの設定ではありません。mosaic IDも構造確認用で、実在や十分な残高を意味しません。2つ目のケースは大整数codecの確認だけが目的です。

この参照実装の署名検証にはPython `cryptography` を使います。**Symbolネイティブ実装との照合は、CodexのM1で実施すべき未完了のゲートです。** JSONの `native_catapult_cross_check` と `on_chain_acceptance` は `NOT_RUN` のまま提供します。

検証時にgeneration hash seedをもう一度prependしないでください。署名対象は文書で規定した200byteです。標準通知のReplayProtectionを使う場合はその設定と入力を照合します。

注文期限の合意条件は `BlockTime < validUntil <= BlockTime + 6h` です。`BlockTime == validUntil` は期限切れです。この時刻判定は署名ベクトルとは別のC++テストで確認します。

## AtomicBundle

`atomic-action-root-v1.json` は、3つの型付きframe、長さ、index、ゼロpadding、順序、root計算の参照値です。

**payloadは意図的にopaqueな短いbyte列であり、有効なEmbeddedTransferやLegacy Aggregateではありません。** そのため、このJSONからネットワークへ送れる取引は作れません。実際のLegacy Aggregateとsolver／P署名を含むgolden fixtureは、CodexのM1でSymbol SDK／C++の両方を使って追加します。

rootには全frameを含めます。外側P連署をrootへ循環的に含めません。外側署名・取引ハッシュ・P連署・block Merkle成分は、このframe-only fixtureとは別の必須テストです。

## 期待するCodexの追加検証

1. 参照ベクトルをC++側で読み、encode/decode、orderId、actionsRootが一致することを確認する。
2. Intent署名をCatapultの標準暗号実装でも検証する。二重seed、orderIdへの誤署名、Keccakとの混同を負試験にする。
3. 実在する私設ネットワーク設定で新しいベクトルを作り、SDK側とC++側を相互検証する。
4. Atomicの実Legacy payloadとouter署名・P連署を生成し、単独Aggregate／Bundle内実行の共有重複検査まで進める。

これらを実行するまで、参照ベクトルの一致だけを「PoCが動作した」と報告しないでください。
