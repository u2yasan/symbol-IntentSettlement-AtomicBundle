# 設計判断・未決事項

更新日: 2026-10-26。基準ソースは今回取得・再検証していない。以下のM0項目は既存資料の記述を検証するための作業であり、確認済みではない。

## 固定する境界

| 判断 | 内容 | 根拠 |
|---|---|---|
| D-01 | 詳細実装は開始しない | 今回のユーザー指示、ADR-0001 |
| D-02 | 両案を分離し、Intentから実装を検討 | 既存README・共通仕様 |
| D-03 | private chain専用、fresh genesis、3ノード | 共通仕様3章 |
| D-04 | Intentは1注文・2資産・全量・専用cache | Intent設計1/6章 |
| D-05 | Atomicは固定3操作・四署名・既存HashCache | Atomic設計3/4/7章 |
| D-06 | REST・UI・注文板は必須にしない | 共通仕様7章 |

## 実装前に閉じる項目

| ID | 未決・未確認点 | 担当工程 | 完了条件／影響 |
|---|---|---|---|
| Q-01 | EntityType、FacilityCode、notification/cache ID | M0 | 基準版の登録一覧と照合し、両案のABI台帳へ記録。0などの仮番号で実装しない |
| Q-02 | ビルド・schema生成・plugin登録・永続化API | M0 | 実ファイル、関数、実コマンド、baseline build結果を記録 |
| Q-03 | 三fork設定の実キーとfee通知順 | M0 | nemgen・全ノード設定が一致し、Custom→fee順をtraceで確認。activation高さ1/2の境界も確認 |
| Q-04 | Atomic adapterの通知channelとundo順 | M0〜M2 | 標準認証・deadline・HashCacheを保持し、子feeとprimary sourceの二重処理を起こさない通知対応表 |
| Q-05 | Intent署名とnative cryptoの互換性 | M1 | 既存200Bベクトルをnative C++で検証。Pythonのみの成功は不足 |
| Q-06 | Atomic outer署名・hashの正確なnative byte範囲 | M0〜M1 | EntityHasher/dataBuffer実装とgolden fixtureを照合。連署の前後で同hash |
| Q-07 | SDKとCLI言語・固定依存版 | M0 | 基準版との互換性、64bit精度、独立codec、鍵入力方式を比較して選定。今回は選定しない |
| Q-08 | 私設網ID・seed・epoch・通貨・ノード構成 | M0〜M4 | 両案別のmanifestを埋め、設定hash、genesis生成、外部peer排除を検証 |
| Q-09 | Intentのreceipt source割当 | M0〜M2 | 脚がembeddedでない点を保ち、標準sourceへの対応を記録。独自receipt追加の要否も判断 |
| Q-10 | cache保存／再構築／rollbackの実経路 | M0〜M3 | IntentのMerkle永続化とAtomicの既存HashCache再構築を別々に確認 |
| Q-11 | エラー番号と複数違反時の優先順位 | M0〜M2 | native順に整合するコード表・優先順位fixture。文書の論理ラベルを数値コードと混同しない |
| Q-12 | AtomicのUT MaxFee仮徴収と後払いfee | M0〜M3 | tip/sweep後のfee資金だけで成立するケースの候補・受信経路差を確認。独自gateで隠さない |
| Q-13 | サイズcap・最大寿命の仮値 | M0〜M1 | 4096B/2048B/2hとnative上限を照合。有効な固定形の実サイズも算出 |

## 仕様上の制約として見える化する事項

- **未来の注文の取消:** IntentCancelにも6hの実行窓がある。期限が6hより先の注文は現行v1ではその時点で取消できない。UI/CLIで隠さない。常時取消を求めるなら、取消の期限規則を変更する別の設計判断と試験が必要。
- **未確定の取消:** メンプール到着順は約定優先順位を保証しない。確定前の取消を成功扱いにしない。
- **Intentの無期限履歴:** pruneなしはPoCの安全側の制約だが、注文数に応じて状態が増加する。長期運用の容量設計は未実施。
- **AtomicのP鍵:** 公開されたP鍵への署名は秘密を保持する者の排他認可ではない。在庫保護は外側inventory署名、root拘束、不可分性、dust不変条件の組合せで成立させる。
- **Atomicのreplay証拠:** StateHash一致だけでは既存HashCacheの共有消費を証明できない。通常経路とBundle経路から実際に再投入して拒否を確認する。
- **実行窓とローカル時計:** CLIの期限見積りは補助。合意判定のBlockTimeと一致する保証はない。
- **数値とeconomics:** 小数表示用divisibilityを署名数量に混ぜない。価格の適正性、利益、流動性は成立条件とは別。

M0で新たな不一致が判明した場合は、該当ID、根拠ソース、仕様への影響、決定、対応テストを追記する。未確認項目を推測で「完了」にしない。
