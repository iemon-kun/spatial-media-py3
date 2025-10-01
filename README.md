# Python 3 対応版 Spatial Media（非公式フォーク）
YouTube 360°/VR 用メタデータ埋込ツールをPython3向けに改変した非公式版です。
iemon_kun (GitHub: iemon-kun)が行なった改変は[CHANGELOG](CHANGELOG.md)に記載しています。

## 追加機能（GUI）
- V2 メタデータ注入（sv3d/proj/prhd/equi）トグルを追加（v1 XML と切替）
- 立体視レイアウト選択（top-bottom / left-right）を追加
- 読み込み時、v1 StereoMode（TB/LR）を検出して反映

## 使い方（概要）
- GUI: `uv run python -m spatialmedia.gui`
  - 「My video is spherical (360)」にチェック
  - 3D の場合はチェックのうえ「top-bottom / left-right」を選択
  - V2 で注入する場合は「Use Spherical Video Metadata V2 (sv3d)」をオン
  - 空間音声（AmbiX ACN/SN3D; FOA/FOA+HL）の場合はチェック
  - 出力先ディレクトリを選んで Inject
- CLI 例
  - 360（モノ）V2: `python -m spatialmedia -i -2 -p equirectangular input.mp4 output.mp4`
  - 360 3D（TB）V2: `python -m spatialmedia -i -2 -p equirectangular -s top-bottom input.mp4 output.mp4`
  - 360 3D（LR）V2: `python -m spatialmedia -i -2 -p equirectangular -s left-right input.mp4 output.mp4`
  - 空間音声（既に 4ch/6ch）付与: 上記に `-a` を併用

## 確認チェックリスト（抜粋）
- 360 モノ: v1/v2 いずれも注入後に再生確認
- 360 3D: TB/LR で v1/v2 注入後に視野切替（WASD/ドラッグ）確認
- 空間音声: FOA/FOA+ヘッドロックの `SA3D` 注入と再生確認（48 kHz）
- 非球面 3D のみは CLI で実施（`-2 -p none -s left-right`）

## 免責事項
- 本フォークは Google Inc. の公式プロジェクトではありません。Google/YouTube および原著作者とは一切の提携関係にありません。
- 本ソフトウェアは「現状のまま」提供され、明示または黙示を問わずいかなる保証も行いません。自己責任でご利用ください。
- YouTube は Google LLC の商標です。その他、記載の会社名・製品名は各社の商標または登録商標です。本プロジェクトはそれらの権利を主張しません。


Upstream: [google/spatial-media](https://github.com/google/spatial-media)
以下はUpstreamのREADMEです。

---
# Spatial Media

A collection of specifications and tools for 360&deg; video and spatial audio, including:

- [Spatial Audio](docs/spatial-audio-rfc.md) metadata specification
- [Spherical Video](docs/spherical-video-rfc.md) metadata specification
- [Spherical Video V2](docs/spherical-video-v2-rfc.md) metadata specification
- [VR180 Video Format](docs/vr180.md) VR180 video format
- [Spatial Media tools](spatialmedia/) for injecting spatial media metadata in media files
