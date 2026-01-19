#!/usr/bin/env python3
"""Generate a minimal .docx template for portal posts.

We intentionally avoid external dependencies (like python-docx) so this works
in constrained environments.

The resulting file is suitable as a writing template:
- Use Title for the main title
- Use Heading 1/2 for section hierarchy
- Insert images inline (no floating/wrapping)

Output: docs/portal_article_template.docx
"""

from __future__ import annotations

import datetime
import os
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "portal_article_template.docx"


def _xml_escape(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _w_p(text: str, style: str | None = None) -> str:
    # Preserve line breaks by splitting into separate runs with <w:br/>
    parts = str(text).split("\n")
    runs = []
    for idx, part in enumerate(parts):
        if idx:
            runs.append("<w:r><w:br/></w:r>")
        if part:
            runs.append(
                "<w:r><w:t xml:space=\"preserve\">%s</w:t></w:r>" % _xml_escape(part)
            )
    r_xml = "".join(runs) if runs else "<w:r/>"
    if style:
        return (
            "<w:p><w:pPr><w:pStyle w:val=\"%s\"/></w:pPr>%s</w:p>" % (style, r_xml)
        )
    return "<w:p>%s</w:p>" % r_xml


def _doc_xml() -> str:
    # Use built-in style ids: Title, Heading1, Heading2, Normal
    now = datetime.datetime.now().strftime("%Y-%m-%d")

    body = []
    body.append(_w_p("信息门户文章 Word 模板", style="Title"))
    body.append(
        _w_p(
            "（使用说明）\n"
            "1. 大标题用『标题 1』（Heading 1）\n"
            "2. 小标题用『标题 2』（Heading 2）\n"
            "3. 正文用『正文』（Normal）\n"
            "4. 图片请『插入到段落中』，不要用环绕/浮动（手机端最稳）\n"
            "5. 文章尽量避免复杂表格；如必须用表格，先用简单 2-3 列\n"
            "6. 版式会由网页端统一排版：手机窄、电脑宽都会自适应\n"
            f"生成日期：{now}",
            style="Normal",
        )
    )

    body.append(_w_p("一、写作结构示例（大标题）", style="Heading1"))
    body.append(
        _w_p(
            "这里写一段引言/摘要（建议 2-4 行），用于让读者快速了解这篇文章。\n"
            "如果要发布到公众号，也建议在开头先把关键信息说清楚。",
            style="Normal",
        )
    )

    body.append(_w_p("1.1 小标题示例（适合要点/步骤）", style="Heading2"))
    body.append(
        _w_p(
            "- 要点 1：……\n"
            "- 要点 2：……\n"
            "- 要点 3：……\n\n"
            "（提示）Word 里可以用项目符号；导入时我们会尽量转换成网页的列表。",
            style="Normal",
        )
    )

    body.append(_w_p("1.2 图片示例（插入图片位置）", style="Heading2"))
    body.append(
        _w_p(
            "在下一行插入图片：\n"
            "【在此处插入图片】\n\n"
            "图片建议：宽图优先；文字密集的长截图建议拆成 2-3 张。",
            style="Normal",
        )
    )

    body.append(_w_p("二、常见格式建议（大标题）", style="Heading1"))
    body.append(
        _w_p(
            "1) 重要信息用『小标题』+ 短段落表达，不要堆在一段里。\n"
            "2) 手机端阅读：段落不宜过长，建议每段 2-5 行。\n"
            "3) 如果要公众号长图：我们后续会支持一键生成『手机宽度长图』。",
            style="Normal",
        )
    )

    # page break and append a second page with checklist
    body.append(
        "<w:p><w:r><w:br w:type=\"page\"/></w:r></w:p>"
    )
    body.append(_w_p("发布前检查清单", style="Heading1"))
    body.append(
        _w_p(
            "□ 标题已填写且不超过 30 字\n"
            "□ 有封面图（可选，但建议有）\n"
            "□ 有摘要（建议 40-80 字）\n"
            "□ 重点信息（时间/地点/对象/联系方式）清晰\n"
            "□ 图片清晰、方向正确、无多余空白\n"
            "□ 手机端预览已确认（后续会支持一键生成公众号长图）",
            style="Normal",
        )
    )

    # sectPr is required
    body.append(
        "<w:sectPr>"
        "<w:pgSz w:w=\"11906\" w:h=\"16838\"/>"  # A4 portrait in twips
        "<w:pgMar w:top=\"1440\" w:right=\"1440\" w:bottom=\"1440\" w:left=\"1440\" w:header=\"720\" w:footer=\"720\" w:gutter=\"0\"/>"
        "</w:sectPr>"
    )

    return (
        "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>"
        "<w:document xmlns:wpc=\"http://schemas.microsoft.com/office/word/2010/wordprocessingCanvas\" "
        "xmlns:mc=\"http://schemas.openxmlformats.org/markup-compatibility/2006\" "
        "xmlns:o=\"urn:schemas-microsoft-com:office:office\" "
        "xmlns:r=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships\" "
        "xmlns:m=\"http://schemas.openxmlformats.org/officeDocument/2006/math\" "
        "xmlns:v=\"urn:schemas-microsoft-com:vml\" "
        "xmlns:wp14=\"http://schemas.microsoft.com/office/word/2010/wordprocessingDrawing\" "
        "xmlns:wp=\"http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing\" "
        "xmlns:w10=\"urn:schemas-microsoft-com:office:word\" "
        "xmlns:w=\"http://schemas.openxmlformats.org/wordprocessingml/2006/main\" "
        "xmlns:w14=\"http://schemas.microsoft.com/office/word/2010/wordml\" "
        "xmlns:wpg=\"http://schemas.microsoft.com/office/word/2010/wordprocessingGroup\" "
        "xmlns:wpi=\"http://schemas.microsoft.com/office/word/2010/wordprocessingInk\" "
        "xmlns:wne=\"http://schemas.microsoft.com/office/word/2006/wordml\" "
        "xmlns:wps=\"http://schemas.microsoft.com/office/word/2010/wordprocessingShape\" "
        "mc:Ignorable=\"w14 wp14\">"
        "<w:body>"
        + "".join(body)
        + "</w:body></w:document>"
    )


def _content_types() -> str:
    return (
        "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>"
        "<Types xmlns=\"http://schemas.openxmlformats.org/package/2006/content-types\">"
        "<Default Extension=\"rels\" ContentType=\"application/vnd.openxmlformats-package.relationships+xml\"/>"
        "<Default Extension=\"xml\" ContentType=\"application/xml\"/>"
        "<Override PartName=\"/word/document.xml\" ContentType=\"application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml\"/>"
        "<Override PartName=\"/docProps/core.xml\" ContentType=\"application/vnd.openxmlformats-package.core-properties+xml\"/>"
        "<Override PartName=\"/docProps/app.xml\" ContentType=\"application/vnd.openxmlformats-officedocument.extended-properties+xml\"/>"
        "</Types>"
    )


def _rels() -> str:
    return (
        "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>"
        "<Relationships xmlns=\"http://schemas.openxmlformats.org/package/2006/relationships\">"
        "<Relationship Id=\"rId1\" Type=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument\" Target=\"word/document.xml\"/>"
        "<Relationship Id=\"rId2\" Type=\"http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties\" Target=\"docProps/core.xml\"/>"
        "<Relationship Id=\"rId3\" Type=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties\" Target=\"docProps/app.xml\"/>"
        "</Relationships>"
    )


def _doc_rels() -> str:
    return (
        "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>"
        "<Relationships xmlns=\"http://schemas.openxmlformats.org/package/2006/relationships\"></Relationships>"
    )


def _core_props() -> str:
    now = datetime.datetime.now(datetime.UTC).replace(microsecond=0).isoformat().replace('+00:00', 'Z')
    return (
        "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>"
        "<cp:coreProperties xmlns:cp=\"http://schemas.openxmlformats.org/package/2006/metadata/core-properties\" "
        "xmlns:dc=\"http://purl.org/dc/elements/1.1/\" "
        "xmlns:dcterms=\"http://purl.org/dc/terms/\" "
        "xmlns:dcmitype=\"http://purl.org/dc/dcmitype/\" "
        "xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\">"
        "<dc:title>信息门户文章模板</dc:title>"
        "<dc:subject>portal template</dc:subject>"
        "<dc:creator>润德后台</dc:creator>"
        "<cp:lastModifiedBy>润德后台</cp:lastModifiedBy>"
        f"<dcterms:created xsi:type=\"dcterms:W3CDTF\">{now}</dcterms:created>"
        f"<dcterms:modified xsi:type=\"dcterms:W3CDTF\">{now}</dcterms:modified>"
        "</cp:coreProperties>"
    )


def _app_props() -> str:
    return (
        "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>"
        "<Properties xmlns=\"http://schemas.openxmlformats.org/officeDocument/2006/extended-properties\" "
        "xmlns:vt=\"http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes\">"
        "<Application>润德后台</Application>"
        "</Properties>"
    )


def build(out: Path):
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists():
        out.unlink()

    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", _content_types())
        z.writestr("_rels/.rels", _rels())
        z.writestr("word/document.xml", _doc_xml())
        z.writestr("word/_rels/document.xml.rels", _doc_rels())
        z.writestr("docProps/core.xml", _core_props())
        z.writestr("docProps/app.xml", _app_props())


if __name__ == "__main__":
    build(OUT)
    print(str(OUT))
