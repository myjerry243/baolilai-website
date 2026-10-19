# -*- coding: utf-8 -*-
"""
Render one bilingual TDS PDF per product:  assets/tds/<CODE>_TDS.pdf
Page order: English (2 pp) then 中文 (2 pp). Text is real text, not an image,
so it is searchable and gets indexed by importers' document systems.

Run:  cd G:/baolilai-site && python tools/make_tds.py
"""
import os, sys, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from build_site import PRODUCTS, SERIES, CFG, L, hexof, nameof, series_of
from tds_data import TDS, PACK, SAFETY, ORDER, DISC, REV

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, Frame, PageTemplate, Paragraph,
                                Spacer, Table, TableStyle, PageBreak, KeepTogether)
from reportlab.pdfgen import canvas as pdfcanvas

INK   = colors.HexColor("#22312B")
MUTED = colors.HexColor("#5F6F66")
GREEN = colors.HexColor("#3F6149")
LINE  = colors.HexColor("#D8E0D8")
HEADBG= colors.HexColor("#EEF1EA")
SOFT  = colors.HexColor("#F7F8F4")

PAGE_W, PAGE_H = A4
MARGIN_X = 17 * mm
MARGIN_T = 21 * mm     # header band sits above this
MARGIN_B = 17 * mm
CONTENT_W = PAGE_W - 2 * MARGIN_X

OUTDIR = os.path.join(ROOT, "assets", "tds")

# ------------------------------------------------------------------ fonts
def register_fonts():
    base = "C:/Windows/Fonts/"
    pdfmetrics.registerFont(TTFont("MS", base + "msyh.ttc", subfontIndex=0))
    pdfmetrics.registerFont(TTFont("MSB", base + "msyhbd.ttc", subfontIndex=0))
    pdfmetrics.registerFontFamily("MS", normal="MS", bold="MSB", italic="MS", boldItalic="MSB")

ST = dict(
    name   = ParagraphStyle("name", fontName="MSB", fontSize=19, leading=23, textColor=INK, spaceAfter=1),
    sub    = ParagraphStyle("sub", fontName="MS", fontSize=10.5, leading=14, textColor=GREEN, spaceAfter=3),
    meta   = ParagraphStyle("meta", fontName="MS", fontSize=8.1, leading=11.2, textColor=MUTED),
    h2     = ParagraphStyle("h2", fontName="MSB", fontSize=9.6, leading=12, textColor=GREEN,
                            spaceBefore=9, spaceAfter=3.5),
    body   = ParagraphStyle("body", fontName="MS", fontSize=8.6, leading=12.3, textColor=INK,
                            alignment=TA_LEFT, spaceAfter=3),
    bodyS  = ParagraphStyle("bodyS", fontName="MS", fontSize=8.1, leading=11.6, textColor=INK, spaceAfter=2.4),
    small  = ParagraphStyle("small", fontName="MS", fontSize=7.4, leading=10.2, textColor=MUTED, spaceAfter=2.4),
    cell   = ParagraphStyle("cell", fontName="MS", fontSize=7.5, leading=9.9, textColor=INK),
    cellb  = ParagraphStyle("cellb", fontName="MSB", fontSize=7.5, leading=9.9, textColor=INK),
    cellh  = ParagraphStyle("cellh", fontName="MSB", fontSize=7.0, leading=9.2, textColor=MUTED),
    stepn  = ParagraphStyle("stepn", fontName="MSB", fontSize=8.4, leading=12.3, textColor=GREEN),
    swatch = ParagraphStyle("swatch", fontName="MS", fontSize=6.6, leading=8.6, textColor=INK),
    numS   = ParagraphStyle("numS", fontName="MS", fontSize=8.1, leading=11.6, textColor=INK,
                            leftIndent=9, firstLineIndent=-9, spaceAfter=2.4),
    numXS  = ParagraphStyle("numXS", fontName="MS", fontSize=7.4, leading=10.2, textColor=MUTED,
                            leftIndent=9, firstLineIndent=-9, spaceAfter=2.2),
)

def P(txt, st="cell"):
    return Paragraph(txt, ST[st])

def cov(sg, dft):
    theo = 1000.0 / (sg * dft)
    return theo, theo * 0.95

def f1(x):
    return ("%.1f" % x).replace(".", ",") if False else "%.1f" % x

