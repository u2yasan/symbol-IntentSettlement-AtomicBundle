# Codex 実装指示書 — AtomicBundle v1

> 現在の段階（2026-10-26）: 仕様詳細化と雛形作成のみ。以下は将来、実装を依頼された段階の指示であり、今すぐclone・C++実装・ノード起動を行う指示ではない。先に[構成](../docs/repository-layout.md)、[判断一覧](../docs/decisions.md)、[受入表](../docs/acceptance-matrix.md)を読む。

## 目的と読込順

あなたは Symbol / catapult の C++ 実装担当である。最初に `codex/00-common-instructions.md`、`docs/00-common-spec.md`、`docs/atomic-bundle-design.md` を読む。現状は設計のみであり、実装・検証済みではない。

`symbol/symbol@6c04695555230c89a6ffa2ac4d41774dcac77ae3` を基準に、既存署名済み AggregateComplete V3 注文を、不可分に funding / execution / sweep する **DEX 限定の新しい top-level transaction plugin**を実装せよ。注文 fixture は `HinaBlogChannel/heika@891a2cb17a0d52c85ed85594d8283c844481a6cb` の `examples/intent-dex` を参照する。

隔離 private chain、新規 genesis、test-only 資産だけを使う。公開ネットワーク、実鍵、mainnet 更新は対象外。基準版で動く実装を作る。

## 守る仕様

- 論理子操作は `funding → legacy order → sweep` の三つだけ。legacy は記事どおり Transfer 三つの AggregateComplete V3 一つ。
- funding / sweep は native EmbeddedTransfer V1。**単独の通常 Transfer として署名しない。**
- inventory が外側を署名し、P が外側 hash を連署する。maker は legacy だけ署名する。legacy P 連署は外側 P 連署の代わりにならない。
- legacy の共通検証と Aggregate 検証を全て維持する。`childPlugin.publish()` だけで済ませない。
- outer fee は solver が一回払う。legacy actual network fee は 0、元 MaxFee は変更しない。tip は全量回収し、funding / sweep の別 fee はない。
- P の既存 dust を保持する。sweep-all を禁止し、全モザイクの `P_after=P_before` を検証する。
- 消費は既存 HashCache の `(legacy Deadline, canonical legacy hash)` を通常経路と共有し、rollback で除去する。
- 未対応の Bonded・再帰・alias・partial・multisig・メッセージ・管理操作は明示的に拒否する。maker / inventory / P は相異なる通常の単一鍵アカウント。

## M0 — 実リポジトリの確認と作業分離

適用される `AGENTS.md`、build / test 文書、CMake、schema generator を実読する。既存変更を確認・保護し、基準 commit から独立 worktree と `poc/atomic-bundle-v1` branch を作る。dirty tree の持込みや他者の変更の reset をしない。

最低限、次の実装と対応テストを読む。

- `TransactionPlugin.h`、`Transaction.h`、EntityHasher / signature utilities。
- `NotificationPublisher.cpp`、`AggregateTransactionPlugin.cpp`、Aggregate model / validators、catbuffer の aggregate schema。
- `TransactionHashObserver.cpp`、`UniqueTransactionHashValidator.cpp`、HashCache の保存・prune・rollback。
- `BatchEntityProcessor.cpp`、processing / undo subscriber、UT と harvesting の検証経路。
- `BlockUtils.cpp`、`SourceChangeObserver.cpp`、native Transfer、account / mosaic restrictions、multisig 認証。
- fee debit を変える fork 設定、private-network の genesis / 起動構成。

既存 type ID と他方の PoC を検索し、非重複の実験型を記録する。架空の API・既存型番号・テスト名を作らず、新しい adapter は新設と明記する。

commit、実コマンド、実験型、設定、通知方針を plan に残す。共通の三 fork height は Height(1) 相当で genesis と全ノードに統一し、初期の通常 Aggregate V3 成功を確認する。差異は根拠付きで記録し、署名・重複検証を省いて解消しない。

## M1 — wire / codec と署名対象

設計書の wire を schema / C++ model にする。body は Root32 / ActionsSize u32 / ActionCount u16 / OuterCosigCount u16 / Reserved8 / ActionStream / P cosig104、count は 3 と 1。

frame は `kind u16, version u16=1, flags u16=0, reserved u16=0, index u32, payloadLength u32, payload, zeroPadTo8`。kind は funding=1、legacy=2、sweep=3、index は 0/1/2。root は次の通り。

```text
SHA3-256(ASCII("SYMBOL_ATOMIC_BUNDLE_ACTIONS_V1")
         || LE32(3) || LE32(byte_length(ActionStream)) || ActionStream)
```

ASCII に NUL・改行を付けない。native payload と frame の padding を区別し、異常長、余剰 bytes、非ゼロ reserved、overflow、非 canonical なモザイク順序を拒否する。

外側主署名には root までの固定 body を含め、末尾 P cosig を含めない。P の署名対象は基準版で計算する外側 tx hash。`merkleSupplementaryBuffers` は outer P 公開鍵 32 bytes 一つ。連署前後で hash が同じ、outer header / root 改変で署名が失敗する golden tests を作る。opaque root fixture は実行不能な codec fixture と明記し、native な実行用 fixture も別に用意する。

outer 4,096 bytes、legacy 2,048 bytes、署名 4 個、固定深さ、outer lifetime 2 時間を PoC 仮値として設定する。

