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

## MCP 最小構成（2ツール）
- エントリポイント: `mcp_server.py`
- ツール:
  - `inspect_spatial_metadata`（read-only）
  - `preview_metadata_settings`（read-only / dry-run）
- UI リソース: `ui://widget/spatial-metadata-viewer.html`（`mcp_ui/spatial_metadata_widget.html`）

### ローカル起動
```bash
./.venv/bin/python mcp_server.py
```
- エンドポイント: `http://127.0.0.1:8000/mcp/`

### ローカル検証（MCPクライアント例）
```bash
./.venv/bin/python - <<'PY'
import asyncio
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

async def main():
    async with streamablehttp_client("http://127.0.0.1:8000/mcp/") as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            print([t.name for t in (await session.list_tools()).tools])
            result = await session.call_tool("inspect_spatial_metadata", {
                "file_path": "data/testsrc_320x240_h264.mp4",
                "include_logs": False,
            })
            print(result.content[0].text)
            print((await session.read_resource("ui://widget/spatial-metadata-viewer.html")).contents[0].mimeType)

asyncio.run(main())
PY
```

### 自動検証スクリプト
```bash
./.venv/bin/python scripts/verify_mcp_apps.py
./scripts/verify_ignore_hygiene.sh
```

### MCP Inspector での確認
- Inspector で接続先を `http://127.0.0.1:8000/mcp/` に設定
- `inspect_spatial_metadata` を呼び出し、`_meta.ui.resourceUri` が `ui://widget/spatial-metadata-viewer.html` であることを確認
- `preview_metadata_settings` を呼び出し、`Preview only. No file is modified.` が返ることを確認
- `read_resource` で `text/html;profile=mcp-app` が返ることを確認
- CLI モード確認例: `npx @modelcontextprotocol/inspector --cli --transport http --server-url http://127.0.0.1:8000/mcp/`
- UI でツール選択を切り替え、`inspect` と `preview` の双方が `tools/call` できることを確認

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