# ------------------------------------------------------------------ number canvas
class NumberedCanvas(pdfcanvas.Canvas):
    """Adds 'page n of N' after the document knows its length."""
    def __init__(self, *a, **kw):
        pdfcanvas.Canvas.__init__(self, *a, **kw)
        self._saved = []
    def showPage(self):
        self._saved.append(dict(self.__dict__))
        self._startPage()
    def save(self):
        total = len(self._saved)
        for state in self._saved:
            self.__dict__.update(state)
            self._draw_pageno(total)
            pdfcanvas.Canvas.showPage(self)
        pdfcanvas.Canvas.save(self)
    def _draw_pageno(self, total):
        self.setFont("MS", 7.2)
        self.setFillColor(MUTED)
        self.drawRightString(PAGE_W - MARGIN_X, 10.5 * mm, "p. %d / %d" % (self._pageNumber, total))

# ------------------------------------------------------------------ header / footer
def chrome(lang, p, s):
    """Draw the header band and footer rule for one page."""
    code = p["code"]
    def draw(canv, doc):
        canv.saveState()
        # header band
        canv.setFillColor(GREEN)
        canv.rect(0, PAGE_H - 13 * mm, PAGE_W, 13 * mm, stroke=0, fill=1)
        canv.setFillColor(colors.white)
        canv.setFont("MSB", 10.5)
        canv.drawString(MARGIN_X, PAGE_H - 8.6 * mm, "Bao" )
        # two-tone wordmark without rich text
        w = canv.stringWidth("Bao", "MSB", 10.5)
        canv.setFont("MS", 10.5)
        canv.drawString(MARGIN_X + w, PAGE_H - 8.6 * mm, "lilai")
        canv.setFont("MS", 7.4)
        canv.setFillColor(colors.HexColor("#D9E4DA"))
        canv.drawString(MARGIN_X, PAGE_H - 11.4 * mm,
                        "Guangdong Baolilai Industrial Co., Ltd.  ·  Foshan, Guangdong, China")
        canv.setFillColor(colors.white)
        canv.setFont("MSB", 7.6)
        title = "TECHNICAL DATA SHEET" if lang == "en" else "技 术 数 据 表"
        canv.drawRightString(PAGE_W - MARGIN_X, PAGE_H - 7.2 * mm, title)
        canv.setFont("MS", 7.2)
        canv.setFillColor(colors.HexColor("#D9E4DA"))
        canv.drawRightString(PAGE_W - MARGIN_X, PAGE_H - 10.6 * mm,
                            "%s  ·  %s  ·  Rev. %s" % (code, L(lang, "English", "中文"), REV))
        # footer rule
        canv.setStrokeColor(LINE); canv.setLineWidth(0.5)
        canv.line(MARGIN_X, 14.5 * mm, PAGE_W - MARGIN_X, 14.5 * mm)
        canv.setFont("MS", 6.9); canv.setFillColor(MUTED)
        canv.drawString(MARGIN_X, 10.5 * mm,
            L(lang,
              "%s TDS · Rev. %s · typical values, not a certificate — see section 9" % (code, REV),
              "%s TDS · 版本 %s · 典型值，非证书——见第 9 节" % (code, REV)))
        canv.restoreState()
    return draw