## M2 — C++ plugin と認証 adapter

load 可能な plugin、登録、CMake、codec、validator を追加する。新型は top-level のみ。native Aggregate の embedding 不可を一般的に緩めない。

legacy adapter は maker の AccountPublicKey、Entity、TransactionNotification、Deadline、actual fee 0 の Fee、replay-protected 主署名と、Aggregate 固有通知・連署を維持する。元 legacy bytes と hash を使い、通常 publisher による MaxFee 課金や top-level source 移動を発生させない。原本の maker signature / Deadline / MaxFee を再署名・書換えして通してはならない。

maker の Aggregate 操作権限と inventory の新型操作権限を確認する。**Bundle 専用の追加制約として全五つの Transfer の signer に outgoing Transfer permission を要求する**。maker は give / tip、P は get / sweep、inventory は funding。native embedded publisher だけでこの検査をしたことにしない。通常 Aggregate の既存挙動は変更しない。通常・remote・multisig アカウントの扱いも native 規則と v1 制限で固定する。

残高・制限・期限・消費状態の変更を検証し、四つの署名はそれぞれ個別に破損した負試験を作る。

## M3 — 状態・fee・replay・source

同じ native cache delta 上で funding、注文、sweep を処理し、失敗時は全差分を戻す。sweep は give と tip の増分だけ。give と currency が同じなら checked addition で一つにまとめる。dust と無関係資産を動かさない。

共通仕様に従い、private chain は `TotalVotingBalanceCalculationFix=Height(1)` 相当の実在設定を確認し、activation height 2 以降で custom 処理後に outer fee debit が来るよう統一する。設定表記と native 通知順を実測する。funding 全量はその実行時に必要だが、outer fee のために custom 前の残高を不必要に二重要求しない。UT の MaxFee 仮徴収と、実ブロックの actual fee の違いも試験する。

legacy TransactionNotification で既存 HashCache を検証・更新する。子の fee と一緒にこの通知を省かない。同一・別ブロック、再起動、prune、rollback を試し、専用の消費 cache は増やさない。

`embeddedCount=6`、DeepCount=7 とする。receipt source primary は外側 index を保持し、secondary は funding 1 / legacy container 2 / legacy内部 3,4,5 / sweep 6、外側へ戻る前に 0。既存 Aggregate の相対 source 更新を adapter で閉じ込める。source trace、block limit 計数、fee receipt、receipt hash を検証する。

## M4 — 三ノードの統合環境

同じ plugin の C++ catapult 三ノードを独立 genesis で起動し、public seed を無効にする。test-only keys、network ID、generation hash seed、設定 hash を記録する。

fixture / CLI で maker の事前署名と solver の構築を再現する。全ノードの hash 一致と、通常 Transfer / Aggregate の回帰を確認する。mock の残高計算で代用しない。

## M5 — 攻撃対照と回帰 gate

設計書 AB-01〜18 を実施し、実行コマンドと結果を ID 別に残す。必須の難しいケースは以下。

1. **旧方式の対照**：T1/T2/T3 の元ブロックに対し、早い有効 timestamp の競合ブロックへ T1 と P→攻撃者送金を入れる。private chain のみで VRF / hit / score を満たす採用条件を再現する。
2. **新方式の抽出拒否**：funding embedded payload を単独 Transfer へ変換・直接収録しても、inventory の有効な独立署名がなく拒否されること。元の外側署名を流用しても通らないこと。
3. **新方式の fork**：同一親から競合枝を作る。正しい Bundle 全体なら全資産移動が一緒に成立し、除外すれば全て成立しない。途中だけ残る結果がないこと。finalized 済み元ブロックの差し替えは拒否する。
4. **経路間 replay**：通常→通常、通常→Bundle、Bundle→通常、Bundle A→Bundle B の四方向を、同一ブロックと別ブロックで検証する。outer の hash / signer / deadline を変えても子注文を再消費できないこと。
5. **後段失敗と再起動**：test harness 限定で legacy 適用後・sweep 中・outer fee 前へ failure を注入し、funding と子消費を含む全差分が消えること。署名不正は別の前段拒否試験にし、本番検証を遅らせない。rollback 後は期限内・未消費なら正しく再署名した別 wrapper を受理する。restart 後に消費済み注文が復活しないこと。

UT 除外と強制収録した不正ブロックの拒否を別々に試す。壊れた署名・timestamp のブロックを有効な fork の代用にしない。通常 Aggregate と変更した共通経路の回帰 gate を完了する。

## M6 — 納品と結果報告

実装差分、schema / codec、native fixture、三ノード設定、再実行手順、test runner、raw logs、hash / balance 比較、設計との差異、dependency / build 制約を残す。

結果は成功・失敗・環境制約で未実行・仕様未対応を区別する。コンパイル、mock、署名を省いた happy path だけで完了にしない。阻害されても可能な作業は続け、未検証項目を明示する。

完了時は仕様、型・隔離条件、抽出防止・replay・fee・source・rollback の証拠と制約を報告する。mainnet 適用や監査完了を主張しない。

## 一次資料

コードは [設計書の一次資料](../docs/atomic-bundle-design.md#一次資料) を参照。[公式 Plugin 説明](https://docs.symbol.dev/concepts/plugin.html) は構成の参考であり、固定版コードの代わりにしない。
