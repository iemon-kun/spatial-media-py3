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