# ------------------------------------------------------------------ blocks
def identity(lang, p, s):
    t = lambda en, cn: L(lang, en, cn)
    d = TDS[p["code"]]
    # colour swatch with a caption badge (a light swatch needs dark text on white)
    badge = Table([[P("%s · %s" % (p["ral"], nameof(lang, p["ral"])), "swatch")]])
    badge.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.white),
                               ("BOX", (0, 0), (-1, -1), 0.3, LINE),
                               ("TOPPADDING", (0, 0), (-1, -1), 1.4),
                               ("BOTTOMPADDING", (0, 0), (-1, -1), 1.8),
                               ("LEFTPADDING", (0, 0), (-1, -1), 3),
                               ("RIGHTPADDING", (0, 0), (-1, -1), 3)]))
    swatch = Table([[badge]], colWidths=[38 * mm], rowHeights=[18 * mm])
    swatch.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 0), colors.HexColor(hexof(p["ral"]))),
        ("BOX", (0, 0), (0, 0), 0.5, LINE),
        ("VALIGN", (0, 0), (0, 0), "BOTTOM"),
        ("ALIGN", (0, 0), (0, 0), "LEFT"),
        ("LEFTPADDING", (0, 0), (0, 0), 3),
        ("BOTTOMPADDING", (0, 0), (0, 0), 3),
    ]))
    head = Table(
        [[P(t("Product", "产品"), "cellh"), P(t("Code · series", "编号 · 系列"), "cellh"),
          P(t("Colour reference", "参照颜色"), "cellh"), P(t("Document", "文件"), "cellh")],
         [P("<b>%s</b><br/>%s" % (p["en"], p["cn"]), "cell"),
          P("%s<br/>%s %s" % (p["code"], s["code"], L(lang, s["en"], s["cn"])), "cell"),
          P("%s · %s" % (p["ral"], nameof(lang, p["ral"])), "cell"),
          P("TDS %s<br/>Rev. %s" % (p["code"], REV), "cell")]],
        colWidths=[38 * mm, 34 * mm, 34 * mm, CONTENT_W - 40 * mm - 106 * mm])
    head.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), HEADBG),
        ("GRID", (0, 0), (-1, -1), 0.4, LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 3.4), ("BOTTOMPADDING", (0, 0), (-1, -1), 3.6),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
    ]))
    row = Table([[swatch, head]], colWidths=[40 * mm, CONTENT_W - 40 * mm])
    row.setStyle(TableStyle([("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                             ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                             ("VALIGN", (0, 0), (-1, -1), "TOP")]))
    return [
        P(p["en"] if lang == "en" else p["cn"], "name"),
        P("%s · %s" % (d["family"][0 if lang == "en" else 1], p["ral"]), "sub"),
        row, Spacer(1, 5),
        P(d["pclass"][0 if lang == "en" else 1], "small"),
        P(t("1. Description", "1. 产品描述"), "h2"),
        P(d["intro"][0 if lang == "en" else 1], "body"),
    ]

def sec_props(lang, p, d):
    t = lambda en, cn: L(lang, en, cn)
    theo, plan = cov(d["sg_mid"], d["dft_mid"])
    if p["code"] == "BL-M103":
        cl_theo, _ = cov(1.50, 50)
        combo = 1.0 / (1.0 / theo + 1.0 / cl_theo)
        if lang == "en":
            cov_val = ("Base %.1f m²/kg theoretical; the base + clear pair covers %.1f m²/kg theoretical, "
                       "%.1f m²/kg at 95 %% utilisation (with reclaim)") % (theo, combo, combo * 0.95)
        else:
            cov_val = ("底粉理论 %.1f m²/kg；底粉+罩光两层理论 %.1f m²/kg，按 95%% 利用率（含回收）%.1f m²/kg"
                       % (theo, combo, combo * 0.95))
    else:
        if lang == "en":
            cov_val = "%.1f m²/kg at 100 %% film · %.1f m²/kg planning value at 95 %% utilisation (with reclaim)" % (theo, plan)
        else:
            cov_val = "100%% 成膜 %.1f m²/kg · 按 95%% 利用率（含回收）规划值 %.1f m²/kg" % (theo, plan)

    rows = [
        (t("Chemistry", "体系"), d["family"][0 if lang == "en" else 1], "—"),
        (t("Colour reference", "参照颜色"),
         t("%s %s — approval on a sprayed panel against a physical chip" % (p["ral"], nameof(lang, p["ral"])),
           "%s %s——以喷板对照实物色卡确认" % (p["ral"], nameof(lang, p["ral"]))), "RAL"),
        (t("Finish and gloss", "表面与光泽"), L(lang, p["gloss_en"], p["gloss_cn"]), "ASTM D523"),
        (t("Film build", "膜厚"), p["dft"], "ISO 2808"),
        (t("Density", "比重"), p["sg"] + " g/cm³", "ISO 8130-2/3"),
        (t("Coverage", "覆盖率"), cov_val, t("calculated", "计算值")),
        (t("Cure schedule", "固化条件"), p["cure"] + t(" (object temperature)", "（工件温度）"),
         t("object temp., not oven set point", "测工件温度，非炉膛设定")),
        (t("Particle size D50", "粒径 D50"), "30–45 µm", "ISO 8130-1 / -13"),
        (t("Stoving loss", "烘烤失重"), "≤ 1–2 %", "ISO 8130-7"),
        (t("Storage stability", "贮存稳定性"), t("1 month at 35–40 °C", "35–40 °C 下 1 个月"), "ISO 8130-8"),
    ]
    data = [[P(t("Property", "项目"), "cellh"), P(t("Value", "数值"), "cellh"), P(t("Method", "方法"), "cellh")]]
    for a, b, c in rows:
        data.append([P(a, "cellb"), P(b), P(c)])
    tb = Table(data, colWidths=[44 * mm, CONTENT_W - 44 * mm - 36 * mm, 36 * mm], repeatRows=1)
    tb.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), HEADBG),
        ("GRID", (0, 0), (-1, -1), 0.4, LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3.2),
        ("LEFTPADDING", (0, 0), (-1, -1), 4.5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, SOFT]),
    ]))
    return [P(t("2. Typical properties", "2. 典型性能"), "h2"), tb]

