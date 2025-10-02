# 変更履歴

このフォークは、上流（Upstream）リポジトリをクローンして以降の主な変更点を記録します。バージョン表記は `<上流バージョン>-py3.X` の形式です。

## [2.1a1-py3.0] - 2025-09-30

- 互換性変更（Python 3 対応） [cddb6b2]
  - バイト列処理: `ord(...)` 依存を排し、`bytes` のインデクシングで値を取得（`get_descriptor_length`, `get_aac_num_channels`）。
  - 文字列結合: `console()` が単一引数を取る前提に合わせ、警告文を文字列連結へ変更（`parse_spherical_xml`）。
  - 定数名の統一: `spherical_prefix` ではなく `SPHERICAL_PREFIX` を使用（`parse_spherical_xml`）。
  - 出力フィールド: `num_channels` → `num_audio_channels` に合わせて参照先を更新（`__main__.py`）。

- 修正 [cf5f5a9, cddb6b2]
  - `generate_spherical_xml()` のデフォルト投影タイプの誤字を修正: `equiretangular` → `equirectangular`（cf5f5a9）。
  - `Box.content_size` の長さ計算の誤りを修正: `len(contents)` → `len(new_contents)`（cddb6b2）。

- ドキュメント
  - `README.md` の冒頭にフォーク告知ブロックを追加し、非公式の Python 3 対応フォークである旨と変更履歴への導線を明記。

- ライセンス/帰属
  - 上流の `LICENSE` を保持し、`spatial-audio/NOTICE` 末尾に帰属文を追記（Apache-2.0 §4 準拠）。

- コンプライアンス
  - 以下のソースファイルで、シバンとエンコーディング宣言の直後に「変更を加えた旨」のコメントを追加（Apache-2.0 §4 要件）。
    - `spatialmedia/__main__.py`
    - `spatialmedia/metadata_utils.py`
    - `spatialmedia/mpeg/box.py`

- リポジトリ整備
  - `.gitignore` を拡張し、仮想環境・ビルド成果物・サンプル・個人メモ等を除外（例: `.venv/`, `dist/`, `build/`, `.sample/`, `memo.txt`, `audio_materials/`, `todo.md`）。

## [2.1a2-py3.0] - 2025-10-01

- 機能追加（GUI）
  - 「Spherical Video Metadata V2（sv3d）」注入オプションを追加（v1 XML との切り替え）。
  - 立体視レイアウト選択（`top-bottom`/`left-right`）を追加。v1/v2 双方の注入に反映。
  - メタデータ読込時、v1 の StereoMode を検出して GUI に反映（TB/LR）。

- 内部仕様
  - V2 有効時は `projection=equirectangular` を設定し、必要に応じて `stereo_mode` を設定して注入。
  - V2 無効時は従来どおり v1 XML（uuid）を生成し、StereoMode を必要に応じて付与。

- 影響ファイル
  - `spatialmedia/gui.py`

- 既知の制限
  - VR180（`mshp` メッシュ投影）には未対応（上流ツールの対象外）。
  - 非球面 3D のみ（st3d 単独注入）は GUI 未対応。CLI（例: `-2 -p none -s left-right`）を利用してください。

- ドキュメント
  - `README.md` に GUI の新機能（V2 トグル、TB/LR 選択）、使い方（GUI/CLI）、確認チェックリストを追記。

- ライセンス/帰属
  - `spatialmedia/gui.py` の先頭に改変表記を追記（Apache-2.0 §4 準拠）。

## [2.1a3-py3.0] - 2025-10-02

- 検証
  - CLI スモークテストで v1/v2、TB/LR、SA3D の注入経路を確認（`.sample/test_outputs/` に出力）。

- バグ修正（V2 メタデータ）
  - `sv3d` に必須の `svhd`（Spherical Video Header）を実装し、注入フローに追加。
  - ffprobe の "Missing spherical video header" 警告を解消。
  - 影響ファイル: `spatialmedia/mpeg/sv3d.py`, `spatialmedia/metadata_utils.py`

- ライセンス/帰属
  - `spatialmedia/mpeg/sv3d.py` の先頭に改変表記を追記（Apache-2.0 §4 準拠）。
