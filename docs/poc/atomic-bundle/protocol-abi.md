# AtomicBundle ABI台帳

文書版0.2 / wire version 1 / **設計値。native照合はNOT_RUN**。
正本: [基本設計3〜4章](../../atomic-bundle-design.md)。EntityType・FacilityCode・通知IDはQ-01で決定、未割当。新cache IDは不要。

## 外側レイアウト

S=`ActionsSize`。区間は開始含む・終了含まない。

| 区間 | 内容 |
|---|---|
| `[0,128)` | native Transaction header、inventory署名 |
| `[128,160)` | ActionsRoot32B |
| `[160,164)` | ActionsSize u32LE |
| `[164,166)` | ActionCount u16LE=3 |
| `[166,168)` | OuterCosignaturesCount u16LE=1 |
| `[168,176)` | reserved8B=0 |
| `[176,176+S)` | ActionStream |
| `[176+S,280+S)` | native Cosignature104B、version=0、P signer |

全長は`280+S`、設計上限4096B。Sはframeの全長和で8の倍数。native cosignature各fieldの内部位置はM0で確認する。欠損連署を補うときにSizeやcountを変更して既存主署名を流用しない。最終サイズ・countを先に確定し、連署欄の有無によらず同じ署名/hash対象を作る。

## frameとparse順

frame内offset: 0=kind u16、2=version u16=1、4=flags u16=0、6=reserved u16=0、8=index u32、12=payloadLength u32、16=payload。全整数LE。

1. 外側上限・固定headerと宣言長を、読み込み・メモリ確保より先に検査する。
2. frame headerの残byteを検査し、kind/indexが`(1,0),(2,1),(3,2)`の順であることを確認する。
3. payloadLengthが残領域内に収まることを検査。padは`(8 - ((16+length) mod 8)) mod 8`。加算前にoverflowを検査する。
4. padが全て0で、frameがS領域からはみ出さないことを確認する。
5. 三frame読了時にSをちょうど消費すること。末尾連署をframeとして読まない。
6. payloadをnative型として厳密decodeする。native sizeとpayloadLengthが一致し、内部padding・reservedも正しいことを確認する。

kind1/3はEmbeddedTransfer V1。kind2は完全なAggregateComplete V3、上限2048B。外側の上限内であっても、固定形・native型の条件に反すれば拒否する。4096B上限ちょうどの有効な固定形が存在すると仮定して水増しpayloadを作らない。

## root・四署名・二つのhash

`ActionsRoot = SHA3-256(ASCII("SYMBOL_ATOMIC_BUNDLE_ACTIONS_V1") || LE32(3) || LE32(S) || ActionStream)`。domainのNUL・改行なし。frame padding、legacy内のP連署もrootに含む。

| 検証 | 対象 | 固定条件 |
|---|---|---|
| inventory主署名 | native署名対象header部分＋body固定48B | ActionStreamをrootで拘束。末尾P連署は対象外 |
| outer P連署 | canonical outer transaction hash | legacy P連署を流用不可 |
| legacy maker主署名 | 原本Aggregateのnative署名対象 | signed MaxFee/Deadline/bytesを変更しない |
| legacy P連署 | canonical legacy transaction hash | outer hashへの署名と別 |

outer hash、legacy hashを独自式で実装しない。native baselineとの照合が必要。P公開鍵32BをouterのMerkle supplementary bufferとして一つ返す。outer P署名64B自体を追加bufferに入れない。

HashCacheの注文キーは`(legacy Deadline, canonical legacy hash)`。root、outer hash、JSON digestをキーにしない。outer hashの連署前後不変性とnative block Merkle寄与を別々に検証する。

## 計数と制約

- logical actions=3、legacy embedded=3、outer/legacy cosignature=各1、署名=4。
- top-levelのみ、embedding不可、再帰不可、embeddedCount=6、DeepCount=7。
- outer lifetime=2hはPoC仮値。outer Deadline≤legacy Deadline、両方native期限検証対象。
- size×fee multiplier、同mosaicのgive+tip、残高creditをoverflow検査。sweepは同IDを合算して昇順、最大2種類。

既存[Atomic fixture](../../../fixtures/atomic-action-root-v1.json)はopaque payloadのroot検算だけ。native三操作、四署名、outer/legacy hash、source、HashCacheを含むgolden fixtureは未作成。