def sec_perf(lang, p, d):
    t = lambda en, cn: L(lang, en, cn)
    data = [[P(t("Test", "检测项目"), "cellh"), P(t("Method", "方法"), "cellh"),
             P(t("Typical result", "典型结果"), "cellh")]]
    for i, (en_t, cn_t, method, en_v, cn_v) in enumerate(d["perf"], 1):
        data.append([P(t("%d. %s" % (i, en_t), "%d. %s" % (i, cn_t)), "cellb"), P(method),
                     P(en_v if lang == "en" else cn_v)])
    tb = Table(data, colWidths=[44 * mm, 34 * mm, CONTENT_W - 78 * mm], repeatRows=1)
    tb.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), HEADBG),
        ("GRID", (0, 0), (-1, -1), 0.4, LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3.2),
        ("LEFTPADDING", (0, 0), (-1, -1), 4.5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, SOFT]),
    ]))
    foot = P(t("Measured to the method listed, on production batches or the third-party report held for this system. "
               "Not a certificate: acceptance values are fixed in the trial report and the purchase specification.",
               "按所列方法在量产批次或本体系所持第三方报告上测定。不是证书：验收值以试粉报告与采购规格为准。"), "small")
    return [P(t("3. Performance data", "3. 性能数据"), "h2"), tb, Spacer(1, 3), foot]

def sec_app(lang, p, d):
    t = lambda en, cn: L(lang, en, cn)
    out = [P(t("4. Application and cure", "4. 施工与固化"), "h2")]
    for i, (en_t, cn_t, en_b, cn_b) in enumerate(d["app"], 1):
        out.append(KeepTogether([
            Table([[P("%02d" % i, "stepn"), P("<b>%s</b>" % (en_t if lang == "en" else cn_t), "cellb")]],
                  colWidths=[9 * mm, CONTENT_W - 9 * mm],
                  style=TableStyle([("LEFTPADDING", (0, 0), (-1, -1), 0), ("TOPPADDING", (0, 0), (-1, -1), 2),
                                    ("BOTTOMPADDING", (0, 0), (-1, -1), 0.5), ("VALIGN", (0, 0), (-1, -1), "TOP")])),
            Paragraph(en_b if lang == "en" else cn_b, ST["bodyS"]),
        ]))
    return out

def sec_pack(lang, p, d):
    t = lambda en, cn: L(lang, en, cn)
    out = [P(t("5. Packaging, storage and ordering", "5. 包装、贮存与订货"), "h2")]
    for i, (en_b, cn_b) in enumerate(PACK + ORDER, 1):
        out.append(Paragraph("%d. %s" % (i, en_b if lang == "en" else cn_b), ST["numS"]))
    if p["code"] == "BL-L301":
        out.append(Paragraph(t("Low-cure note: this chemistry is more storage-sensitive than standard powder — keep packs sealed and cool, and re-check gel time after a month open.",
                               "低温型提示：该体系比标准粉更怕贮存——保持密封阴凉；开袋超过一个月要复测胶化时间。"), ST["small"]))
    return out

def sec_safety(lang, p, d):
    t = lambda en, cn: L(lang, en, cn)
    out = [P(t("6. Health and safety", "6. 健康与安全"), "h2")]
    for i, (en_b, cn_b) in enumerate(SAFETY, 1):
        out.append(Paragraph("%d. %s" % (i, en_b if lang == "en" else cn_b), ST["numS"]))
    return out

def sec_related(lang, p, d):
    """Cross-sell + document control. Fills the tail of page 2 with something useful."""
    t = lambda en, cn: L(lang, en, cn)
    sibs = [x for x in PRODUCTS if x["series"] == p["series"] and x["code"] != p["code"]]
    if not sibs:
        sibs = [x for x in PRODUCTS if x["code"] != p["code"]][:3]
    data = [[P(t("Code", "编号"), "cellh"), P(t("Product", "产品"), "cellh"),
             P(t("Colour", "颜色"), "cellh"), P(t("Film build", "膜厚"), "cellh"),
             P(t("Cure", "固化"), "cellh")]]
    for x in sibs:
        data.append([P(x["code"], "cellb"), P(L(lang, x["en"], x["cn"])), P(x["ral"]),
                     P(x["dft"]), P(x["cure"])])
    tb = Table(data, colWidths=[20 * mm, 52 * mm, 34 * mm, 26 * mm, CONTENT_W - 132 * mm], repeatRows=1)
    tb.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), HEADBG),
        ("GRID", (0, 0), (-1, -1), 0.4, LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 2.8), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 4.5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, SOFT]),
    ]))
    ctrl = Table(
        [[P(t("Sheet", "文件"), "cellh"), P(t("Revision", "版本"), "cellh"),
          P(t("Issued", "签发"), "cellh"), P(t("Supersedes", "替代版本"), "cellh"),
          P(t("Languages", "语言"), "cellh")],
         [P("%s TDS" % p["code"], "cellb"), P(REV), P(REV),
          P(t("None — first issue", "无——首版")), P(t("English + 中文 (4 pp.)", "英文 + 中文（共 4 页）"))]],
        colWidths=[40 * mm, 22 * mm, 22 * mm, CONTENT_W - 84 * mm - 32 * mm, 32 * mm])
    ctrl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), HEADBG),
        ("GRID", (0, 0), (-1, -1), 0.4, LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 2.8), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 4.5),
    ]))
    return [P(t("7. Also in this range", "7. 同系列其他产品"), "h2"), tb, Spacer(1, 6),
            P(t("8. Document control", "8. 文件控制"), "h2"), ctrl]

def sec_limits(lang, p, d):
    t = lambda en, cn: L(lang, en, cn)
    out = [P(t("9. Limits of this document", "9. 本文件的边界"), "h2")]
    out.append(Paragraph(t("What this product is not for:", "这款产品不适合用在："), ST["cellb"]))
    for en_b, cn_b in d["limits"]:
        out.append(Paragraph("— " + (en_b if lang == "en" else cn_b), ST["numS"]))
    out.append(Spacer(1, 3))
    for i, (en_b, cn_b) in enumerate(DISC, 1):
        out.append(Paragraph("%d. %s" % (i, en_b if lang == "en" else cn_b), ST["numXS"]))
    out.append(Spacer(1, 4))
    out.append(Paragraph(t(
        "Issued by %s · %s · %s<br/>Ask for: SDS · third-party test report · batch report · physical colour chip · sample in 3 days",
        "签发：%s · %s · %s<br/>可索取：SDS · 第三方检测报告 · 批次报告 · 实物色卡 · 3 天出样")
        % ((CFG["brand_full_en"] if lang == "en" else CFG["brand_full_cn"]),
           CFG["email"], CFG["phone"]), ST["small"]))
    return out

# ------------------------------------------------------------------ build one
def build_one(p, outdir=OUTDIR):
    d = TDS[p["code"]]
    s = series_of(p["series"])
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "%s_TDS.pdf" % p["code"].replace("/", "-"))
    doc = BaseDocTemplate(path, pagesize=A4,
                          leftMargin=MARGIN_X, rightMargin=MARGIN_X,
                          topMargin=MARGIN_T, bottomMargin=MARGIN_B,
                          title="%s %s — Technical Data Sheet (EN/中文)" % (p["code"], p["en"]),
                          author=CFG["brand_full_en"],
                          subject="Powder coating technical data sheet",
                          creator="Baolilai build_site.py / tools/make_tds.py")
    story = []
    for lang in ("en", "cn"):
        story += identity(lang, p, s)
        story += sec_props(lang, p, d)
        story += sec_perf(lang, p, d)
        story += sec_app(lang, p, d)
        story += sec_pack(lang, p, d)
        story += sec_safety(lang, p, d)
        story += sec_related(lang, p, d)
        story += sec_limits(lang, p, d)
        if lang == "en":
            story.append(PageBreak())
    # one template handles both languages; header text is drawn per page
    doc.pageTemplates = [PageTemplate(id="all", frames=[Frame(MARGIN_X, MARGIN_B, CONTENT_W,
                                                              PAGE_H - MARGIN_T - MARGIN_B, id="f")],
                                      onPage=dual_chrome(p, s))]
    doc.build(story, canvasmaker=NumberedCanvas)
    return path

def dual_chrome(p, s):
    """Header switches language by page number: pages 1–2 EN, 3+ 中文."""
    def draw(canv, doc):
        lang = "en" if doc.page <= 2 else "cn"
        chrome(lang, p, s)(canv, doc)
    return draw

# ------------------------------------------------------------------ build all
def build_all(verbose=True):
    register_fonts()
    paths = []
    for p in PRODUCTS:
        path = build_one(p)
        paths.append(path)
        if verbose:
            import fitz
            doc = fitz.open(path)
            txt = doc[0].get_text()
            ok = ("Technical" in txt or "TECHNICAL" in txt) and p["code"] in txt
            print("  %-8s %d pages  %6.1f KB  %s" % (
                p["code"], doc.page_count, os.path.getsize(path) / 1024.0,
                "OK" if ok else "!! header check failed"))
            doc.close()
    return paths

if __name__ == "__main__":
    print("TDS ->", OUTDIR)
    build_all()
