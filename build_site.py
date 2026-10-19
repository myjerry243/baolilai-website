# -*- coding: utf-8 -*-
"""
Baolilai powder coating — bilingual static site generator
EN at /  ·  CN at /cn/  ·  Colour cards use RAL codes + digital approximations
Run: python build_site.py
"""
import os, json, shutil, re
from datetime import date

OUT = r"G:/baolilai-site"
SRC = [
    (r"G:/Aluminium-Website/public/assets/facade.jpg", "application-facade.jpg", 1600),
    (r"G:/2026入户大门/2026PIVOTDOOR图册/2026PIVOTDOOR图册_28.jpg", "application-door.jpg", 1400),
]

CFG = {
    "brand": "Baolilai",
    "brand_full_en": "Guangdong Baolilai Industrial Co., Ltd.",
    "brand_full_cn": "广东宝利莱工业有限公司",
    "email": "jerry888.xu@gmail.com",
    "phone": "+86 188 2310 0890",
    "phone_raw": "+8618823100890",
    "whatsapp": "+86 188 2310 0890",
    "wa_raw": "8618823100890",
    "addr_en": "Sanshui District, Foshan, Guangdong, China",
    "addr_cn": "中国广东省佛山市三水区",
    "domain": "",   # set when the domain is live; canonical/sitemap are skipped until then
    "year": date.today().year,
}

# ------------------------------------------------------------------ RAL palette
# hex = digital approximation of the RAL chip, NOT an official sRGB definition.
COLORS = [
    dict(ral="RAL 9016", en="Traffic white", cn="交通白", hex="#F1F1EA", finish="smooth", series="BL-A", stock=True),
    dict(ral="RAL 9010", en="Pure white", cn="纯白", hex="#FFFFFF", finish="smooth", series="BL-L", stock=True),
    dict(ral="RAL 9018", en="Papyrus white", cn="纸莎白", hex="#CFD3CD", finish="smooth", series="BL-A", stock=True),
    dict(ral="RAL 7035", en="Light grey", cn="浅灰", hex="#C5C7C4", finish="sand", series="BL-A", stock=True),
    dict(ral="RAL 7037", en="Dusty grey", cn="灰土灰", hex="#7D7F7D", finish="sand", series="BL-I", stock=True),
    dict(ral="RAL 7016", en="Anthracite grey", cn="无烟煤灰", hex="#383E42", finish="sand", series="BL-A", stock=True),
    dict(ral="RAL 7021", en="Black grey", cn="黑灰", hex="#23282B", finish="matte", series="BL-I", stock=True),
    dict(ral="RAL 9005", en="Jet black", cn="墨黑", hex="#0A0A0A", finish="matte", series="BL-I", stock=True),
    dict(ral="RAL 9006", en="White aluminium", cn="白铝色", hex="#A5A5A5", finish="metallic", series="BL-M", stock=True),
    dict(ral="RAL 9007", en="Grey aluminium", cn="灰铝色", hex="#8F8F8C", finish="metallic", series="BL-M", stock=True),
    dict(ral="RAL 1036", en="Pearl gold", cn="珍珠金", hex="#8C7048", finish="metallic", series="BL-M", stock=True),
    dict(ral="RAL 1035", en="Pearl beige", cn="珍珠米", hex="#6A5D4D", finish="metallic", series="BL-M", stock=False),
    dict(ral="RAL 1015", en="Light ivory", cn="浅象牙", hex="#E6D2B5", finish="smooth", series="BL-A", stock=True),
    dict(ral="RAL 1013", en="Oyster white", cn="牡蛎白", hex="#DDD9C4", finish="smooth", series="BL-A", stock=True),
    dict(ral="RAL 1019", en="Grey beige", cn="灰米色", hex="#9E9764", finish="matte", series="BL-A", stock=False),
    dict(ral="RAL 1024", en="Ochre yellow", cn="赭黄", hex="#BA8F4C", finish="metallic", series="BL-M", stock=False),
    dict(ral="RAL 3020", en="Traffic red", cn="交通红", hex="#CC0605", finish="smooth", series="BL-A", stock=True),
    dict(ral="RAL 3003", en="Ruby red", cn="宝石红", hex="#8D1D2C", finish="smooth", series="BL-A", stock=False),
    dict(ral="RAL 2004", en="Pure orange", cn="纯橙", hex="#E25303", finish="smooth", series="BL-I", stock=False),
    dict(ral="RAL 5010", en="Gentian blue", cn="龙胆蓝", hex="#004F7C", finish="smooth", series="BL-A", stock=True),
    dict(ral="RAL 5012", en="Light blue", cn="浅蓝", hex="#3B83BD", finish="smooth", series="BL-I", stock=False),
    dict(ral="RAL 6005", en="Moss green", cn="苔藓绿", hex="#2F4538", finish="matte", series="BL-A", stock=False),
    dict(ral="RAL 8017", en="Chocolate brown", cn="巧克力棕", hex="#45322E", finish="sand", series="BL-I", stock=True),
    dict(ral="RAL 1023", en="Traffic yellow", cn="交通黄", hex="#F7B500", finish="smooth", series="BL-I", stock=False),
]
C = {c["ral"]: c for c in COLORS}

SERIES = [
    dict(code="BL-M", slug="series-bonded.html", en="Bonded Metallics", cn="邦定金属",
         tag_en="Signature", tag_cn="招牌工艺", ral="RAL 1036",
         blurb_en="Metal pigment bonded to the base powder — no separation, no stripes, reclaimable.",
         blurb_cn="金属颜料与基粉键合，不分离、不出条纹，回收粉可再用。"),
    dict(code="BL-A", slug="series-architectural.html", en="Architectural Polyester", cn="建筑户外聚酯",
         tag_en="Exterior", tag_cn="户外", ral="RAL 7035",
         blurb_en="Outdoor polyesters for aluminium profiles, façades and doors. Sand, matte and super-durable.",
         blurb_cn="铝型材、幕墙、门的户外聚酯：砂纹、哑光与超耐候。"),
    dict(code="BL-L", slug="series-lowtemp.html", en="Low-Temperature Cure", cn="低温固化",
         tag_en="130 °C", tag_cn="130 °C", ral="RAL 9010",
         blurb_en="Cures at 130 °C for MDF, thin-wall and heat-sensitive assemblies. Lower oven energy.",
         blurb_cn="130 °C 固化，适用 MDF、薄壁件与含塑组件，烘道能耗更低。"),
    dict(code="BL-I", slug="series-industrial.html", en="Industrial & Epoxy", cn="工业防腐环氧",
         tag_en="Protection", tag_cn="防腐", ral="RAL 7037",
         blurb_en="Pure epoxy and hybrid systems for pipes, valves, enclosures and shelving.",
         blurb_cn="纯环氧与混合型，用于管道、阀门、机柜与货架。"),
]

PRODUCTS = [
    dict(code="BL-M102", series="BL-M", ral="RAL 1036", en="Bonded Gold Sand", cn="邦定金砂",
         dft="70–90 µm", gloss_en="Sand, 8–15 @60°", gloss_cn="砂纹 8–15（60°）", sg="1.55–1.65",
         cure="200 °C × 10 min", app_en="Aluminium profiles, façade panels, appliances", app_cn="铝型材、幕墙板、家电",
         blurb_en="The look of anodised gold with the durability of powder. Bonded pigment survives handling, spraying and reclaim.",
         blurb_cn="阳极氧化金的观感，粉末涂料的耐久性。邦定颜料经得起搬运、喷涂与回收。"),
    dict(code="BL-M103", series="BL-M", ral="RAL 9006", en="Bonded Mirror Silver", cn="邦定镜面银",
         dft="60–80 µm + clear", gloss_en="90–100 @60°", gloss_cn="90–100（60°）", sg="1.6–1.8",
         cure="180–200 °C × 10–15 min", app_en="Lighting reflectors, hardware, decorative trim", app_cn="灯具反射罩、五金、装饰件",
         blurb_en="A chrome-like finish without electroplating: no heavy metals, no plating waste water. Requires a clear top coat.",
         blurb_cn="接近电镀铬的镜面，无重金属、无电镀废水。必须配套透明罩光。"),
    dict(code="BL-A201", series="BL-A", ral="RAL 7035", en="Outdoor Sand Grey", cn="户外砂纹灰",
         dft="60–80 µm", gloss_en="Sand, 5–12 @60°", gloss_cn="砂纹 5–12（60°）", sg="1.50–1.58",
         cure="200 °C × 10 min", app_en="Window systems, enclosures, shelving, guard rails", app_cn="门窗系统、机柜、货架、护栏",
         blurb_en="Texture hides substrate imperfections — less sanding, fewer rejects. TGIC and TGIC-free chemistry.",
         blurb_cn="纹理遮基材缺陷，省打磨、降返工。可做 TGIC 与 TGIC-free 两条路线。"),
    dict(code="BL-A202", series="BL-A", ral="RAL 1015", en="Super Durable Champagne", cn="超耐候香槟金",
         dft="70–90 µm", gloss_en="Matte, 30 ± 5 @60°", gloss_cn="哑光 30±5（60°）", sg="1.50–1.60",
         cure="200 °C × 12–15 min", app_en="Curtain wall, premium windows, coastal projects", app_cn="幕墙、高端门窗、沿海项目",
         blurb_en="Super-durable polyester with a high-performance light stabiliser package, tested to the AAMA 2604/2605 test methods.",
         blurb_cn="超耐候聚酯配高效光稳定体系，按 AAMA 2604/2605 测试项目送检。"),
    dict(code="BL-L301", series="BL-L", ral="RAL 9010", en="Low-Temp White 130 °C", cn="130 °C 低温白",
         dft="60–80 µm", gloss_en="30–80 @60°", gloss_cn="30–80（60°）", sg="1.45–1.55",
         cure="130 °C × 20 min", app_en="MDF furniture, composite doors, thin-wall parts", app_cn="MDF 家具、复合门、薄壁件",
         blurb_en="Cures at 130 °C so MDF edges stay clean and assemblies with plastic inserts survive the oven.",
         blurb_cn="130 °C 固化，MDF 不焦边，含塑料嵌件的组件也能过炉。"),
    dict(code="BL-I401", series="BL-I", ral="RAL 7037", en="Epoxy Anti-Corrosion Grey", cn="环氧防腐灰",
         dft="80–120 µm", gloss_en="20–90 @60°", gloss_cn="20–90（60°）", sg="1.45–1.60",
         cure="180–200 °C × 10–15 min", app_en="Pipes, valves, tanks, steel structures", app_cn="管道、阀门、储罐、钢结构",
         blurb_en="The strongest adhesion and corrosion package in the range. Indoor use only — epoxy chalks under UV.",
         blurb_cn="全系最强的附着与防腐组合。仅限室内，环氧在紫外下会粉化。"),
]

def L(lang, en, cn): return en if lang == "en" else cn
def hexof(ral): return C[ral]["hex"]
def nameof(lang, ral): return C[ral]["en"] if lang == "en" else C[ral]["cn"]
def series_of(code): return next(s for s in SERIES if s["code"] == code)

# ------------------------------------------------------------------ CSS / JS
CSS = r"""
:root{--bg:#f5f6f2;--surface:#fff;--text:#22312b;--muted:#5f6f66;--p200:#c9d4cc;--p300:#a8bfad;
--p400:#7c9a83;--p600:#41604c;--p700:#3f6149;--line:#dfe5dc;--dark:#2a3b31;--radius:3px;
--max:1280px;--pad:clamp(20px,5vw,64px)}
*{box-sizing:border-box}html{scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--text);font-family:"Archivo","PingFang SC","Microsoft YaHei",
"Helvetica Neue",-apple-system,"Segoe UI",Roboto,Arial,sans-serif;font-size:16.5px;line-height:1.72;-webkit-font-smoothing:antialiased}
img{max-width:100%;display:block}a{color:var(--p600);text-decoration:none}a:hover{color:var(--p700)}
h1,h2,h3,h4{margin:0 0 .5em;font-weight:300;letter-spacing:-.015em;line-height:1.2}
h1{font-size:clamp(34px,5.2vw,64px)}h2{font-size:clamp(26px,3.4vw,42px);color:var(--text)}
h3{font-size:clamp(19px,1.9vw,25px);font-weight:400}p{margin:0 0 1.1em;max-width:68ch}
.wrap{max-width:var(--max);margin:0 auto;padding:0 var(--pad)}
.eyebrow{font-size:11.5px;letter-spacing:.16em;text-transform:uppercase;color:var(--muted);margin-bottom:18px;display:block}
.lead{font-size:clamp(16.5px,1.5vw,19.5px);color:var(--muted);max-width:64ch}
.section{padding:clamp(60px,7.5vw,112px) 0}.section.tight{padding:clamp(42px,5vw,70px) 0}
.alt{background:var(--surface)}.dark{background:var(--dark);color:#fff}
.dark h2,.dark h3{color:#fff}.dark .lead,.dark .eyebrow{color:rgba(255,255,255,.72)}
.grid{display:grid;gap:clamp(16px,2.2vw,30px)}
.g2{grid-template-columns:repeat(2,1fr)}.g3{grid-template-columns:repeat(3,1fr)}.g4{grid-template-columns:repeat(4,1fr)}
.g6{grid-template-columns:repeat(6,1fr)}
.split{display:grid;grid-template-columns:1.05fr .95fr;gap:clamp(26px,5vw,70px);align-items:center}
@media(max-width:900px){.g4,.g6{grid-template-columns:repeat(2,1fr)}.g3{grid-template-columns:1fr}
.split{grid-template-columns:1fr}.g2{grid-template-columns:1fr}}
/* header */
.hdr{position:fixed;inset:0 0 auto;z-index:60;transition:background .35s,box-shadow .35s}
.hdr::before{content:"";position:absolute;inset:0;background:linear-gradient(180deg,rgba(245,246,242,.96),rgba(245,246,242,0));pointer-events:none;transition:opacity .35s}
.hdr.solid{background:rgba(245,246,242,.97);box-shadow:0 1px 0 var(--line);backdrop-filter:blur(8px)}
.hdr.solid::before{opacity:0}
.hdr .bar{max-width:var(--max);margin:0 auto;padding:15px var(--pad);display:flex;align-items:center;gap:22px}
.logo{font-size:19px;letter-spacing:.14em;text-transform:uppercase;color:var(--text);font-weight:500;white-space:nowrap}
.nav{margin-left:auto;display:flex;gap:17px;align-items:center}
.nav a{font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:var(--text);opacity:.86;white-space:nowrap}
.nav a:hover{opacity:1;color:var(--p700)}
.lang{display:flex;gap:6px;align-items:center;font-size:11.5px;letter-spacing:.08em;border-left:1px solid var(--line);padding-left:14px}
.lang a{opacity:.55}.lang a.on{opacity:1;font-weight:600;color:var(--p700)}
.btn{display:inline-flex;align-items:center;justify-content:center;height:50px;padding:0 26px;background:var(--p700);
color:#fff;border:0;border-radius:var(--radius);font-family:inherit;font-size:12.5px;letter-spacing:.1em;
text-transform:uppercase;cursor:pointer;transition:background .25s}
.btn:hover{background:#35543e;color:#fff}
.btn.ghost{background:transparent;color:var(--text);border:1px solid var(--p600)}
.btn.ghost:hover{background:var(--p600);color:#fff}
.btn.sm{height:34px;padding:0 13px;font-size:10.5px;letter-spacing:.07em}
.btn.on-dark{background:#fff;color:var(--dark)}.btn.on-dark:hover{background:#e8ece6;color:var(--dark)}
.hdr .btn{height:40px;padding:0 18px;font-size:11px}
@media(max-width:1080px){.nav{display:none}}
/* hero */
.hero{position:relative;min-height:min(86vh,760px);display:grid;align-items:end;overflow:hidden;background:#eef1ea}
.slide{position:absolute;inset:0;opacity:0;transition:opacity 1s ease}.slide.on{opacity:1}
.slide .fill{position:absolute;inset:0}
.slide .code{position:absolute;right:var(--pad);top:46%;font-size:11px;letter-spacing:.16em;text-transform:uppercase;color:rgba(34,49,43,.45)}
.hero::after{content:"";position:absolute;inset:0;background:linear-gradient(180deg,rgba(245,246,242,.93) 0%,rgba(245,246,242,.72) 40%,rgba(245,246,242,.95) 100%)}
.hero .inner{position:relative;z-index:3;padding:150px 0 clamp(44px,6vw,86px);max-width:940px}
.hero h1{font-weight:200;letter-spacing:-.02em}
.hero p{color:var(--muted);font-size:clamp(16px,1.6vw,19px);max-width:56ch}
.dots{display:flex;gap:9px;margin-top:30px}
.dot{width:34px;height:3px;background:rgba(34,49,43,.22);border:0;padding:0;cursor:pointer;transition:background .3s}
.dot.on{background:var(--p700)}
/* ticker */
.ticker{background:var(--dark);color:#fff;overflow:hidden}
.ticker .track{display:flex;gap:46px;width:max-content;padding:13px 0;animation:slide 40s linear infinite}
.ticker:hover .track{animation-play-state:paused}
.ticker span{font-size:11px;letter-spacing:.18em;text-transform:uppercase;color:rgba(255,255,255,.78);white-space:nowrap}
.ticker span::before{content:"—";margin-right:46px;color:rgba(255,255,255,.3)}
@keyframes slide{from{transform:translateX(0)}to{transform:translateX(-50%)}}
/* stats */
.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:1px;background:var(--line)}
.stat{background:var(--bg);padding:clamp(22px,3vw,40px)}
.stat b{display:block;font-size:clamp(28px,3.4vw,44px);font-weight:300;color:var(--p700)}
.stat small{display:block;margin-top:8px;font-size:11.5px;letter-spacing:.07em;text-transform:uppercase;color:var(--muted);line-height:1.6}
@media(max-width:820px){.stats{grid-template-columns:repeat(2,1fr)}}
/* cards */
.card{background:var(--surface);border:1px solid var(--line);display:flex;flex-direction:column;transition:transform .3s,border-color .3s}
.card:hover{transform:translateY(-3px);border-color:var(--p300)}
.card .sw{height:170px;position:relative;border-bottom:1px solid var(--line)}
.card .sw .rl{position:absolute;left:14px;bottom:12px;font-size:10.5px;letter-spacing:.12em;text-transform:uppercase;
  background:rgba(255,255,255,.86);color:#22312b;padding:4px 8px;border-radius:2px}
.card .body{padding:22px 24px 26px;display:flex;flex-direction:column;gap:9px;flex:1}
.card .kicker{font-size:11px;letter-spacing:.13em;text-transform:uppercase;color:var(--muted)}
.card h3{margin:0;font-weight:400}.card p{margin:0;font-size:14.5px;color:var(--muted);line-height:1.65}
.card .go{margin-top:auto;padding-top:14px;font-size:12px;letter-spacing:.09em;text-transform:uppercase;color:var(--p600)}
.card .go::after{content:" →"}
/* colour chips */
.chips{display:grid;grid-template-columns:repeat(4,1fr);gap:1px;background:var(--line);border:1px solid var(--line)}
.chip{background:var(--surface)}
.chip .box{height:120px;position:relative}
.chip .box span{position:absolute;left:10px;bottom:8px;font-size:10px;letter-spacing:.1em;padding:3px 6px;border-radius:2px;
  background:rgba(255,255,255,.85);color:#22312b}
.chip .meta{padding:12px 14px 16px}
.chip b{display:block;font-size:13.5px;font-weight:500}
.chip small{display:block;color:var(--muted);font-size:12px;margin-top:2px}
@media(max-width:900px){.chips{grid-template-columns:repeat(2,1fr)}}
/* table */
table{width:100%;border-collapse:collapse;font-size:14.5px}
th,td{text-align:left;padding:12px 13px;border-bottom:1px solid var(--line);vertical-align:top}
th{font-size:11px;letter-spacing:.09em;text-transform:uppercase;color:var(--muted);font-weight:500;background:rgba(201,212,204,.22)}
.scroll{overflow-x:auto}
/* figure */
.figure{border:1px solid var(--line);background:var(--surface)}
.figure img{width:100%;height:clamp(230px,36vw,440px);object-fit:cover}
.figure .ralswatch{height:clamp(230px,36vw,440px);display:flex;align-items:flex-end;padding:20px}
.figure .ralswatch span{background:rgba(255,255,255,.88);padding:6px 10px;font-size:11px;letter-spacing:.12em;text-transform:uppercase}
.figure figcaption{padding:13px 16px;font-size:11.5px;letter-spacing:.05em;color:var(--muted);text-transform:uppercase}
/* steps */
.steps{counter-reset:s}
.step{display:grid;grid-template-columns:60px 1fr;gap:22px;padding:26px 0;border-top:1px solid var(--line)}
.step:last-child{border-bottom:1px solid var(--line)}
.step .n{font-size:12px;letter-spacing:.1em;color:var(--p400);padding-top:5px}
.step .n::before{counter-increment:s;content:"0" counter(s)}
.step h3{margin:0 0 6px}.step p{margin:0;color:var(--muted)}
.strip{display:grid;grid-template-columns:repeat(6,1fr);gap:1px;background:var(--line)}
.strip div{background:var(--surface);padding:20px 16px;font-size:11.5px;letter-spacing:.07em;text-transform:uppercase;color:var(--muted)}
@media(max-width:820px){.strip{grid-template-columns:repeat(2,1fr)}}
/* form */
form{display:grid;gap:15px;max-width:720px}
.row{display:grid;grid-template-columns:1fr 1fr;gap:15px}
@media(max-width:640px){.row{grid-template-columns:1fr}}
label{font-size:11.5px;letter-spacing:.09em;text-transform:uppercase;color:var(--muted);display:block;margin-bottom:6px}
input,select,textarea{width:100%;padding:12px 13px;border:1px solid var(--line);background:var(--surface);
font-family:inherit;font-size:15px;color:var(--text);border-radius:2px}
input:focus,select:focus,textarea:focus{outline:2px solid var(--p300);outline-offset:1px}
.note{font-size:12.5px;color:var(--muted)}
.ok{display:none;padding:15px 17px;border:1px solid var(--p300);background:rgba(168,191,173,.16);font-size:14px}.ok.on{display:block}
/* footer */
footer{background:var(--dark);color:rgba(255,255,255,.78);padding:clamp(44px,6vw,76px) 0 26px;font-size:14px}
footer a{color:rgba(255,255,255,.86)}
.fgrid{display:grid;grid-template-columns:1.4fr 1fr 1fr 1fr;gap:30px}
footer h4{font-size:11.5px;letter-spacing:.13em;text-transform:uppercase;color:rgba(255,255,255,.5);margin-bottom:13px}
footer ul{list-style:none;padding:0;margin:0;display:grid;gap:8px}
.copy{border-top:1px solid rgba(255,255,255,.12);margin-top:40px;padding-top:20px;display:flex;justify-content:space-between;gap:14px;flex-wrap:wrap;font-size:12px;color:rgba(255,255,255,.5)}
@media(max-width:820px){.fgrid{grid-template-columns:1fr 1fr}}
.rv{opacity:0;transform:translateY(16px);transition:opacity .7s ease,transform .7s ease}.rv.in{opacity:1;transform:none}
@media(prefers-reduced-motion:reduce){.rv{opacity:1;transform:none;transition:none}.ticker .track{animation:none}html{scroll-behavior:auto}}
.wa{position:fixed;right:20px;bottom:20px;z-index:70;display:inline-flex;align-items:center;
background:var(--p700);color:#fff;padding:9px 15px;border-radius:999px;font-size:11.5px;letter-spacing:.08em;
text-transform:uppercase;box-shadow:0 6px 22px rgba(34,49,43,.28)}
.wa:hover{background:#35543e;color:#fff}
@media(max-width:640px){.wa{right:12px;bottom:12px;padding:9px 13px;font-size:11px}}
body{padding-bottom:0}
"""

JS = r"""
const hdr=document.querySelector('.hdr');
const onScroll=()=>hdr.classList.toggle('solid',window.scrollY>60);
onScroll();addEventListener('scroll',onScroll,{passive:true});
const slides=[...document.querySelectorAll('.slide')],dots=[...document.querySelectorAll('.dot')];
let idx=0,timer=null;
function go(i){idx=(i+slides.length)%slides.length;
  slides.forEach((s,n)=>s.classList.toggle('on',n===idx));
  dots.forEach((d,n)=>d.classList.toggle('on',n===idx));}
function start(){if(slides.length>1&&!matchMedia('(prefers-reduced-motion: reduce)').matches){timer=setInterval(()=>go(idx+1),6500);}}
dots.forEach((d,n)=>d.addEventListener('click',()=>{clearInterval(timer);go(n);start();}));start();
const io=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target);}}),{threshold:.14});
document.querySelectorAll('.rv').forEach(el=>io.observe(el));
setTimeout(()=>document.querySelectorAll('.rv:not(.in)').forEach(el=>el.classList.add('in')),2600);
const nums=[...document.querySelectorAll('[data-count]')];
const cio=new IntersectionObserver(es=>es.forEach(e=>{
  if(!e.isIntersecting)return;const el=e.target,target=+el.dataset.count;
  el.textContent='0';let t0=null;const dur=1100;
  const step=t=>{if(!t0)t0=t;const p=Math.min((t-t0)/dur,1);const v=target*(1-Math.pow(1-p,3));
    el.textContent=Math.round(v).toLocaleString('en-US');if(p<1)requestAnimationFrame(step);};
  requestAnimationFrame(step);cio.unobserve(el);
}),{threshold:.4});
nums.forEach(n=>cio.observe(n));
const f=document.querySelector('#inquiry');
if(f){f.addEventListener('submit',ev=>{ev.preventDefault();
  const d=new FormData(f),g=k=>(d.get(k)||'').toString().trim();
  const body=[`Name: ${g('name')}`,`Company: ${g('company')}`,`Email: ${g('email')}`,
    `Country: ${g('country')}`,`Substrate: ${g('substrate')}`,`Finish: ${g('finish')}`,
    `Volume: ${g('volume')}`,'',g('message')].join('\n');
  const to=f.dataset.email||'';
  if(to){location.href=`mailto:${to}?subject=${encodeURIComponent('Powder coating inquiry')}&body=${encodeURIComponent(body)}`;}
  const ok=document.querySelector('#formOk');ok.classList.add('on');
  ok.textContent=to?'Your email client should open with the inquiry filled in.':'Thank you. Please send the same details to the sales address listed in the footer.';
});}
"""

# ------------------------------------------------------------------ shared chrome
NAV = [
    ("products.html", "Products", "产品"),
    ("colors.html", "Colours", "色卡"),
    ("durability.html", "Durability", "耐候等级"),
    ("pvdf.html", "Liquid PVDF", "PVDF 液体漆"),
    ("applications.html", "Applications", "应用"),
    ("technology.html", "Technology", "技术"),
    ("quality.html", "Quality", "质量"),
    ("downloads.html", "Docs", "资料"),
    ("about.html", "Company", "公司"),
]

def head(lang, base, title, desc, canonical):
    alt = "cn/" if lang == "en" else "../"
    seo = ""
    if CFG["domain"]:
        en_url = f"{CFG['domain']}/{canonical.replace('cn/','')}"
        cn_url = f"{CFG['domain']}/cn/{canonical.replace('cn/','')}"
        seo = (f'<link rel="canonical" href="{CFG["domain"]}/{canonical}">\n'
               f'<link rel="alternate" hreflang="en" href="{en_url}">\n'
               f'<link rel="alternate" hreflang="zh-CN" href="{cn_url}">')
    nav = "".join(f'<a href="{u}">{L(lang,en,cn)}</a>' for u,en,cn in NAV)
    return f"""<!DOCTYPE html>
<html lang="{'en' if lang=='en' else 'zh-CN'}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
{seo}
<link rel="icon" href="{base}assets/favicon.svg">
<link rel="stylesheet" href="{base}assets/css/site.css">
</head>
<body>
<header class="hdr"><div class="bar">
  <a class="logo" href="index.html">Bao<b>lilai</b></a>
  <nav class="nav">{nav}</nav>
  <div class="lang">
    <a href="{'index.html' if lang=='en' else '../index.html'}" class="{'on' if lang=='en' else ''}">EN</a>
    <span style="opacity:.3">/</span>
    <a href="{'cn/index.html' if lang=='en' else 'index.html'}" class="{'on' if lang!='en' else ''}">中文</a>
  </div>
  <a class="btn" href="contact.html">{L(lang,'Request a quote','获取报价')}</a>
</div></header>
"""

def foot(lang, base):
    bf = CFG["brand_full_en"] if lang == "en" else CFG["brand_full_cn"]
    addr = CFG["addr_en"] if lang == "en" else CFG["addr_cn"]
    series = "".join(f'<li><a href="{s["slug"]}">{s["code"]} {L(lang,s["en"],s["cn"])}</a></li>' for s in SERIES)
    email = f'<li><a href="mailto:{CFG["email"]}">{CFG["email"]}</a></li>' if CFG["email"] else f'<li>{L(lang,"Email on request","邮箱见询盘表单")}</li>'
    phone = (f'<a href="tel:{CFG["phone_raw"]}">{CFG["phone"]}</a>' if CFG.get("phone_raw")
             else L(lang, "Direct line on request", "直线电话请询"))
    wa = (f'<a href="https://wa.me/{CFG["wa_raw"]}" target="_blank" rel="noopener">{CFG["whatsapp"]}</a>'
          if CFG.get("wa_raw") else L(lang, "on request", "请询"))
    return f"""
<footer><div class="wrap">
  <div class="fgrid">
    <div>
      <div class="logo" style="color:#fff;margin-bottom:12px">Bao<b>lilai</b></div>
      <p style="color:rgba(255,255,255,.68);max-width:34ch">{L(lang,
        'Powder coatings for metal. Bonded metallics, low-temperature cure and architectural polyester — made in Foshan, China.',
        '金属表面粉末涂料。邦定金属、低温固化与建筑户外聚酯，广东佛山制造。')}</p>
      <p style="color:rgba(255,255,255,.5);font-size:12.5px">{bf}<br>{addr}</p>
    </div>
    <div><h4>{L(lang,'Series','产品系列')}</h4><ul>{series}</ul></div>
    <div><h4>{L(lang,'Company','公司')}</h4><ul>
      <li><a href="about.html">{L(lang,'About','公司简介')}</a></li>
      <li><a href="colors.html">{L(lang,'Colour card','色卡')}</a></li>
      <li><a href="durability.html">{L(lang,'Durability classes','耐候等级')}</a></li>
      <li><a href="functional.html">{L(lang,'Functional coatings','功能性粉末')}</a></li>
      <li><a href="integrated.html">{L(lang,'Integrated finishing','一体化表面处理')}</a></li>
      <li><a href="pvdf.html">{L(lang,'PVDF liquid coatings','PVDF 液体涂料')}</a></li>
      <li><a href="automotive.html">{L(lang,'Automotive parts','汽车零部件')}</a></li>
      <li><a href="technology.html">{L(lang,'Technology','技术工艺')}</a></li>
      <li><a href="quality.html">{L(lang,'Quality &amp; testing','质量与检测')}</a></li>
      <li><a href="downloads.html">{L(lang,'TDS &amp; documents','TDS 与资料下载')}</a></li>
      <li><a href="contact.html">{L(lang,'Contact','联系我们')}</a></li>
    </ul></div>
    <div><h4>{L(lang,'Contact','联系方式')}</h4><ul>
      {email}<li>{phone}</li><li>WhatsApp: {wa}</li>
      <li>{L(lang,'Mon–Sat 08:30–18:00 (GMT+8)','周一至周六 08:30–18:00')}</li>
    </ul></div>
  </div>
  <div class="copy">
    <span>© {CFG['year']} {bf} {L(lang,'All rights reserved.','保留所有权利。')}</span>
    <span>{L(lang,'Powder coatings · Foshan, Guangdong, China','粉末涂料 · 广东佛山')}</span>
  </div>
</div></footer>
{('<a class="wa" href="https://wa.me/' + CFG['wa_raw'] + '" target="_blank" rel="noopener" aria-label="WhatsApp">WhatsApp</a>') if CFG.get('wa_raw') else ''}
<script src="{base}assets/js/site.js"></script>
</body></html>"""

def write_page(lang, base, subdir, fname, title, desc, body):
    out = os.path.join(OUT, subdir) if subdir else OUT
    os.makedirs(out, exist_ok=True)
    html = head(lang, base, title, desc, (subdir + "/" if subdir else "") + fname) + body + foot(lang, base)
    if fname == "contact.html":
        html = re.sub(r'<a class="wa"[^>]*>.*?</a>\n?', '', html, flags=re.S)
    with open(os.path.join(out, fname), "w", encoding="utf-8") as f:
        f.write(html)


def preview_chip(c):
    return ('<div style="background:' + c["hex"] + ';height:150px;position:relative">'
            '<span style="position:absolute;left:10px;bottom:8px;font-size:10px;'
            'background:rgba(255,255,255,.85);padding:3px 6px">' + c["ral"] + '</span></div>')

def color_chip(c, lang):
    stock = L(lang, "In stock", "常备") if c["stock"] else L(lang, "On request", "订做")
    return f"""<div class="chip">
      <div class="box" style="background:{c['hex']}"><span>{c['ral']}</span></div>
      <div class="meta"><b>{c['en'] if lang=='en' else c['cn']}</b>
      <small>{c['finish'].title()} · {c['series']} · {stock}</small></div></div>"""

def product_card(p, lang, base=""):
    s = series_of(p["series"])
    return f"""<article class="card rv">
      <div class="sw" style="background:{hexof(p['ral'])}"><span class="rl">{p['ral']} · {nameof(lang,p['ral'])}</span></div>
      <div class="body"><span class="kicker">{p['code']} · {s['code']} {L(lang,s['en'],s['cn'])}</span>
        <h3>{L(lang,p['en'],p['cn'])}</h3><p>{L(lang,p['blurb_en'],p['blurb_cn'])}</p>
        <a class="go" href="{s['slug']}">{L(lang,'View series','查看系列')}</a>
        <a class="go" style="padding-top:6px;opacity:.72" href="{base}assets/tds/{p['code']}_TDS.pdf" download>{L(lang,'TDS · PDF','TDS · PDF')}</a></div></article>"""

# ------------------------------------------------------------------ pages
def pg_index(lang, base, sub):
    t = lambda en, cn: L(lang, en, cn)
    slides = [("RAL 1036", 0.55), ("RAL 7035", 0.35), ("RAL 9006", 0.45)]
    sl = "".join(
        f'<div class="slide{" on" if i==0 else ""}"><div class="fill" style="background:linear-gradient(150deg,{hexof(r)} 0%,{hexof(r)} 55%,#ffffff 130%)"></div><span class="code">{r}</span></div>'
        for i,(r,_) in enumerate(slides))
    stats = [(18080, t("Tonnes per year capacity","年产能（吨）")), (7, t("Patents","专利")),
             (6, t("Core platforms","核心产品平台")), (3, t("Days to sample","出样天数"))]
    stat_html = "".join(f'<div class="stat"><b><span data-count="{v}">{v:,}</span></b><small>{lab}</small></div>' for v,lab in stats)
    cards = "".join(f"""<article class="card rv">
      <div class="sw" style="background:{hexof(s['ral'])}"><span class="rl">{s['ral']}</span></div>
      <div class="body"><span class="kicker">{s['code']} · {L(lang,s['tag_en'],s['tag_cn'])}</span>
      <h3>{L(lang,s['en'],s['cn'])}</h3><p>{L(lang,s['blurb_en'],s['blurb_cn'])}</p>
      <a class="go" href="{s['slug']}">{t('Explore','了解')}</a></div></article>""" for s in SERIES)
    body = f"""
<section class="hero">{sl}
  <div class="wrap inner">
    <span class="eyebrow">{t('Powder coatings · Foshan, China','金属粉末涂料 · 中国佛山')}</span>
    <h1>{t('Coatings engineered for metal — and for the line that applies them.','为金属而做，也为你的喷涂线而调。')}</h1>
    <p>{t('Bonded metallics, 130 °C low-temperature cure and architectural polyester. 18,080 tonnes a year of capacity, samples in three days, and a technical answer for every substrate you run.',
        '邦定金属、130 °C 低温固化、建筑户外聚酯。年产 18,080 吨，3 天出样板，每一种基材都给出技术答案，而不是一句“可以”。')}</p>
    <div style="display:flex;gap:14px;flex-wrap:wrap;margin-top:30px">
      <a class="btn" href="contact.html">{t('Request a quote','获取报价')}</a>
      <a class="btn ghost" href="colors.html">{t('See the colour card','查看色卡')}</a></div>
    <div class="dots"><button class="dot on" aria-label="RAL 1036"></button><button class="dot" aria-label="RAL 7035"></button><button class="dot" aria-label="RAL 9006"></button></div>
  </div>
</section>
<div class="ticker"><div class="track">{''.join(f'<span>{x}</span>' for x in [ 'RAL 9016','RAL 7035','RAL 1036','RAL 9006','RAL 7016','RAL 1015','TGIC-free','130 °C cure','ΔE ≤ 1.5','3-day sample']*2)}</div></div>
<section class="section tight"><div class="wrap stats">{stat_html}</div></section>

<section class="section"><div class="wrap">
  <span class="eyebrow">{t('The range','产品系列')}</span>
  <h2>{t('Four platforms, one supply chain.','四大平台，一条供应链。')}</h2>
  <p class="lead">{t('Start from the finish you need to sell. Each platform carries its own application notes, cure window and test data.','从你要卖的效果出发选型。每个平台都有对应的应用说明、固化窗口与检测数据。')}</p>
  <div class="grid g4" style="margin-top:42px">{cards}</div>
</div></section>

<section class="section alt"><div class="wrap split">
  <div><span class="eyebrow">{t('Signature technology','招牌工艺')}</span>
    <h2>{t('Bonded, not blended.','是邦定，不是干混。')}</h2>
    <p>{t('A dry-blended metallic separates in the box. By the time it reaches the gun the pigment-to-base ratio has drifted, and the part comes out striped.',
         '干混金属粉在箱里就会分层。到枪口时颜料与基粉的比例已经跑偏，喷出来就是条纹。')}</p>
    <p>{t('We bond the metallic pigment to the base particle. The ratio stays fixed through transport, spraying and reclaim — which is why a bonded finish can be reclaimed without a colour shift.',
         '我们把金属颜料键合到基粉颗粒上。运输、喷涂、回收全程比例不变——所以邦定粉的回收粉可以再用，色相不漂移。')}</p>
    <a class="btn ghost" href="series-bonded.html">{t('Bonded metallics in detail','邦定金属详解')}</a></div>
  <figure class="figure rv">
    <div class="ralswatch" style="background:{hexof('RAL 1036')}"><span>RAL 1036 · {nameof(lang,'RAL 1036')}</span></div>
    <figcaption>{t('Bonded gold — representative colour','邦定金 — 示意色（以实物色卡为准）')}</figcaption></figure>
</div></section>

<section class="section"><div class="wrap">
  <span class="eyebrow">{t('Applications','应用')}</span>
  <h2>{t('Where the coating has to survive.','涂层必须活下来的地方。')}</h2>
  <div class="grid g3" style="margin-top:38px">
    <figure class="figure rv"><img src="{base}assets/img/application-facade.jpg" alt="{t('Aluminium façade','铝幕墙')}" loading="eager" decoding="async" width="1600" height="1067"><figcaption>{t('Architectural aluminium','建筑铝型材')}</figcaption></figure>
    <figure class="figure rv"><img src="{base}assets/img/application-door.jpg" alt="{t('Coated aluminium door','喷涂铝门')}" loading="eager" decoding="async" width="1400" height="1153"><figcaption>{t('Doors &amp; entrance systems','门与入口系统')}</figcaption></figure>
    <div class="card rv"><div class="body"><span class="kicker">{t('Industrial','工业')}</span>
      <h3>{t('Enclosures, shelving, pipes','机柜、货架、管道')}</h3>
      <p>{t('Epoxy and hybrid systems where corrosion resistance matters more than the colour card.','防腐优先于色卡的场景，用环氧与混合型。')}</p>
      <a class="go" href="series-industrial.html">{t('Industrial series','工业系列')}</a></div></div>
  </div>
</div></section>

<section class="section alt"><div class="wrap">
  <span class="eyebrow">{t('Durability classes','耐候等级')}</span>
  <h2>{t('A number of years is only credible with a class behind it.','“保几年”只有挂上等级才可信。')}</h2>
  <p class="lead">{t('Three architectural platforms, each tied to a standard class and a test report rather than a promise.','三个建筑平台，各自绑定标准等级与检测报告，而不是一句承诺。')}</p>
  <div class="grid g3" style="margin-top:38px">
    <article class="card rv"><div class="body"><span class="kicker">P1000 · {t('tested to AAMA 2603','对标 AAMA 2603 送检')}</span>
      <h3>{t('Standard exterior','标准户外')}</h3><p>{t('Polyester for inland façades and window systems. Up to 10 years design life.','内陆幕墙与门窗用聚酯，设计年限 10 年。')}</p>
      <a class="go" href="durability.html">{t('Compare classes','对比等级')}</a></div></article>
    <article class="card rv"><div class="body"><span class="kicker">P1500 · {t('tested to AAMA 2604','对标 AAMA 2604 送检')}</span>
      <h3>{t('Super-durable','超耐候')}</h3><p>{t('Higher-grade polyester for curtain wall, coastal and high-UV work. Up to 15 years.','高等级聚酯，用于幕墙、沿海与强紫外环境，最高 15 年。')}</p>
      <a class="go" href="durability.html">{t('Compare classes','对比等级')}</a></div></article>
    <article class="card rv"><div class="body"><span class="kicker">P2000 · {t('tested to AAMA 2605','对标 AAMA 2605 送检')}</span>
      <h3>{t('Fluorocarbon','氟碳')}</h3><p>{t('The top exterior class: landmarks, airports, extreme salt and sun. Up to 20 years.','户外最高等级：地标、机场、极端盐雾与紫外，最高 20 年。')}</p>
      <a class="go" href="durability.html">{t('Compare classes','对比等级')}</a></div></article>
  </div>
  <p class="note" style="margin-top:22px">{t('Need the liquid fluorocarbon route for Class-A panels? See the PVDF line.','可见平板需要液体氟碳路线？见 PVDF 液体漆页。')} <a href="pvdf.html">{t('PVDF liquid coatings →','PVDF 液体涂料 →')}</a></p>
</div></section>

<section class="section"><div class="wrap">
  <span class="eyebrow">{t('Inside the plant','工厂实景')}</span>
  <h2>{t('Not a stock photo.','不是图库照片。')}</h2>
  <div class="grid g3" style="margin-top:34px">
    <figure class="figure rv"><img src="{base}assets/img/factory-line.jpg" alt="{t('Powder coating production line','粉末涂装生产线')}" loading="lazy" decoding="async"><figcaption>{t('Production line','生产线')}</figcaption></figure>
    <figure class="figure rv"><img src="{base}assets/img/factory-detail.jpg" alt="{t('Production line detail','产线细节')}" loading="lazy" decoding="async"><figcaption>{t('Equipment detail','设备细节')}</figcaption></figure>
    <figure class="figure rv"><img src="{base}assets/img/panel-ceiling.jpg" alt="{t('Coated panels','喷涂板材')}" loading="lazy" decoding="async"><figcaption>{t('Coated panels','喷涂成品')}</figcaption></figure>
  </div>
</div></section>

<section class="section alt"><div class="wrap split">
  <div><span class="eyebrow">{t('Beyond powder','不止粉末')}</span>
    <h2>{t('Pre-treatment, anodising chemistry and liquid PVDF.','前处理、阳极氧化药剂与 PVDF 液体漆。')}</h2>
    <p>{t('Coating failures usually start one step earlier. The group supplies the chemistry that runs before the powder — degreasing, silane/zirconium conversion, chrome-free passivation, anodising and sealing — so the film has something sound to sit on.',
         '涂层失效通常发生在前一步。集团供应粉末之前的所有药剂——脱脂、硅烷陶化、无铬钝化、阳极氧化与封孔——让膜层有一个可靠的基底。')}</p>
    <a class="btn ghost" href="integrated.html">{t('Integrated surface finishing','一体化表面处理')}</a></div>
  <figure class="figure"><img src="{base}assets/img/panel-close.jpg" alt="{t('Coated panel close-up','喷涂板特写')}" loading="lazy" decoding="async"><figcaption>{t('Coated panel — close-up','喷涂板特写')}</figcaption></figure>
</div></section>

<section class="section dark"><div class="wrap">
  <span class="eyebrow">{t('How we work','合作方式')}</span>
  <h2>{t('Sample, trial, then volume.','先样板，再试线，后上量。')}</h2>
  <div class="grid g3" style="margin-top:38px">
    <div><h3>{t('1 · Sample in 3 days','① 3 天出样板')}</h3><p class="lead">{t('Panels in the finish you asked for, with the TDS and the test data.','按你要的效果出板，随板给 TDS 与检测数据。')}</p></div>
    <div><h3>{t('2 · Trial on your line','② 上你的线上试')}</h3><p class="lead">{t('We send the powder, you run it, we write the trial report.','我们寄粉，你上线跑，我们出试粉报告。')}</p></div>
    <div><h3>{t('3 · Volume with a fixed spec','③ 定标后上量')}</h3><p class="lead">{t('Once signed off, the specification stops moving. Batch ΔE within 1.5.','签样后配方与指标不再变动，批次色差 ΔE ≤ 1.5。')}</p></div>
  </div>
  <a class="btn on-dark" style="margin-top:32px" href="contact.html">{t('Start with a sample','先要一块样板')}</a>
</div></section>"""
    write_page(lang, base, sub, "index.html",
        L(lang, "Baolilai — Powder Coatings for Metal | Bonded Metallics & Architectural",
                 "宝利莱 — 金属粉末涂料 | 邦定金属 · 建筑户外 · 低温固化"),
        L(lang, "Powder coating manufacturer in Foshan, China. Bonded metallic, architectural polyester, 130 °C low-temperature cure and epoxy systems. 18,080 t/yr, samples in 3 days.",
                 "佛山粉末涂料工厂：邦定金属、建筑户外聚酯、130℃低温固化、环氧防腐。年产 18,080 吨，3 天出样板。"), body)

def pg_colors(lang, base, sub):
    t = lambda en, cn: L(lang, en, cn)
    chips = "".join(color_chip(c, lang) for c in COLORS)
    rows = "".join(
        f"<tr><td><b>{s['code']}</b></td><td>{L(lang,s['en'],s['cn'])}</td>"
        f"<td>{', '.join(c['ral'] for c in COLORS if c['series']==s['code'])}</td></tr>" for s in SERIES)
    body = f"""
<section class="section" style="padding-top:150px"><div class="wrap">
  <span class="eyebrow">{t('Colour card','色卡')}</span>
  <h1 style="font-size:clamp(30px,4.2vw,50px)">{t('RAL references, so the colour is not an opinion.','用 RAL 编号说话，颜色不是“感觉差不多”。')}</h1>
  <p class="lead">{t('Every finish is quoted against a RAL reference. The digital values below are approximations for screen reference only — approval is made on a sprayed panel against a physical RAL chip.',
      '所有颜色都按 RAL 编号报价。下方屏幕色仅为近似示意，最终以实物 RAL 色卡和我方喷板签样为准。')}</p>
</div></section>

<section class="section tight"><div class="wrap">
  <div class="chips">{chips}</div>
  <p class="note" style="margin-top:18px">{t('Hex values approximate the RAL chip on an sRGB screen and will differ between displays. RAL is a trademark of RAL gGmbH; colour names are used for reference only.',
      '此处 HEX 为 RAL 色卡在 sRGB 屏幕上的近似值，不同显示器会有差异。RAL 为 RAL gGmbH 的商标，色名仅作引用。')}</p>
</div></section>

<section class="section alt"><div class="wrap">
  <span class="eyebrow">{t('Coverage by series','系列色域')}</span>
  <h2>{t('Which references sit in which platform.','哪个系列覆盖哪些编号。')}</h2>
  <div class="scroll" style="margin-top:30px"><table>
    <thead><tr><th>{t('Series','系列')}</th><th>{t('Platform','平台')}</th><th>{t('Typical RAL references','常用 RAL 编号')}</th></tr></thead>
    <tbody>{rows}</tbody></table></div>
</div></section>

<section class="section"><div class="wrap split">
  <div><span class="eyebrow">{t('Custom colour','定制色')}</span>
    <h2>{t('Send a chip, get a panel.','寄色卡，回喷板。')}</h2>
    <p>{t('Standard references in stock ship in 3–5 days. A custom match takes 7–12 days and is approved on a sprayed panel — never on a monitor.','常备色 3–5 天发货；定制色 7–12 天，且以喷板签样，不以屏幕确认。')}</p>
    <ul style="color:var(--muted);padding-left:20px">
      <li>{t('Batch-to-batch ΔE within 1.5','批次间 ΔE ≤ 1.5')}</li>
      <li>{t('Sample retained for 12 months','留样 12 个月')}</li>
      <li>{t('Gloss: matte / semi / high, per reference','光泽：哑光/半光/高光，按编号指定')}</li>
    </ul>
    <a class="btn" href="contact.html">{t('Request a colour match','申请配色')}</a></div>
  <div class="grid g2" style="gap:1px;background:var(--line)">
    {''.join(preview_chip(c) for c in COLORS[:4])}
  </div>
</div></section>"""
    write_page(lang, base, sub, "colors.html",
        L(lang, "RAL Colour Card — Powder Coating Colours | Baolilai", "RAL 色卡 — 粉末涂料颜色 | 宝利莱"),
        L(lang, "RAL colour references for powder coating: 24 standard colours with finish type, series and stock status. Custom matching against a physical chip.",
                 "粉末涂料 RAL 色卡：24 个标准颜色，标注表面效果、所属系列与常备/订做状态，支持实物色卡配色。"), body)

def pg_products(lang, base, sub):
    t = lambda en, cn: L(lang, en, cn)
    cards = "".join(product_card(p, lang, base) for p in PRODUCTS)
    rows = "".join(f"<tr><td><b>{p['code']}</b></td><td>{L(lang,p['en'],p['cn'])}</td><td>{p['ral']}</td>"
                   f"<td>{p['dft']}</td><td>{L(lang,p['gloss_en'],p['gloss_cn'])}</td><td>{p['sg']}</td><td>{p['cure']}</td></tr>" for p in PRODUCTS)
    body = f"""
<section class="section" style="padding-top:150px"><div class="wrap">
  <span class="eyebrow">{t('Product range','产品')}</span>
  <h1 style="font-size:clamp(30px,4.2vw,50px)">{t('Six platforms that cover most metal finishing lines.','六个平台，覆盖多数金属喷涂线。')}</h1>
  <p class="lead">{t('Each product carries a fixed specification, a cure window, a RAL reference colour and a test sheet. Anything outside the list follows the same custom route.',
      '每个产品都有固定规格、固化窗口、RAL 参照色和检测表。清单之外的，走同一套定制流程。')}</p>
  <div class="grid g3" style="margin-top:48px">{cards}</div>
</div></section>
<section class="section alt"><div class="wrap">
  <span class="eyebrow">{t('Specification summary','规格一览')}</span>
  <h2>{t('Compare in one table.','一张表比完。')}</h2>
  <div class="scroll" style="margin-top:30px"><table>
    <thead><tr><th>{t('Code','编号')}</th><th>{t('Product','产品')}</th><th>RAL</th><th>{t('Film build','膜厚')}</th><th>{t('Gloss @60°','光泽 60°')}</th><th>{t('Density','比重')}</th><th>{t('Cure','固化')}</th></tr></thead>
    <tbody>{rows}</tbody></table></div>
  <p class="note" style="margin-top:16px">{t('Typical values. Acceptance values are fixed on the trial report and the purchase specification.','为典型值。验收值以试粉报告与采购规格为准。')}</p>
  <div style="display:flex;gap:14px;flex-wrap:wrap;margin-top:26px">
    <a class="btn" href="downloads.html">{t('Download all six TDS','下载全部六份 TDS')}</a>
    <a class="btn ghost" href="quality.html">{t('What we test, and what we do not hold','我们测什么、不持有什么')}</a>
  </div>
</div></section>

<section class="section"><div class="wrap">
  <span class="eyebrow">{t('Surface &amp; gloss','表面与光泽')}</span>
  <h2>{t('Finish is a specification, not a mood.','表面效果是规格，不是感觉。')}</h2>
  <div class="grid g4" style="margin-top:34px">
    <div><h3>{t('Texture','纹理')}</h3><p class="lead">{t('Smooth · sand · hammer · wrinkle · orange peel · leather','平面 · 砂纹 · 锤纹 · 皱纹 · 桔纹 · 皮革纹')}</p></div>
    <div><h3>{t('Gloss @60°','光泽 60°')}</h3><p class="lead">{t('High 80–95 · semi 50–70 · matte 5–30 · dead matte below 5','高光 80–95 · 半光 50–70 · 哑光 5–30 · 全哑 5 以下')}</p></div>
    <div><h3>{t('Effect','效果')}</h3><p class="lead">{t('Bonded metallic · 3D metallic · pearl · anodised look · mirror chrome','邦定金属 · 3D 金属 · 珠光 · 阳极氧化效果 · 镜面铬')}</p></div>
    <div><h3>{t('Wood grain','木纹')}</h3><p class="lead">{t('PU transfer base, high definition, exterior durable','聚氨酯转印底粉，清晰度高，户外耐候')}</p></div>
  </div>
  <a class="btn ghost" style="margin-top:26px" href="colors.html">{t('Open the colour card','打开色卡')}</a>
</div></section>"""
    write_page(lang, base, sub, "products.html",
        L(lang, "Products — Powder Coating Platforms | Baolilai", "产品 — 粉末涂料平台 | 宝利莱"),
        L(lang, "Six powder coating platforms with RAL reference colours, film build, gloss, density and cure windows.",
                 "六大粉末涂料平台，含 RAL 参照色、膜厚、光泽、比重与固化条件。"), body)

def spec_table(lang, rows):
    return ('<div class="scroll"><table><thead><tr><th>' + L(lang,"Property","项目") +
            '</th><th>' + L(lang,"Value","数值") + '</th><th>' + L(lang,"Method","方法") +
            '</th></tr></thead><tbody>' +
            "".join(f"<tr><td>{a}</td><td><b>{b}</b></td><td>{c}</td></tr>" for a,b,c in rows) + "</tbody></table></div>")

def pg_series(lang, base, sub, s, products, intro, extra_head, extra_table, faq):
    t = lambda en, cn: L(lang, en, cn)
    cards = "".join(product_card(p, lang, base) for p in products)
    faq_html = "".join(f"<div class='step'><div class='n'></div><div><h3>{q}</h3><p>{a}</p></div></div>" for q,a in faq)
    body = f"""
<section class="section" style="padding-top:150px"><div class="wrap">
  <span class="eyebrow">{s['code']} · {L(lang,s['tag_en'],s['tag_cn'])}</span>
  <h1 style="font-size:clamp(30px,4.4vw,54px)">{L(lang,s['en'],s['cn'])}</h1>
  <p class="lead">{L(lang,intro[0],intro[1])}</p>
  <div class="grid g2" style="margin-top:48px">{cards}</div>
</div></section>
<section class="section alt"><div class="wrap">{L(lang,extra_head[0],extra_head[1]).replace('@BASE@', base)}<h3 style="margin-top:46px">{t('Typical values','典型值')}</h3>{spec_table(lang,extra_table)}</div></section>
<section class="section"><div class="wrap">
  <span class="eyebrow">{t('Questions we actually get','客户真会问的问题')}</span>
  <h2>{t('Straight answers.','直接回答。')}</h2>
  <div class="steps" style="margin-top:30px">{faq_html}</div>
</div></section>
<section class="section tight dark"><div class="wrap" style="display:flex;justify-content:space-between;align-items:center;gap:22px;flex-wrap:wrap">
  <h2 style="margin:0">{t('Want a panel in this finish?','想要一块这个效果的样板？')}</h2>
  <a class="btn on-dark" href="contact.html">{t('Request a sample','申请样板')}</a>
</div></section>"""
    write_page(lang, base, sub, s["slug"], f"{s['code']} {L(lang,s['en'],s['cn'])} | Baolilai", s["blurb_en"] if lang=="en" else s["blurb_cn"], body)

def pg_applications(lang, base, sub):
    t = lambda en, cn: L(lang, en, cn)
    items = [
        ("01", t("Architectural aluminium","建筑铝型材"), t("Profiles, façade panels, window systems","型材、幕墙板、门窗系统"),
         t("Exterior polyester, sand texture and super-durable matte. The critical variables are pre-treatment, film build on complex profiles and colour control across batches.",
           "户外聚酯、砂纹与超耐候哑光。关键变量是前处理、复杂截面的膜厚均匀性和批次色控。"),
         "BL-A201 · BL-A202 · BL-M102", "assets/img/application-facade.jpg", t("Application reference","应用参考图")),
        ("02", t("Doors & entrance systems","门与入口系统"), t("Where colour accuracy is the sale","颜色准不准就是卖点"),
         t("Entrance doors are sold on appearance, which makes ΔE, gloss and texture repeatability commercial issues rather than technical footnotes.",
           "入户门靠外观成交，ΔE、光泽与纹理的重复性因此是生意问题，不是技术脚注。"),
         "BL-M102 · BL-A202 · BL-M103", "assets/img/application-door.jpg", t("Application reference","应用参考图")),
        ("03", t("Appliances","家电"), t("Hardness, detergent, line speed","硬度、耐洗涤剂、线速"),
         t("White goods need 2H hardness, detergent resistance and a cure window that matches a fast line. Year-round colour consistency matters more than any single test.",
           "白电需要 2H 硬度、耐洗涤剂，以及与快线匹配的固化窗口。全年颜色一致比单项测试更重要。"),
         "BL-A201 · BL-I401", None, None),
        ("04", t("Shelving & enclosures","货架与机柜"), t("Cost per square metre, not per kilo","算每平米，不算每公斤"),
         t("For high-volume, low-margin parts the decision is coverage and first-pass transfer efficiency. A sand texture that covers a scratched substrate beats a cheaper powder that needs rework.",
           "大批量低毛利件，看的是覆盖面积与一次上粉率。能盖住划伤基材的砂纹，胜过便宜但返工的粉。"),
         "BL-A201 · BL-I401", None, None),
        ("05", t("MDF & heat-sensitive parts","MDF 与热敏件"), t("130 °C changes the economics","130 °C 改变成本结构"),
         t("MDF, composites and assemblies with plastic inserts cannot survive a 190 °C oven. Low-temperature cure removes charring, edge sanding and part of the energy bill.",
           "MDF、复合材料、含塑料嵌件的组件过不了 190 °C。低温固化省掉焦边、打磨和一部分电费。"),
         "BL-L301", None, None),
        ("06", t("Pipes, valves & steel","管道、阀门与钢结构"), t("Corrosion first","防腐优先"),
         t("Epoxy at 100 µm plus a verified pre-treatment is still the most cost-effective corrosion barrier for pipe, valve and tank work.",
           "100 µm 环氧 + 可验证的前处理，仍是管道阀门储罐最划算的防腐方案。"),
         "BL-I401", None, None),
    ]
    cards = ""
    for num, title, sub_t, body_t, rec, img, cap in items:
        media = (f'<figure class="figure rv"><img src="{base}{img}" alt="{title}" loading="eager" decoding="async" width="1600" height="1067"><figcaption>{cap}</figcaption></figure>'
                 if img else f'<div class="figure rv"><div class="ralswatch" style="background:{hexof("RAL 7035" if num!="05" else "RAL 9010")}"><span>{"RAL 7035" if num!="05" else "RAL 9010"}</span></div><figcaption>{t("Colour reference","颜色参照")}</figcaption></div>')
        cards += f'<div class="rv"><span class="eyebrow">{num} · {sub_t}</span><h2 style="font-size:clamp(22px,2.4vw,30px)">{title}</h2><p>{body_t}</p><p class="note">{t("Recommended","推荐")}：{rec}</p></div>{media}'
    body = f"""
<section class="section" style="padding-top:150px"><div class="wrap">
  <span class="eyebrow">{t('Applications','应用')}</span>
  <h1 style="font-size:clamp(30px,4.2vw,50px)">{t('The finish is the last 80 microns of a long process.','涂层，是一条长工艺的最后 80 微米。')}</h1>
  <p class="lead">{t('Most coating failures we get called about are not powder failures. They are pre-treatment, grounding, oven profile or substrate problems that only show up at the coating stage.',
      '我们被叫去处理的涂层问题，多数不是粉末的问题，而是前处理、接地、炉温曲线或基材问题，只是到喷涂这道工序才暴露。')}</p>
</div></section>
<section class="section tight"><div class="wrap"><div class="grid g2">{cards}</div></div></section>
<section class="section alt"><div class="wrap">
  <span class="eyebrow">{t('Industries','行业')}</span>
  <h2>{t('Three industries that buy on repeat.','三个复购型行业。')}</h2>
  <div class="grid g3" style="margin-top:34px">
    <div><h3>{t('Appliances','家电')}</h3><p class="lead">{t('2H hardness, detergent resistance, colour consistency across a year of production. Hybrid and polyester systems, RAL whites and greys in stock.','2H 硬度、耐洗涤剂、全年颜色一致。混合型与聚酯体系，RAL 白与灰常备。')}</p></div>
    <div><h3>{t('Machinery &amp; equipment','机械制造')}</h3><p class="lead">{t('Sand texture that hides weld dressing and scratches, thick film on edges, fast cure on a busy line.','砂纹遮盖焊缝打磨痕与划伤，边角厚膜，快节奏产线可匹配固化。')}</p></div>
    <div><h3>{t('Outdoor furniture','户外家具')}</h3><p class="lead">{t('Exterior polyester with UV and moisture resistance, matte and textured finishes, wood-grain transfer.','户外聚酯，耐紫外耐潮湿，哑光与纹理效果，可做木纹转印。')}</p></div>
  </div>
  <p class="note" style="margin-top:22px"><a href="automotive.html">{t('Automotive parts have their own page →','汽车零部件有独立页面 →')}</a></p>
</div></section>

<section class="section dark"><div class="wrap" style="display:flex;justify-content:space-between;gap:22px;align-items:center;flex-wrap:wrap">
  <div><span class="eyebrow">{t('Next step','下一步')}</span><h2 style="margin:0">{t('Tell us the substrate and the finish.','告诉我们基材和想要的效果。')}</h2></div>
  <a class="btn on-dark" href="contact.html">{t('Request a quote','获取报价')}</a></div></section>"""
    write_page(lang, base, sub, "applications.html",
        L(lang,"Applications — Aluminium, Doors, Appliances, MDF, Pipes | Baolilai","应用 — 铝型材、门、家电、MDF、管道 | 宝利莱"),
        L(lang,"Powder coating applications across architectural aluminium, doors, appliances, shelving, MDF and steel.",
                 "粉末涂料应用：建筑铝型材、门、家电、货架、MDF 与钢结构。"), body)

def pg_technology(lang, base, sub):
    t = lambda en, cn: L(lang, en, cn)
    steps = [
        (t("Bonding — metallic effects that survive handling","邦定 — 经得起搬运的金属效果"),
         t("Metallic pigment is fixed onto the base particle instead of being dry-blended. The ratio stays constant through transport, spraying and reclaim.",
           "金属颜料被固定到基粉颗粒上，而非干混。运输、喷涂、回收全程比例不变。")),
        (t("Low-temperature extrusion — 130 °C without losing the film","低温挤出 — 130 °C 仍保住膜性能"),
         t("A dedicated extrusion route for low-cure chemistry. It opens MDF, thin-wall and heat-sensitive assemblies that a standard system would distort or char.",
           "为低温体系配置的独立挤出路线，让 MDF、薄壁件与热敏组件能上粉，而不被高温烤变形或焦边。")),
        (t("Ultrafine separation — the fraction you do not want","超细粉分离 — 去掉你不想要的那部分"),
         t("Particle size distribution drives transfer efficiency and surface quality. A cyclone separation system (patent CN223010819U) controls the fine fraction.",
           "粒径分布决定上粉率与表面质量。旋风分离装置（专利 CN223010819U）控制细粉比例。")),
        (t("Quality control — measured, not asserted","质量 — 测出来，不是说出来"),
         t("Gel time, particle size, film build, gloss, colour, adhesion, impact and salt spray are checked against the specification, with a retained sample for twelve months.",
           "胶化时间、粒径、膜厚、光泽、颜色、附着、冲击、盐雾逐项按规格检验，留样 12 个月。")),
    ]
    st = "".join(f'<div class="step rv"><div class="n"></div><div><h3>{a}</h3><p>{b}</p></div></div>' for a,b in steps)
    body = f"""
<section class="section" style="padding-top:150px"><div class="wrap">
  <span class="eyebrow">{t('Technology','技术工艺')}</span>
  <h1 style="font-size:clamp(30px,4.2vw,50px)">{t('Three process systems that decide the finish.','三套工艺，决定最终效果。')}</h1>
  <p class="lead">{t('Formulation is half the product. How the pigment is bonded, how the melt is extruded and how the fine fraction is separated decide whether a specification holds on a production line.',
      '配方只是产品的一半。颜料怎么键合、熔体怎么挤出、细粉怎么分离，决定这份规格能不能在产线上守住。')}</p>
</div></section>
<section class="section tight"><div class="wrap steps">{st}</div></section>
<section class="section alt"><div class="wrap">
  <span class="eyebrow">{t('Inside the plant','工厂内部')}</span>
  <h2>{t('What the process looks like.','工艺长什么样。')}</h2>
  <div class="strip" style="margin-top:32px">
    <div>{t('Weighing','配料')}</div><div>{t('Extrusion','挤出')}</div><div>{t('Flaking','压片破碎')}</div>
    <div>{t('Grinding','磨粉')}</div><div>{t('Classification','分级')}</div><div>{t('Packing','包装留样')}</div>
  </div>
  <p class="note" style="margin-top:22px">{t('Capacity 18,080 t/yr after the 2025 expansion · site 8,631 m² · building 9,477 m².',
      '2025 年改扩建后年产能 18,080 吨 · 占地 8,631 ㎡ · 建筑面积 9,477 ㎡。')}</p>
</div></section>
<section class="section"><div class="wrap">
  <span class="eyebrow">{t('How powder is made','粉末是怎么做出来的')}</span>
  <h2>{t('Seven steps from resin to a bag of powder.','从树脂到一袋粉，七道工序。')}</h2>
  <div class="strip" style="margin-top:32px">
    <div>{t('Weighing &amp; premix','配料预混')}</div><div>{t('Melt extrusion','熔融挤出')}</div><div>{t('Cooling &amp; flaking','冷却压片')}</div>
    <div>{t('Grinding','磨粉')}</div><div>{t('Sieving / classification','过筛分级')}</div><div>{t('Packing','包装留样')}</div>
  </div>
  <p class="note" style="margin-top:22px">{t('Particle size distribution is set at the sieving and classification stage — this is where transfer efficiency and surface quality are decided, not in the gun.','粒径分布是在过筛分级这道定下来的——上粉率与表面质量在这里决定，不在喷枪。')}</p>
</div></section>

<section class="section alt"><div class="wrap split">
  <div><span class="eyebrow">{t('Application principle','施工原理')}</span>
    <h2>{t('Corona charging, then a hot oven.','先电晕带电，再进炉熔融。')}</h2>
    <p>{t('Powder is fluidised by compressed air, pushed through a gun with a high-voltage electrode at the tip. Corona discharge charges the particles; the earthed workpiece pulls them in. The part then enters the oven, where the powder melts, flows and cures into a continuous film.',
         '粉末由压缩空气流化，经枪口高压电极电晕放电带电，被接地的工件吸附；随后进炉，粉末熔融、流平、固化成连续涂膜。')}</p>
    <p>{t('Typical settings: 60–90 kV, gun-to-part 150–250 mm, film build 60–90 µm in one pass. Overspray is recovered and blended back — total utilisation above 95%, against 40–60% for liquid paint.',
         '典型参数：60–90 kV、枪距 150–250 mm、一次上膜 60–90 µm。过喷粉回收掺用，总利用率 95% 以上，液体漆通常只有 40–60%。')}</p>
    <p class="note">{t('Why this matters commercially: the customer does not buy kilos, they buy square metres of finished part.','这在生意上的意义：客户买的不是公斤，是喷好的平方米。')}</p></div>
  <figure class="figure"><img src="{base}assets/img/factory-line.jpg" alt="{t('Powder coating line','粉末涂装线')}" loading="lazy" decoding="async"><figcaption>{t('Coating line','涂装线')}</figcaption></figure>
</div></section>

<section class="section"><div class="wrap">
  <span class="eyebrow">{t('Why powder','为什么用粉末')}</span>
  <h2>{t('Four advantages that survive an audit.','经得起审计的四个优势。')}</h2>
  <div class="grid g4" style="margin-top:34px">
    <div><h3>{t('No solvent','无溶剂')}</h3><p class="lead">{t('No VOC, no fire load in the store, no solvent odour at the line.','无 VOC、仓库无火灾负荷、产线无异味。')}</p></div>
    <div><h3>{t('High utilisation','高利用率')}</h3><p class="lead">{t('Overspray recovered; total utilisation above 95%.','过喷可回收，总利用率 95% 以上。')}</p></div>
    <div><h3>{t('Thick in one coat','一次厚涂')}</h3><p class="lead">{t('40–500 µm in a single pass without sagging.','一次可达 40–500 µm 且不流挂。')}</p></div>
    <div><h3>{t('Durable film','膜性能高')}</h3><p class="lead">{t('High-molecular-weight resins give better mechanical and chemical resistance.','树脂分子量高，机械与耐化学性能更好。')}</p></div>
  </div>
</div></section>

<section class="section"><div class="wrap split">
  <div><span class="eyebrow">{t('Test capability','检测能力')}</span><h2>{t('Numbers with methods attached.','带测试方法的数字。')}</h2>
    <p>{t('Every performance claim is tied to a method and a measured value. For accredited third-party reports we commission the test rather than presenting an internal number as a certificate.',
        '每一项性能都对应方法与实测值。需要权威第三方报告时，我们送检，而不是把内部数据当证书。')}</p>
    <a class="btn ghost" href="quality.html">{t('See the test matrix','查看测试矩阵')}</a></div>
  <figure class="figure"><div class="ralswatch" style="background:{hexof('RAL 7035')}"><span>RAL 7035 · {nameof(lang,'RAL 7035')}</span></div>
  <figcaption>{t('Sand texture reference','砂纹参照色')}</figcaption></figure>
</div></section>"""
    write_page(lang, base, sub, "technology.html",
        L(lang,"Technology — Bonding, Low-Temp Extrusion, Classification | Baolilai","技术工艺 — 邦定、低温挤出、超细分离 | 宝利莱"),
        L(lang,"Bonded metallic process, 130 °C low-temperature extrusion and ultrafine separation (patent CN223010819U).",
                 "邦定金属工艺、130 °C 低温挤出与超细粉分离（专利 CN223010819U）。"), body)

def pg_quality(lang, base, sub):
    t = lambda en, cn: L(lang, en, cn)
    rows = [
        (t("Particle size D50","粒径 D50"), "30–45 µm", "ISO 8130-1 / -13"),
        (t("Gel time (180 °C)","胶化时间（180 °C）"), "100–300 s", "ISO 8130-6"),
        (t("Loss on stoving","烘烤失重"), "≤ 1–2 %", "ISO 8130-7"),
        (t("Storage stability","贮存稳定性"), t("1 month at 35–40 °C","35–40 °C × 1 月"), "ISO 8130-8"),
        (t("Specific gravity","比重"), "1.45–1.70", "ISO 8130-2/3"),
        (t("Film build","膜厚"), "60–90 µm", "ISO 2808"),
        (t("Adhesion, cross-cut","附着力 划格"), "0–1", "ISO 2409 / ASTM D3359"),
        (t("Impact","冲击"), "50 kg·cm", "ASTM D2794"),
        (t("Pencil hardness","铅笔硬度"), "≥ H, 2H typical", "ASTM D3363"),
        (t("Gloss 60°","光泽 60°"), t("per specification ±5","按规格 ±5"), "ASTM D523"),
        (t("Colour difference","色差"), "ΔE ≤ 1.5", "ASTM D2244"),
        (t("Neutral salt spray","中性盐雾"), t("500 h standard, 1000 h on request","常规 500 h，可做 1000 h"), "ASTM B117 / ISO 9227"),
        (t("QUV","QUV 紫外"), t("500–2000 h by chemistry","按体系 500–2000 h"), "ASTM G154"),
        (t("Chemical resistance","耐化学"), t("per application","按应用"), "ASTM D1308"),
    ]
    body = f"""
<section class="section" style="padding-top:150px"><div class="wrap">
  <span class="eyebrow">{t('Quality & testing','质量与检测')}</span>
  <h1 style="font-size:clamp(30px,4.2vw,50px)">{t('Claims with a method behind them.','每个说法都有方法支撑。')}</h1>
  <p class="lead">{t('A performance number without a test method cannot be accepted, audited or claimed against. This is the matrix we work to, and the matrix we send with a quotation.',
      '没有测试方法的性能数字，无法验收、无法审计、也无法索赔。这是我们执行的矩阵，也是随报价单一起发出的矩阵。')}</p>
  <div style="margin-top:40px">{spec_table(lang,rows)}</div>
</div></section>

<section class="section tight alt"><div class="wrap">
  <span class="eyebrow">{t('Fluorocarbon system — AAMA 2605 test items','氟碳体系 — AAMA 2605 测试项')}</span>
  <h2 style="font-size:clamp(22px,2.6vw,32px)">{t('Measured, with the limit next to it.','实测值，旁边就是标准限值。')}</h2>
  <div class="scroll" style="margin-top:26px"><table>
    <thead><tr><th>{t('Test','项目')}</th><th>{t('AAMA 2605 limit','AAMA 2605 限值')}</th><th>{t('Measured','实测')}</th><th>{t('Method','方法')}</th></tr></thead>
    <tbody>
      <tr><td>{t('Gloss 60°','光泽 60°')}</td><td>19–80 by class</td><td><b>25–35</b></td><td>ASTM D523</td></tr>
      <tr><td>{t('Pencil hardness','铅笔硬度')}</td><td>F min</td><td><b>H</b></td><td>ASTM D3363</td></tr>
      <tr><td>{t('Adhesion','附着力')}</td><td>100/100</td><td><b>100/100</b></td><td>1 mm cross-cut</td></tr>
      <tr><td>{t('Boiling water 20 min','沸水 20 分钟')}</td><td>100/100</td><td><b>100/100</b></td><td>99–100 °C</td></tr>
      <tr><td>{t('Impact','冲击')}</td><td>{t('No loss','无脱落')}</td><td><b>{t('No loss','无脱落')}</b></td><td>Gardner 16 mm</td></tr>
      <tr><td>{t('Abrasion','耐磨')}</td><td>40 min</td><td><b>65 min</b></td><td>ASTM D968</td></tr>
      <tr><td>{t('Acid resistance','耐酸')}</td><td>{t('No change','无变化')}</td><td><b>{t('No change','无变化')}</b></td><td>10% HCl, 15 min</td></tr>
      <tr><td>{t('Mortar resistance','耐砂浆')}</td><td>{t('No change','无变化')}</td><td><b>{t('No change','无变化')}</b></td><td>24 h</td></tr>
      <tr><td>{t('Nitric acid','耐硝酸')}</td><td>ΔE ≤ 5</td><td><b>ΔE 3</b></td><td>70% HNO₃, 30 min</td></tr>
      <tr><td>{t('Humidity','耐湿')}</td><td>{t('No blister','无起泡')}</td><td><b>{t('No blister','无起泡')}</b></td><td>ASTM D2247, 4000 h</td></tr>
      <tr><td>{t('Salt spray','盐雾')}</td><td>1/32 in</td><td><b>1/32 in</b></td><td>ASTM B117, 4000 h</td></tr>
      <tr><td>{t('South Florida 10 yr','南佛罗里达 10 年')}</td><td>ΔE ≤ 5, gloss ≥ 50%</td><td><b>ΔE 3</b></td><td>ASTM D2244 / D523</td></tr>
    </tbody></table></div>
  <p class="note" style="margin-top:16px">{t('Values from the fluorocarbon system test report; the powder P2000 is specified to the same class of requirement. Ask for the report for your colour and finish.','以上为氟碳体系检测报告数据；粉末 P2000 按同一等级要求制造。具体颜色与效果请索取对应报告。')}</p>
</div></section>
<section class="section alt"><div class="wrap split">
  <div><span class="eyebrow">{t('Certification status','认证状态')}</span><h2>{t('What we hold — and what we do not.','我们有什么，没有什么。')}</h2>
    <p><b>{t('Held','已取得')}：</b>{t('quality management system certification, high-tech enterprise (2025), tax credit rating A.',
      '质量管理体系认证、2025 年高新技术企业、纳税信用 A 级。')}</p>
    <p><b>ISO 9001</b> — {t('quality management system certificate held.','质量管理体系认证，已持有。')}</p>
    <p><b>AAMA 2603 / 2604 / 2605 · QUALICOAT I / II / III · GSB · UL</b> — <b>{t('no product certificate is held.','未持有任何产品认证证书。')}</b>{t(' We do not display those marks anywhere on this site, in either language.','本站中英文任何位置都不使用这些标志。')}</p>
    <p><b>{t('What we do have','我们确实有的')}：</b>{t('third-party test reports from the National Building Materials Test Centre covering the AAMA 2605 test items — gloss, adhesion, impact, 4000 h salt spray, 10-year South Florida exposure — plus an in-house batch report with every delivery.','国家建筑材料测试中心出具的第三方检测报告，覆盖 AAMA 2605 测试项——光泽、附着、冲击、4000h 盐雾、南佛罗里达 10 年曝晒；以及每批货随附的厂内检测报告。')}</p>
    <p><b>{t('How to use this commercially','商务上怎么用')}：</b>{t('a test report usually satisfies a fabricator or a contractor; a certificate is required when the specifier names one. If a tender demands the certificate, tell us early — we will say we do not have it rather than lose the project at the document check.','加工厂与工程商通常认检测报告；只有设计方点名要求证书时才必须持证。若招标硬性要证书，请尽早告知——我们会直说没有，而不是在资审环节被刷掉。')}</p>
    <p>{t('We test to those methods and can supply third-party reports. If your project requires the certificate itself, we will say plainly that we do not have it and quote the certification route separately. Buyers check — an implied claim is the fastest way to lose an account.',
        '我们按这些方法送检并提供第三方报告。如果项目本身要求证书，我们会直说没有，并单独报认证路径。采购方会核证——含糊暗示是丢客户最快的方式。')}</p>
    <p class="note">{t('Documents on request: TDS, SDS, batch test report, retained sample, non-hazardous declaration.',
        '可提供：TDS、SDS、批次检测报告、留样、非危险品声明。')}</p></div>
  <div class="grid" style="gap:1px;background:var(--line)">
    <div style="background:var(--surface);padding:24px"><h3 style="margin:0">{t('Traceability','可追溯')}</h3><p style="margin:8px 0 0;color:var(--muted)">{t('Batch number on every carton; retained sample kept 12 months.','每箱有批号，留样保存 12 个月。')}</p></div>
    <div style="background:var(--surface);padding:24px"><h3 style="margin:0">{t('Trial report','试粉报告')}</h3><p style="margin:8px 0 0;color:var(--muted)">{t('Every line trial documented: film build, coverage, adhesion, colour.','每次上线试粉都出报告：膜厚、覆盖、附着、颜色。')}</p></div>
    <div style="background:var(--surface);padding:24px"><h3 style="margin:0">{t('Change control','变更控制')}</h3><p style="margin:8px 0 0;color:var(--muted)">{t('Signed specification does not change without written notice.','签样后的规格，未经书面通知不得变更。')}</p></div>
  </div>
</div></section>"""
    write_page(lang, base, sub, "quality.html",
        L(lang,"Quality & Testing — ISO/ASTM Test Matrix | Baolilai","质量与检测 — ISO/ASTM 测试矩阵 | 宝利莱"),
        L(lang,"Powder coating test matrix with methods, plus a plain statement of certification status.",
                 "粉末涂料测试矩阵（含方法），以及如实说明的认证状态。"), body)

def pg_about(lang, base, sub):
    t = lambda en, cn: L(lang, en, cn)
    body = f"""
<section class="section" style="padding-top:150px"><div class="wrap split">
  <div><span class="eyebrow">{t('Company','公司')}</span>
    <h1 style="font-size:clamp(30px,4.2vw,50px)">{t('A coating plant built around three process problems.','一家为解决三个工艺问题而建的粉末厂。')}</h1>
    <p class="lead">{t('Guangdong Baolilai Industrial Co., Ltd. was founded in 2019 in Sanshui, Foshan — inside the Pearl River Delta metalworking cluster, within two hours of most of the aluminium, appliance and hardware plants we serve.',
      '广东宝利莱工业有限公司成立于 2019 年，位于佛山三水，处在珠三角金属加工带内，距我们服务的大部分铝型材、家电与五金厂两小时车程。')}</p>
    <p>{t('The plant was built to solve three specific problems: metallic effects that separate, substrates that cannot take a 190 °C oven, and particle size distributions that drift. Each became a patented process system.',
      '工厂围绕三个具体问题而建：金属效果会分层、基材过不了 190 °C、粒径分布会漂移。每一个都做成了专利工艺装置。')}</p>
  </div>
  <div class="grid" style="gap:1px;background:var(--line)">
    <div style="background:var(--surface);padding:24px"><small class="eyebrow" style="margin:0">{t('Founded','成立')}</small><b style="font-size:28px;font-weight:300">2019</b><p style="margin:6px 0 0;color:var(--muted)">{t('Foshan, Guangdong','广东佛山')}</p></div>
    <div style="background:var(--surface);padding:24px"><small class="eyebrow" style="margin:0">{t('Capacity','产能')}</small><b style="font-size:28px;font-weight:300"><span data-count="18080">18,080</span> t</b><p style="margin:6px 0 0;color:var(--muted)">{t('per year after 2025 expansion','2025 改扩建后 / 年')}</p></div>
    <div style="background:var(--surface);padding:24px"><small class="eyebrow" style="margin:0">{t('Site','厂区')}</small><b style="font-size:28px;font-weight:300">8,631 m²</b><p style="margin:6px 0 0;color:var(--muted)">{t('Building 9,477 m²','建筑面积 9,477 ㎡')}</p></div>
    <div style="background:var(--surface);padding:24px"><small class="eyebrow" style="margin:0">{t('Patents','专利')}</small><b style="font-size:28px;font-weight:300">7</b><p style="margin:6px 0 0;color:var(--muted)">{t('Process and device patents','工艺与装置专利')}</p></div>
  </div>
</div></section>
<section class="section alt"><div class="wrap">
  <span class="eyebrow">{t('The group behind the powder','粉末背后的集团')}</span>
  <h2>{t('Polyshine: three lines, one surface.','宝利鑫：三条产品线，同一个表面。')}</h2>
  <p class="lead">{t('Baolilai is the powder coatings division of Polyshine Technology Limited (宝利鑫科技). The group also formulates the pre-treatment chemistry and runs a liquid PVDF / water-based industrial coatings line — which is why a coating problem can be solved one step upstream instead of argued about.',
      '宝利莱是宝利鑫科技（Polyshine Technology Limited）旗下的粉末涂料板块。集团同时研制前处理药剂，并拥有 PVDF 氟碳漆与水性工业漆产线——所以涂层问题可以往上游解决一步，而不是互相扯皮。')}</p>
  <div class="grid g3" style="margin-top:36px">
    <div><h3>{t('R&amp;D centre','研发中心')}</h3><p class="lead">{t('Formulation, application testing and custom development under one roof.','配方、应用测试与定制开发在同一栋楼里。')}</p></div>
    <div><h3>{t('CMF laboratory','CMF 实验室')}</h3><p class="lead">{t('Colour, Material, Finish: sample boards, gloss and texture development before a line trial.','色彩·材料·表面：上线试粉前先做样板、光泽与纹理开发。')}</p></div>
    <div><h3>{t('Digital factory','数字化工厂')}</h3><p class="lead">{t('IoT and production data across the plant: batch traceability, energy and yield monitoring.','物联网与生产数据贯穿全厂：批次追溯、能耗与良率监控。')}</p></div>
  </div>
  <div class="grid g3" style="margin-top:30px">
    <figure class="figure"><img src="{base}assets/img/lab.jpg" alt="{t('Laboratory','实验室')}" loading="lazy" decoding="async"><figcaption>{t('Laboratory','实验室')}</figcaption></figure>
    <figure class="figure"><img src="{base}assets/img/colour-wall.jpg" alt="{t('Colour sample wall','样板墙')}" loading="lazy" decoding="async"><figcaption>{t('Colour sample wall','样板墙')}</figcaption></figure>
    <figure class="figure"><img src="{base}assets/img/warehouse.jpg" alt="{t('Warehouse','仓库')}" loading="lazy" decoding="async"><figcaption>{t('Warehouse','仓库')}</figcaption></figure>
  </div>
  <p class="note" style="margin-top:22px">{t('Held: ISO 9001 quality management system, high-tech enterprise (2025), tax credit rating A, seven patents. Not held: AAMA, QUALICOAT, GSB or UL product certification — we supply test reports instead.','已取得：ISO 9001 质量管理体系、2025 年高新技术企业、纳税信用 A 级、七项专利。未取得：AAMA、QUALICOAT、GSB、UL 产品认证——我们提供的是检测报告。')}</p>
</div></section>

<section class="section"><div class="wrap">
  <span class="eyebrow">{t('Where we are going','我们要去哪')}</span>
  <h2>{t('Southeast Asia, the Middle East, Africa, Central America.','东南亚、中东、非洲、中美洲。')}</h2>
  <p class="lead">{t('The markets we serve now are the ones that were told a coating could not be both affordable and durable. That is the same problem the group was built to solve at home, and it is why the export line exists.',
      '我们现在服务的市场，正是那些“便宜和耐久只能选一个”的地方。这和集团在国内起步时要解决的问题是同一个，也是出口线存在的理由。')}</p>
</div></section>

<section class="section alt"><div class="wrap">
  <span class="eyebrow">{t('How we operate','我们怎么做生意')}</span>
  <h2>{t('Small enough to answer, large enough to supply.','小到能直接回答你，大到能稳定供货。')}</h2>
  <div class="grid g3" style="margin-top:34px">
    <div><h3>{t('A technical reply, not a price list','给技术答复，不甩价格表')}</h3><p class="lead">{t('A quotation comes with the cure window, film build and test values. If we cannot meet a specification, we say so before the sample ships.','报价单会带固化窗口、膜厚与检测值。做不到的规格，在寄样前就说明。')}</p></div>
    <div><h3>{t('Three-day sampling','3 天出样')}</h3><p class="lead">{t('Panels come off the plant sample line, not a laboratory bench.','样板出自工厂样板线，不是实验室台面。')}</p></div>
    <div><h3>{t('Documentation discipline','文档纪律')}</h3><p class="lead">{t('Batch records, retained samples, trial reports — so a colour question eighteen months later is answered with a panel.','批次记录、留样、试粉报告——18 个月后问颜色，拿得出板。')}</p></div>
  </div>
</div></section>"""
    write_page(lang, base, sub, "about.html",
        L(lang,"Company — Guangdong Baolilai Industrial | Powder Coatings","公司 — 广东宝利莱工业有限公司 | 粉末涂料"),
        L(lang,"Powder coating plant in Sanshui, Foshan. Founded 2019, 18,080 t/yr capacity, seven process patents.",
                 "佛山三水粉末涂料工厂：2019 年成立，年产能 18,080 吨，7 项工艺专利。"), body)

def pg_contact(lang, base, sub):
    t = lambda en, cn: L(lang, en, cn)
    email = f'<div><b style="color:var(--text)">{t("Email","邮箱")}</b><br><a href="mailto:{CFG["email"]}">{CFG["email"]}</a></div>' if CFG["email"] else f'<div><b style="color:var(--text)">{t("Email","邮箱")}</b><br>{t("Please use the form — mailbox being connected","请用右侧表单，邮箱正在配置")}</div>'
    subs = ["Aluminium","Steel","Galvanised steel","MDF / wood","Other"] if lang=="en" else ["铝","钢","镀锌钢","MDF / 木材","其他"]
    vols = ["< 500 kg","0.5–2 t","2–10 t","> 10 t"]
    body = f"""
<section class="section" style="padding-top:150px"><div class="wrap split" style="align-items:start">
  <div><span class="eyebrow">{t('Contact','联系我们')}</span>
    <h1 style="font-size:clamp(28px,3.6vw,44px)">{t('Tell us the substrate, the finish and the volume.','告诉我们基材、效果和月用量。')}</h1>
    <p class="lead">{t('That is enough for a real quotation in USD per kilogram and USD per square metre. The second number is the one your cost sheet needs.',
      '有这三项就能给出真实报价：美元/公斤 与 美元/平方米。后者才是成本表要用的数字。')}</p>
    <div style="margin-top:30px;display:grid;gap:15px;color:var(--muted)">
      {email}
      <div><b style="color:var(--text)">{t('Tel','电话')}</b><br>{f'<a href="tel:{CFG["phone_raw"]}">{CFG["phone"]}</a>' if CFG.get('phone_raw') else t('Available on request','请询')}</div>
      <div><b style="color:var(--text)">WhatsApp</b><br>{f'<a href="https://wa.me/{CFG["wa_raw"]}" target="_blank" rel="noopener">{CFG["whatsapp"]}</a>' if CFG.get('wa_raw') else t('Available on request','请询')}</div>
      <div><b style="color:var(--text)">{t('Plant','工厂')}</b><br>{CFG['addr_en'] if lang=='en' else CFG['addr_cn']}</div>
      <div><b style="color:var(--text)">{t('Hours','营业时间')}</b><br>{t('Monday–Saturday, 08:30–18:00 (GMT+8)','周一至周六 08:30–18:00')}</div>
    </div>
  </div>
  <div><form id="inquiry" data-email="{CFG['email']}">
    <div class="row"><div><label for="name">{t('Name','姓名')}</label><input id="name" name="name" required></div>
    <div><label for="company">{t('Company','公司')}</label><input id="company" name="company"></div></div>
    <div class="row"><div><label for="email">{t('Email','邮箱')}</label><input id="email" name="email" type="email" required></div>
    <div><label for="country">{t('Country','国家')}</label><input id="country" name="country"></div></div>
    <div class="row"><div><label for="substrate">{t('Substrate','基材')}</label><select id="substrate" name="substrate">{''.join(f'<option>{x}</option>' for x in subs)}</select></div>
    <div><label for="volume">{t('Monthly volume','月用量')}</label><select id="volume" name="volume">{''.join(f'<option>{x}</option>' for x in vols)}</select></div></div>
    <div><label for="finish">{t('Finish / RAL reference','效果 / RAL 编号')}</label><input id="finish" name="finish" placeholder="{t('e.g. RAL 7035 sand texture','例如 RAL 7035 砂纹')}"></div>
    <div><label for="message">{t('Application notes','应用说明')}</label><textarea id="message" name="message" rows="5" placeholder="{t('Part type, film build, available cure temperature, current problem','工件类型、膜厚、可用烘烤温度、现在遇到的问题')}"></textarea></div>
    <button class="btn" type="submit">{t('Send inquiry','提交询盘')}</button>
    <div class="ok" id="formOk"></div>
    <p class="note">{t('We reply within one working day. Technical questions get a better answer than commercial ones — send a photo of the failure if you have one.',
      '一个工作日内回复。技术问题比商务问题更好回答——有失效照片就一起发来。')}</p>
  </form></div>
</div></section>
<section class="section alt tight"><div class="wrap"><div class="strip">
  <div><a href="downloads.html">{t('TDS downloads','TDS 下载')}</a></div><div>{t('SDS provided','提供 SDS')}</div><div>{t('Non-hazardous declaration','非危险品声明')}</div>
  <div>{t('Batch test report','批次检测报告')}</div><div>{t('Retained sample 12 months','留样 12 个月')}</div><div>{t('Sample in 3 days','3 天出样')}</div>
</div></div></section>"""
    write_page(lang, base, sub, "contact.html",
        L(lang,"Contact — Request a Powder Coating Quote | Baolilai","联系我们 — 粉末涂料询价 | 宝利莱"),
        L(lang,"Request a powder coating quotation: substrate, finish, film build and monthly volume.",
                 "粉末涂料询价：基材、效果、膜厚与月用量，一个工作日内回复。"), body)

# ------------------------------------------------------------------ assets
def build_assets():
    os.makedirs(os.path.join(OUT,"assets/css"), exist_ok=True)
    os.makedirs(os.path.join(OUT,"assets/js"), exist_ok=True)
    open(os.path.join(OUT,"assets/css/site.css"),"w",encoding="utf-8").write(CSS)
    open(os.path.join(OUT,"assets/js/site.js"),"w",encoding="utf-8").write(JS)
    open(os.path.join(OUT,"assets/favicon.svg"),"w",encoding="utf-8").write(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><rect width="32" height="32" fill="#3f6149"/>'
        '<text x="16" y="22" font-family="Arial" font-size="15" fill="#f5f6f2" text-anchor="middle">B</text></svg>')
    try:
        from PIL import Image
        Image.MAX_IMAGE_PIXELS = None
        os.makedirs(os.path.join(OUT,"assets/img"), exist_ok=True)
        for src, name, w in SRC:
            if not os.path.exists(src):
                print("  ! missing", src); continue
            im = Image.open(src).convert("RGB")
            if im.width > w: im = im.resize((w, int(im.height*w/im.width)), Image.LANCZOS)
            im.save(os.path.join(OUT,"assets/img",name), quality=80, progressive=True, optimize=True)
    except Exception as e:
        print("  ! image step:", e)

def build_meta():
    if not CFG["domain"]:
        for f in ("sitemap.xml", "robots.txt"):
            fp = os.path.join(OUT, f)
            if os.path.exists(fp): os.remove(fp)
        print("  meta: no domain set — sitemap/robots skipped")
        return
    pages = ["index.html","products.html","colors.html","durability.html","functional.html","integrated.html","pvdf.html","automotive.html",
             "series-bonded.html","series-architectural.html","series-lowtemp.html","series-industrial.html",
             "applications.html","technology.html","quality.html","downloads.html","about.html","contact.html"]
    sm = ['<?xml version="1.0" encoding="UTF-8"?>','<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for p in pages:
        for prefix in ("", "cn/"):
            sm.append(f"  <url><loc>{CFG['domain']}/{prefix}{p}</loc>"
                      f"<priority>{'1.0' if p=='index.html' else '0.8'}</priority></url>")
    sm.append("</urlset>")
    open(os.path.join(OUT,"sitemap.xml"),"w",encoding="utf-8").write("\n".join(sm))
    open(os.path.join(OUT,"robots.txt"),"w",encoding="utf-8").write(
        f"User-agent: *\nAllow: /\nSitemap: {CFG['domain']}/sitemap.xml\n")
    ld = {"@context":"https://schema.org","@type":"Organization",
          "name":CFG["brand_full_en"],"alternateName":CFG["brand_full_cn"],"url":CFG["domain"],
          "address":{"@type":"PostalAddress","addressLocality":"Foshan","addressRegion":"Guangdong","addressCountry":"CN"},
          "description":"Powder coating manufacturer: bonded metallics, architectural polyester, low-temperature cure, epoxy systems."}
    os.makedirs(os.path.join(OUT,"assets"),exist_ok=True)
    open(os.path.join(OUT,"assets/organization.json"),"w",encoding="utf-8").write(json.dumps(ld,ensure_ascii=False,indent=2))

def build_readme():
    open(os.path.join(OUT,"README.md"),"w",encoding="utf-8").write("""# Baolilai powder coating site (bilingual)

EN: `/`  ·  CN: `/cn/`  ·  generator: `build_site.py`

    cd /g/baolilai-site && python -m http.server 8099
    # http://127.0.0.1:8099/      (English)
    # http://127.0.0.1:8099/cn/   (中文)

## Launch checklist
1. Edit `CFG` at the top of `build_site.py`: email / phone / whatsapp / domain.
2. `python build_site.py` — regenerates both languages.
3. Replace the two `assets/img/application-*.jpg` with the plant's own photos
   (they are labelled "application reference" until then).
4. Colour card: `COLORS` list holds 24 RAL references + hex approximations.
   Add/remove entries there; both languages update automatically.

## Colour discipline (important)
RAL does not define sRGB values. The hex numbers in `COLORS` are approximations
for screen display only. Every page that shows a colour states that approval is
made on a sprayed panel against a physical RAL chip. Do not remove that sentence.

## Claim discipline
No AAMA / QUALICOAT / GSB / UL certificate is claimed anywhere. `quality.html`
states what is held and what is not, in both languages.

## Structure
- 12 pages × 2 languages, static, zero CDN dependencies
- `assets/css/site.css` — Archetype D tokens (bright natural, sage/grey-green)
- `assets/js/site.js` — header, hero carousel, reveal, counters, inquiry form
- `sitemap.xml` with both languages, `hreflang` tags on every page
""")

def main():
    os.makedirs(OUT, exist_ok=True)
    print("building ->", OUT)
    build_assets()
    for lang, sub, base in (("en", "", ""), ("cn", "cn", "../")):
        pg_index(lang, base, sub); pg_products(lang, base, sub); pg_colors(lang, base, sub)
        pg_applications(lang, base, sub); pg_technology(lang, base, sub)
        pg_quality(lang, base, sub); pg_about(lang, base, sub); pg_contact(lang, base, sub)
        pg_durability(lang, base, sub); pg_functional(lang, base, sub); pg_integrated(lang, base, sub)
        pg_pvdf(lang, base, sub); pg_automotive(lang, base, sub)
        pg_downloads(lang, base, sub)
        for s, prods, intro, eh, et, faq in SERIES_PAGES:
            pg_series(lang, base, sub, s, prods, intro, eh, et, faq)
        print(f"  {lang} done")
    build_meta(); build_readme()
    print("done")

# --- series page content (bilingual tuples)
SERIES_PAGES = [
    (SERIES[0], [PRODUCTS[0], PRODUCTS[1]],
     ("Metallic effects fail in the field for one reason: the pigment and the base powder are only mixed, not joined. Bonding fixes the ratio at the particle level, which changes what happens in the box, in the gun and in the reclaim hopper.",
      "金属效果在现场失效只有一个原因：颜料与基粉只是混在一起，没有结合。邦定把比例固定到颗粒层面，于是箱内、枪口、回收桶里的表现都变了。"),
     ("""<div class="split"><div><span class="eyebrow">Process / 工艺</span><h2>What bonding changes. / 邦定改变了什么。</h2>
     <p>In a dry blend, pigment and base powder differ in particle size and density; vibration separates them, the first parts of a shift look different from the last, and reclaimed powder is unusable for a critical colour.</p>
     <p>With bonding the pigment is fixed onto the base particle, so every scoop is the same and reclaim can go back into the hopper.</p></div>
     <figure class="figure"><div class="ralswatch" style="background:#8C7048"><span>RAL 1036</span></div><figcaption>Bonded gold / 邦定金</figcaption></figure></div>""",
      """<div class="split"><div><span class="eyebrow">工艺</span><h2>邦定改变了什么。</h2>
     <p>干混体系里颜料与基粉的粒径和密度不同，震动就会分层：一个班次开头和结尾的件颜色不一样，回收粉也不能用在关键色上。</p>
     <p>邦定把颜料固定到基粉颗粒上，每一勺比例一致，回收粉可以直接回桶。</p></div>
     <figure class="figure"><div class="ralswatch" style="background:#8C7048"><span>RAL 1036</span></div><figcaption>邦定金</figcaption></figure></div>"""),
     [("Pigment separation / 颜料分离", "None / 无", "Visual"), ("Reclaim / 回收", "Reusable / 可再用", "Trial"),
      ("Batch ΔE", "≤ 1.5", "ASTM D2244"), ("Film build / 膜厚", "70–90 µm", "ISO 2808"),
      ("Adhesion / 附着", "0–1", "ISO 2409"), ("Impact / 冲击", "50 kg·cm", "ASTM D2794")],
     [("Can bonded metallic be reclaimed? / 邦定粉能回收吗？",
       "Yes — the overspray keeps the same pigment-to-base ratio, so it blends back instead of being sold as seconds. / 能。过喷粉的颜料基粉比例不变，可以掺回使用，不必当次品处理。"),
      ("Why does mirror need a clear coat? / 镜面为什么必须罩光？",
       "The metallic layer sits at the surface; a clear coat protects it from oxidation and handling. / 金属层暴露在表面，罩光层防氧化也防刮擦。"),
      ("Is bonded suitable outdoors? / 邦定能户外用吗？",
       "Depends on the base chemistry: BL-M102 uses exterior polyester; BL-M103 is for interior and sheltered use. / 看基体体系：BL-M102 用户外聚酯，BL-M103 限室内或遮蔽环境。")]),
    (SERIES[1], [PRODUCTS[2], PRODUCTS[3]],
     ("Exterior polyesters for aluminium profiles, façade panels and entrance systems: sand textures that hide substrate defects, and a super-durable matte for coastal and high-UV projects.",
      "铝型材、幕墙板与入口系统的户外聚酯：遮基材缺陷的砂纹，以及面向沿海与强紫外项目的超耐候哑光。"),
     ("""<div class="split"><div><span class="eyebrow">Specification / 规格</span><h2>Standard or super-durable. / 常规还是超耐候。</h2>
     <p>Standard exterior polyester answers most window and profile work. Super-durable costs more per kilo and holds gloss and colour longer under high UV. We quote both and show the test data rather than arguing about years.</p>
     <p class="note">TGIC and TGIC-free (HAA) routes are both available.</p></div>
     <figure class="figure"><img src="@BASE@assets/img/application-facade.jpg" alt="aluminium facade" loading="eager" width="1600" height="1067"><figcaption>Application reference / 应用参考</figcaption></figure></div>""",
      """<div class="split"><div><span class="eyebrow">规格</span><h2>常规还是超耐候。</h2>
     <p>多数门窗型材用常规户外聚酯就够。超耐候每公斤更贵，但强紫外下保光保色更久。两条都报，用数据说话，不争“保几年”。</p>
     <p class="note">TGIC 与 TGIC-free（HAA）两条路线都可做。</p></div>
     <figure class="figure"><img src="@BASE@assets/img/application-facade.jpg" alt="铝幕墙" loading="eager" width="1600" height="1067"><figcaption>应用参考</figcaption></figure></div>"""),
     [("Adhesion / 附着", "0–1", "ISO 2409"), ("Impact / 冲击", "50 kg·cm", "ASTM D2794"),
      ("Salt spray / 盐雾", "500 h / 1000 h", "ASTM B117"), ("QUV", "500–2000 h", "ASTM G154"),
      ("ΔE", "≤ 1.5", "ASTM D2244"), ("Film build / 膜厚", "60–90 µm", "ISO 2808")],
     [("Do you hold AAMA or QUALICOAT? / 有 AAMA 或 QUALICOAT 认证吗？",
       "Not today. We test to those methods and can supply third-party reports; we will not imply a certificate we do not hold. / 目前没有。我们按这些方法送检并提供第三方报告，不会暗示没有的证书。"),
      ("Chemistry for a coastal project? / 沿海项目用什么体系？",
       "Super-durable polyester at 80 µm or above, with verified pre-treatment. / 超耐候聚酯，膜厚 80 µm 以上，前处理必须验证。"),
      ("Can you match an anodised colour? / 能配阳极氧化的颜色吗？",
       "Yes within pigment limits — send a physical sample and we return a panel with the ΔE we can hold. / 在颜料允许范围内可以，寄实物样，我们回喷板并给出能把住的 ΔE。")]),
    (SERIES[2], [PRODUCTS[4]],
     ("A 130 °C cure opens substrates a 180–200 °C system cannot touch: MDF, thin-wall extrusions, and assemblies that already contain plastic or heat-sensitive parts.",
      "130 °C 固化，打开了 180–200 °C 体系碰不了的基材：MDF、薄壁型材，以及已经装了塑料件的组件。"),
     ("""<div class="split"><div><span class="eyebrow">Why / 为什么</span><h2>The oven is the constraint. / 瓶颈在烘道。</h2>
     <p>Most powder decisions are made by the oven, not the colour card. Dropping from 190 °C to 130 °C cuts energy per cycle and removes the charring and edge-lift that make MDF finishing expensive.</p>
     <p>Low-temperature chemistry has a narrower window, so we specify it on a measured workpiece curve, not an oven setpoint.</p></div>
     <figure class="figure"><div class="ralswatch" style="background:#FFFFFF;border:1px solid #dfe5dc"><span>RAL 9010</span></div><figcaption>Low-temp white / 低温白</figcaption></figure></div>""",
      """<div class="split"><div><span class="eyebrow">为什么</span><h2>瓶颈在烘道。</h2>
     <p>多数粉末选型是被烘道决定的，不是被色卡决定的。从 190 °C 降到 130 °C，单次能耗下降，也去掉了让 MDF 涂装变贵的焦边和起翘。</p>
     <p>低温体系窗口更窄，所以按实测工件曲线定参数，不看炉子设定值。</p></div>
     <figure class="figure"><div class="ralswatch" style="background:#FFFFFF;border:1px solid #dfe5dc"><span>RAL 9010</span></div><figcaption>低温白</figcaption></figure></div>"""),
     [("Cure / 固化", "130 °C × 20 min", "Workpiece curve"), ("Alt / 备选", "140 °C × 15 min", "Workpiece curve"),
      ("Film build / 膜厚", "60–80 µm", "ISO 2808"), ("Adhesion / 附着", "0–1", "ISO 2409"),
      ("Impact / 冲击", "40–50 kg·cm", "ASTM D2794"), ("Overbake / 过烘", "Avoid / 严禁", "ΔE / visual")],
     [("Is performance lower? / 机械性能会差吗？",
       "Impact is slightly lower; adhesion and chemical resistance are comparable. Not for heavy corrosion duty. / 冲击略低，附着与耐化学相当；重防腐场景不适用。"),
      ("Oven setpoint or part temperature? / 看炉温还是工件温度？",
       "Part temperature. Dense extrusions need longer than thin panels at the same setpoint. / 看工件温度。同样的炉温，厚型材比薄板需要更长时间。"),
      ("MDF without primer? / MDF 能不打底吗？",
       "Yes with conductive pre-treatment and low-temp powder; edge quality depends on board and sanding. / 可以，需导电前处理配合；板边质量取决于板材与打磨。")]),
    (SERIES[3], [PRODUCTS[5]],
     ("Pure epoxy and hybrid systems for the parts where the specification is corrosion, not colour: pipes, valves, tanks, enclosures, shelving and battery hardware.",
      "规格是防腐而不是颜色的地方，用纯环氧与混合型：管道、阀门、储罐、机柜、货架与电池托盘。"),
     ("""<div class="split"><div><span class="eyebrow">Specification / 规格</span><h2>Epoxy does one thing better. / 环氧只赢一件事。</h2>
     <p>Adhesion and corrosion resistance — and it is the cheapest route to a salt-spray number. What it cannot do is stay outside: UV chalks and yellows the film.</p>
     <p>On galvanised steel, adhesion is a pre-treatment problem before it is a powder problem.</p></div>
     <figure class="figure"><div class="ralswatch" style="background:#7D7F7D"><span>RAL 7037</span></div><figcaption>Epoxy grey / 环氧灰</figcaption></figure></div>""",
      """<div class="split"><div><span class="eyebrow">规格</span><h2>环氧只赢一件事。</h2>
     <p>附着与防腐，而且是最便宜的盐雾数字路线。它做不到的是户外：紫外下会粉化、变黄。</p>
     <p>镀锌件附着差，先是前处理问题，才是粉末问题。</p></div>
     <figure class="figure"><div class="ralswatch" style="background:#7D7F7D"><span>RAL 7037</span></div><figcaption>环氧灰</figcaption></figure></div>"""),
     [("Film build / 膜厚", "80–120 µm", "ISO 2808"), ("Adhesion / 附着", "0", "ISO 2409"),
      ("Salt spray / 盐雾", "1000 h @ ≥100 µm", "ASTM B117"), ("Chemical / 耐化学", "Per application", "ASTM D1308"),
      ("Impact / 冲击", "50 kg·cm", "ASTM D2794"), ("UV / 紫外", "Not recommended / 不推荐", "—")],
     [("Can epoxy go outdoors? / 环氧能户外用吗？",
       "No. It chalks and loses gloss. Use the polyester series for daylight. / 不能，会粉化失光；见光部位用聚酯系列。"),
      ("How is 1000 h reached? / 1000h 盐雾怎么做到？",
       "Pre-treatment, ≥100 µm, full cure — all three. / 前处理、膜厚 100 µm 以上、完全固化，三者缺一不可。"),
      ("Do you supply a primer? / 供底粉吗？",
       "For galvanised and pitted substrates we quote a compatible primer or zinc-rich route. / 镀锌与麻面基材，我们报配套底粉或富锌方案。")]),
]


# ============================================================ v3 pages (from Polyshine deck)
def pg_durability(lang, base, sub):
    t = lambda en, cn: L(lang, en, cn)
    rows = [
        ("P1000", t("Standard polyester","标准耐候聚酯"), "AAMA 2603 / QUALICOAT I",
         t("Up to 10 years","最高 10 年"), t("Inland façades, general architecture","内陆幕墙、一般建筑")),
        ("P1500", t("Super-durable polyester","超耐候聚酯"), "AAMA 2604 / QUALICOAT II",
         t("Up to 15 years","最高 15 年"), t("Curtain wall, coastal, high UV","幕墙、沿海、强紫外")),
        ("P2000", t("Fluorocarbon","氟碳"), "AAMA 2605 / QUALICOAT III",
         t("Up to 20 years","最高 20 年"), t("Landmarks, extreme exposure","地标、极端环境")),
    ]
    trs = "".join(f"<tr><td><b>{a}</b></td><td>{b}</td><td>{c}</td><td>{d}</td><td>{e}</td></tr>" for a,b,c,d,e in rows)
    body = f"""
<section class="section" style="padding-top:150px"><div class="wrap">
  <span class="eyebrow">{t('Durability ladder','耐候等级')}</span>
  <h1 style="font-size:clamp(30px,4.2vw,50px)">{t('Three classes. One honest ladder.','三个等级，一条不吹的阶梯。')}</h1>
  <p class="lead">{t('Architectural powder is sold on a number of years. The number only means something when it is tied to a chemistry, a standard class and a film build. This is how the P-series is structured.',
      '建筑粉末卖的是“保几年”。只有把年限绑到具体体系、标准等级和膜厚上，这个数字才成立。P 系列就是按这个逻辑分档的。')}</p>
  <div class="scroll" style="margin-top:40px"><table>
    <thead><tr><th>{t('Series','系列')}</th><th>{t('Chemistry','体系')}</th><th>{t('Tested to (not certified)','对标送检（非认证）')}</th><th>{t('Design life','设计年限')}</th><th>{t('Typical use','典型应用')}</th></tr></thead>
    <tbody>{trs}</tbody></table></div>
  <p class="note" style="margin-top:16px">{t('Design life is a target tied to the test report, the pre-treatment and the film build in the specification. It is not a warranty on its own.',
      '设计年限是与测试报告、前处理和规格膜厚绑定的目标值，本身不构成质保承诺。')}</p>
  <p class="note" style="margin-top:10px"><b>{t('Reading that column correctly','第二列怎么读')}：</b>{t('it is the test standard our products are measured against, not a certificate number. We hold no AAMA or QUALICOAT product certificate — we hold the test reports.','那是产品对标并送检的标准，不是证书编号。我们不持有 AAMA 或 QUALICOAT 产品证书，持有的是检测报告。')}</p>
</div></section>

<section class="section alt"><div class="wrap">
  <span class="eyebrow">{t('What each class actually means','每个等级到底差在哪')}</span>
  <div class="steps" style="margin-top:30px">
    <div class="step"><div class="n"></div><div><h3>P1000 · {t('Standard exterior','标准户外')}</h3>
      <p>{t('A polyester that holds colour and gloss in normal inland exposure. The cost-effective answer for window systems and panels that are not facing salt or desert sun.',
           '常规内陆曝晒下能保住颜色和光泽的聚酯。门窗型材与不临海、不强紫外的板材，用这一档最划算。')}</p></div></div>
    <div class="step"><div class="n"></div><div><h3>P1500 · {t('Super-durable','超耐候')}</h3>
      <p>{t('Higher-grade polyester with a stronger light-stabiliser package, tested to the AAMA 2604 / QUALICOAT II level. The default choice for curtain wall and coastal projects.',
           '更高等级聚酯 + 更强光稳定体系，按 AAMA 2604 / QUALICOAT II 级送检。幕墙与沿海项目的默认选项。')}</p></div></div>
    <div class="step"><div class="n"></div><div><h3>P2000 · {t('Fluorocarbon','氟碳')}</h3>
      <p>{t('Fluorocarbon chemistry, tested to AAMA 2605 / QUALICOAT III — the top exterior class. Specified where the façade is the brand: landmarks, airports, extreme UV and salt.',
           '氟碳体系，按 AAMA 2605 / QUALICOAT III 级送检——户外最高等级。外立面本身就是品牌的项目才用它：地标、机场、极端紫外与盐雾环境。')}</p></div></div>
  </div>
</div></section>

<section class="section"><div class="wrap split">
  <div><span class="eyebrow">{t('How to specify','怎么下单才不踩坑')}</span>
    <h2>{t('Five lines that decide the outcome.','决定成败的五行字。')}</h2>
    <ul style="color:var(--muted);padding-left:20px;font-size:15px">
      <li>{t('Chemistry + standard class (P1000 / P1500 / P2000)','体系 + 标准等级（P1000 / P1500 / P2000）')}</li>
      <li>{t('Film build and the substrate pre-treatment','膜厚与基材前处理方式')}</li>
      <li>{t('Colour reference (RAL / Pantone) and gloss level','颜色编号（RAL / Pantone）与光泽档位')}</li>
      <li>{t('Test items and acceptance values, with methods','测试项目与验收值，附方法编号')}</li>
      <li>{t('Retained sample and colour tolerance (ΔE)','留样与色差公差（ΔE）')}</li>
    </ul>
    <a class="btn" href="contact.html">{t('Ask for a durability proposal','索取耐候方案')}</a></div>
  <figure class="figure"><img src="{base}assets/img/facade-panels.jpg" alt="{t('Coated façade panels','喷涂幕墙板')}" loading="lazy" decoding="async"><figcaption>{t('Coated façade panels','喷涂幕墙板')}</figcaption></figure>
</div></section>"""
    write_page(lang, base, sub, "durability.html",
        L(lang,"Durability Classes P1000 / P1500 / P2000 — AAMA & QUALICOAT | Baolilai",
                 "耐候等级 P1000 / P1500 / P2000 — AAMA 与 QUALICOAT | 宝利莱"),
        L(lang,"Architectural powder coating durability classes: P1000 (AAMA 2603 / QUALICOAT I), P1500 (2604 / II), P2000 fluorocarbon (2605 / III).",
                 "建筑粉末涂料耐候分级：P1000（AAMA 2603 / QUALICOAT I）、P1500（2604 / II）、P2000 氟碳（2605 / III）。"), body)

def pg_functional(lang, base, sub):
    t = lambda en, cn: L(lang, en, cn)
    items = [
        ("9H", t("9H ultra-hard","9H 超硬"), t("Nano-modified polyester","纳米改性聚酯"),
         t("Pencil hardness 9H, abrasion and scratch resistance","铅笔硬度 9H，耐刮擦耐磨损"),
         t("Appliance fronts, 3C housings, elevator panels","家电面板、3C 外壳、电梯板")),
        ("AG", t("Antibacterial","抗菌"), t("Polyester / epoxy + silver-ion additive","聚酯/环氧 + 银离子抗菌剂"),
         t("Inhibits bacteria and mould on the film surface","抑制表面细菌与霉菌"),
         t("Medical equipment, public furniture, food service","医疗设备、公共家具、餐饮设备")),
        ("SC", t("Self-cleaning / anti-graffiti","抗污自洁"), t("Low-surface-energy polyester","低表面能聚酯"),
         t("Dirt does not bond; rain washes residue off","污物难附着，雨水自洁"),
         t("Tunnels, signage, street furniture","隧道、标识、市政设施")),
        ("EC", t("Conductive","导电"), t("Carbon / metal-filled system","碳系/金属填料体系"),
         t("Surface resistance for ESD control","表面电阻满足防静电要求"),
         t("Electronics racks, clean rooms, explosive areas","电子机柜、洁净室、防爆场所")),
        ("HT", t("High temperature 600 °C","耐高温 600 ℃"), t("Silicone / special inorganic","有机硅/特种无机"),
         t("Holds adhesion and colour at 600 °C service","600 ℃ 长期使用仍保附着与颜色"),
         t("Stoves, exhausts, engine parts, BBQ grills","炉具、排气管、发动机件、烤炉")),
        ("PC", t("Pipe anti-corrosion","管道防腐"), t("Epoxy / PE-based","环氧/聚乙烯体系"),
         t("Designed for steel pipe exteriors, oil gas water","专为钢管外壁，油气水输送"),
         t("Oil & gas, water mains, district heating","油气、供水主管、集中供热")),
        ("IN", t("Electrical insulation","绝缘"), t("Epoxy insulation grade","环氧绝缘级"),
         t("Dielectric strength, edge coverage","介电强度与边角覆盖"),
         t("Busbars, motor parts, switchgear","母线、电机件、开关柜")),
        ("AU", t("Automotive parts","汽车零部件"), t("Epoxy / hybrid / polyester / PU / acrylic","环氧/混合/聚酯/PU/丙烯酸"),
         t("Wheels, springs, chassis, filters, mirrors","轮毂、弹簧、底盘、滤清器、后视镜"),
         t("Tier-1 and aftermarket, IATF route on request","一级供应商与售后，可按 IATF 路径推进")),
        ("WG", t("Wood-grain transfer base","木纹转印底粉"), t("Polyurethane, high flow","聚氨酯高流平体系"),
         t("High definition transfer, outdoor durability","转印清晰度高，户外耐候"),
         t("Aluminium doors and windows, furniture profiles","铝门窗、家具型材")),
    ]
    cards = "".join(f"""<article class="card rv"><div class="body">
        <span class="kicker">{code}</span><h3>{name}</h3>
        <p><b style="font-weight:500">{chem}</b></p>
        <p>{prop}</p><p class="note" style="margin:0">{app}</p></div></article>""" for code,name,chem,prop,app in items)
    body = f"""
<section class="section" style="padding-top:150px"><div class="wrap">
  <span class="eyebrow">{t('Functional coatings','功能性粉末')}</span>
  <h1 style="font-size:clamp(30px,4.2vw,50px)">{t('When the coating has a job beyond looking good.','当涂层要干活，不只是好看。')}</h1>
  <p class="lead">{t('Nine functional platforms. Each one is a formulation answer to a measurable requirement — hardness in H, resistance in ohms, temperature in °C, bacteria in log reduction.',
      '九个功能平台。每一个都是针对可测指标给出的配方答案——硬度用 H、电阻用欧姆、耐温用 ℃、抗菌用对数减少值。')}</p>
  <div class="grid g3" style="margin-top:44px">{cards}</div>
</div></section>
<section class="section alt"><div class="wrap">
  <span class="eyebrow">{t('Specification notes','选型提示')}</span>
  <h2>{t('Three things buyers get wrong.','采购最常搞错的三件事。')}</h2>
  <div class="steps" style="margin-top:30px">
    <div class="step"><div class="n"></div><div><h3>{t('Functional additives change the cure window','功能助剂会改固化窗口')}</h3>
      <p>{t('Conductive and 9H systems are not drop-in replacements: pigment loading and additive level shift the flow and the cure. Re-run the line trial, do not assume the old oven profile works.',
           '导电与 9H 体系不是“直接替换”：填料与助剂比例会改变流动性与固化。必须重跑试粉，不能沿用原炉温曲线。')}</p></div></div>
    <div class="step"><div class="n"></div><div><h3>{t('Ask for the test, not the adjective','要报告，不要形容词')}</h3>
      <p>{t('“Antibacterial” means nothing without a standard and a log-reduction figure. “Conductive” means nothing without a surface-resistance range and a method.',
           '“抗菌”没有标准号和抑菌率就是空话；“导电”没有表面电阻区间和测试方法也是空话。')}</p></div></div>
    <div class="step"><div class="n"></div><div><h3>{t('Check compatibility with the pre-treatment','先确认与前处理的兼容性')}</h3>
      <p>{t('Self-cleaning and conductive films are sensitive to substrate residues. Where the substrate is galvanised or chromated, send a panel before committing to volume.',
           '自洁与导电膜对基材残留敏感。镀锌或铬化基材，先寄板确认再谈量。')}</p></div></div>
  </div>
</div></section>
<section class="section dark"><div class="wrap" style="display:flex;justify-content:space-between;gap:22px;align-items:center;flex-wrap:wrap">
  <h2 style="margin:0">{t('Send the requirement, not the product name.','发需求，不用发产品名。')}</h2>
  <a class="btn on-dark" href="contact.html">{t('Discuss a functional spec','沟通功能指标')}</a>
</div></section>"""
    write_page(lang, base, sub, "functional.html",
        L(lang,"Functional Powder Coatings — 9H, Antibacterial, Conductive, 600 °C | Baolilai",
                 "功能性粉末涂料 — 9H、抗菌、导电、耐高温 600℃ | 宝利莱"),
        L(lang,"Functional powder platforms: 9H hardness, antibacterial, self-cleaning, conductive, 600 °C high temperature, pipe anti-corrosion, insulation, automotive, wood-grain base.",
                 "功能粉末平台：9H 超硬、抗菌、抗污自洁、导电、耐高温 600℃、管道防腐、绝缘、汽车零部件、木纹转印底粉。"), body)

def pg_integrated(lang, base, sub):
    t = lambda en, cn: L(lang, en, cn)
    pre = [
        ("1", t("Loading","上件"), t("Hang parts so every surface is exposed and no liquid traps","悬挂牢固、各面暴露、无兜液死角")),
        ("2", t("Pre-degrease","预脱脂"), t("Remove the bulk of oil and loose soil","去除大部分油污与颗粒")),
        ("3", t("Main degrease","主脱脂"), t("Remove all residual oil — this decides adhesion","彻底除油，决定附着力")),
        ("4", t("Rinse 1 + 2","水洗①②"), t("Two-stage rinse so cleaner is not carried forward","两级水洗，防止污染后槽")),
        ("5", t("Silane / zirconium conversion","硅烷/陶化"), t("Chrome-free, phosphate-free nano ceramic film","无铬无磷纳米陶瓷膜")),
        ("6", t("Rinse 3 + DI rinse","水洗③ + 纯水洗"), t("Deionised final rinse — prevents craters and specks","去离子水终洗，防缩孔颗粒")),
        ("7", t("Dry-off","烘干"), t("Dry before powder; moisture causes pinholes","入粉前烘干，水分致针孔")),
    ]
    pre_rows = "".join(f"<tr><td>{a}</td><td><b>{b}</b></td><td>{c}</td></tr>" for a,b,c in pre)
    chems = [
        ("BS-Q03 / BS-Q04", t("Alkaline degreaser / oil remover","碱性脱脂剂 / 除油剂")),
        ("BS-Q07", t("Spray chromating agent","喷涂铬化剂")),
        ("BS-H09", t("Chrome-free passivation for RoHS markets","无铬皮膜剂（应对 RoHS）")),
        ("BS-H03", t("Fluoride-free neutralising brightener (replaces nitric/sulphuric)","无氟中和增光剂（替代硝酸/硫酸中和）")),
        ("BS-F01 / BS-F02", t("Room / mid-temperature sealing","常温 / 中温封孔剂")),
        ("BS-H01 / BS-H04", t("Nickel-free sealing, room / mid temperature","无镍常温 / 中温封孔剂")),
        ("BS-Z01 / Z03 / Z04", t("Bronze / gold / copper colouring","古铜 / 金黄 / 紫铜着色剂")),
        ("BS-H02", t("Tin-free black colouring","无锡着色剂")),
        ("BS-H05", t("Paint stripper for jigs (replaces sulphuric acid)","挂具脱漆剂（替代浓硫酸）")),
    ]
    chem_rows = "".join(f"<tr><td><b>{a}</b></td><td>{b}</td></tr>" for a,b in chems)
    body = f"""
<section class="section" style="padding-top:150px"><div class="wrap">
  <span class="eyebrow">{t('Integrated surface finishing','一体化表面处理')}</span>
  <h1 style="font-size:clamp(30px,4.2vw,50px)">{t('Chemistry, powder and liquid — one responsibility.','药剂、粉末、液体漆——一个责任主体。')}</h1>
  <p class="lead">{t('Most coating failures are born one step before the coating. Baolilai is the powder division of Polyshine Technology, which also supplies the pre-treatment chemistry and the liquid PVDF line. That means one supplier answers for the whole chain instead of three suppliers pointing at each other.',
      '多数涂层失效，发生在涂装的前一步。宝利莱是宝利鑫科技旗下的粉末板块，集团同时供应前处理药剂与 PVDF 液体漆线——整条链由一个供应商负责，而不是三家互相指。')}</p>
</div></section>

<section class="section alt"><div class="wrap">
  <span class="eyebrow">{t('Pre-treatment','前处理')}</span>
  <h2>{t('The seven steps that decide adhesion.','决定附着力的七道工序。')}</h2>
  <div class="scroll" style="margin-top:30px"><table>
    <thead><tr><th>#</th><th>{t('Step','工序')}</th><th>{t('Purpose','目的')}</th></tr></thead>
    <tbody>{pre_rows}</tbody></table></div>
  <p class="note" style="margin-top:16px">{t('Silane / zirconium conversion replaces traditional phosphating: no heavy metals, less sludge, and a film that powder adheres to reliably.',
      '硅烷/陶化替代传统磷化：不含重金属、淤泥更少，粉末在其上的附着力稳定。')}</p>
</div></section>

<section class="section"><div class="wrap">
  <span class="eyebrow">{t('Anodising chemistry','阳极氧化药剂')}</span>
  <h2>{t('For plants that anodise as well as coat.','给既做氧化又做喷涂的工厂。')}</h2>
  <div class="scroll" style="margin-top:30px"><table>
    <thead><tr><th>{t('Product code','产品编号')}</th><th>{t('Function','功能')}</th></tr></thead>
    <tbody>{chem_rows}</tbody></table></div>
  <p class="note" style="margin-top:16px">{t('Anodising line sequence: loading → degrease → alkali etch → neutralise → (polish) → anodise → colour → seal. We supply the chemistry for each bath.',
      '氧化线工序：上挂 → 脱脂 → 碱蚀 → 中和 →（抛光）→ 氧化 → 着色 → 封孔。各槽药剂我们都能供。')}</p>
  <div class="scroll" style="margin-top:26px"><table>
    <thead><tr><th>#</th><th>{t('Anodising step','氧化工序')}</th><th>{t('Function','作用')}</th></tr></thead>
    <tbody>
      <tr><td>1</td><td><b>{t('Loading','装挂')}</b></td><td>{t('Aluminium or titanium jigs, good electrical contact','铝或钛挂具，保证导电')}</td></tr>
      <tr><td>2</td><td><b>{t('Degrease','脱脂')}</b></td><td>{t('Remove oil and handling soil','去除油污与搬运脏污')}</td></tr>
      <tr><td>3</td><td><b>{t('Alkali etch','碱蚀')}</b></td><td>{t('Remove natural oxide, uniform matte surface','去除自然氧化膜，表面均匀亚光')}</td></tr>
      <tr><td>4</td><td><b>{t('Neutralise / desmut','中和出光')}</b></td><td>{t('Remove the black smut left by the caustic bath','去除碱蚀后的挂灰')}</td></tr>
      <tr><td>5</td><td><b>{t('Polish (optional)','抛光（可选）')}</b></td><td>{t('Chemical or electrolytic brightening','化学或电解增亮')}</td></tr>
      <tr><td>6</td><td><b>{t('Anodise','氧化')}</b></td><td>{t('Sulphuric bath, porous Al₂O₃ film forms','硫酸槽生成多孔氧化膜')}</td></tr>
      <tr><td>7</td><td><b>{t('Colour (optional)','着色（可选）')}</b></td><td>{t('Organic dye or electrolytic colouring','有机染料或电解着色')}</td></tr>
      <tr><td>8</td><td><b>{t('Seal','封孔')}</b></td><td>{t('Close the pores; decides salt spray and weight loss','封闭孔隙，决定盐雾与失重')}</td></tr>
    </tbody></table></div>
</div></section>

<section class="section alt"><div class="wrap split">
  <div><span class="eyebrow">{t('Why one supplier','为什么要一家供')}</span>
    <h2>{t('Compatibility is not a document.','兼容性不是一份文件。')}</h2>
    <p>{t('A pre-treatment chemical and a powder are developed against each other. When the passivation film and the powder chemistry come from the same house, the adhesion and salt-spray numbers are repeatable instead of negotiated.',
         '前处理药剂与粉末是相互对着开发的。皮膜与粉末出自同一家，附着力与盐雾数据才是可重复的，而不是谈出来的。')}</p>
    <p>{t('It also shortens the debugging loop: if a batch fails adhesion, there is one电话 to make instead of a three-way meeting.',
         '它也缩短排障链路：附着力出问题，只打一个电话，不用开三方会议。')}</p></div>
  <figure class="figure"><img src="{base}assets/img/factory-detail.jpg" alt="{t('Production line detail','产线细节')}" loading="lazy" decoding="async"><figcaption>{t('Powder line — detail','粉末产线细节')}</figcaption></figure>
</div></section>

<section class="section dark"><div class="wrap" style="display:flex;justify-content:space-between;gap:22px;align-items:center;flex-wrap:wrap">
  <h2 style="margin:0">{t('Ask for the full chain, not just the powder.','要整条链，不只买粉。')}</h2>
  <a class="btn on-dark" href="contact.html">{t('Talk to a process engineer','对接工艺工程师')}</a>
</div></section>"""
    write_page(lang, base, sub, "integrated.html",
        L(lang,"Integrated Surface Finishing — Pre-treatment, Anodising Chemistry, Powder | Baolilai",
                 "一体化表面处理 — 前处理、阳极氧化药剂、粉末 | 宝利莱"),
        L(lang,"Integrated metal finishing: pre-treatment chemistry (degrease, silane/zirconium, chrome-free passivation), anodising chemicals and powder coatings from one group.",
                 "金属表面处理一体化：前处理药剂（脱脂、硅烷陶化、无铬钝化）、阳极氧化药剂与粉末涂料，同一集团供应。"), body)


def pg_pvdf(lang, base, sub):
    t = lambda en, cn: L(lang, en, cn)
    builds = [
        ("2C1B", t("Primer + top coat, one bake","底漆 + 面漆，一烘"),
         t("Solid colours","素色"), "5–8 / 25–30 µm", "232 °C × 10–20 min"),
        ("3C1B", t("Primer + top + clear, one bake","底漆 + 面漆 + 清漆，一烘"),
         t("Metallic and pearl","金属漆 / 珍珠漆"), "5–8 / 25–30 / 10–13 µm", "232 °C × 10–20 min"),
        ("4C2B", t("Primer + mid + top + clear, two bakes","底漆 + 中涂 + 面漆 + 清漆，两烘"),
         t("High-spec façades, colour depth","高要求幕墙、深色"), "5–8 / 15–20 / 25–30 / 10–13 µm", "232 °C × 5–10 + 10–20 min"),
    ]
    brow = "".join(f"<tr><td><b>{a}</b></td><td>{b}</td><td>{c}</td><td>{d}</td><td>{e}</td></tr>" for a,b,c,d,e in builds)
    cmp_rows = [
        (t("Film build","膜厚"), t("80–120 µm total, multi-layer","总膜厚 80–120 µm，多层"),
         t("60–90 µm single coat","60–90 µm 单层")),
        (t("Application","施工"), t("Spray, 2–4 coats, flash-off between","喷涂 2–4 道，道间静置"),
         t("Electrostatic powder, one pass","静电粉末，一次成膜")),
        (t("Bake","烘烤"), "232 °C", t("180–200 °C (130 °C low-temp option)","180–200 ℃（可选 130 ℃ 低温）")),
        (t("Tested to","对标送检"), t("AAMA 2605 items","AAMA 2605 测试项"), t("P2000: same class of test items","P2000：同类测试项")),
        (t("Design life","设计年限"), t("20 years+","20 年以上"), t("Up to 20 years (P2000)","最高 20 年（P2000）")),
        (t("Best at","最适合"), t("Class-A surfaces, metallic/pearl depth, complex colour","Class-A 外观、金属珍珠的层次感、复杂颜色"),
         t("Edge coverage, thick film, no solvent, high utilisation","边角覆盖、厚膜、无溶剂、高利用率")),
        (t("Weak at","弱在"), t("Solvent handling, oven load, per-square-metre cost","溶剂管理、烘炉负荷、单位面积成本"),
         t("Metallic depth on large flat panels","大面积平板的金属层次")),
    ]
    crow = "".join(f"<tr><td>{a}</td><td>{b}</td><td>{c}</td></tr>" for a,b,c in cmp_rows)
    body = f"""
<section class="section" style="padding-top:150px"><div class="wrap">
  <span class="eyebrow">{t('Liquid line · PVDF fluorocarbon','液体线 · PVDF 氟碳')}</span>
  <h1 style="font-size:clamp(30px,4.2vw,50px)">{t('For façades that must not change.','给不能变色的幕墙。')}</h1>
  <p class="lead">{t('PVDF is the liquid fluorocarbon system behind most of the world’s high-end aluminium architecture. Baked at 232 °C, built in two to four coats, and specified by the AAMA 2605 class. It is the other half of what Polyshine supplies — the powder range gets you 95% of the way; PVDF is for the façade that is the brand.',
      'PVDF 是全球高端铝建筑幕墙背后的液体氟碳体系：232 ℃ 烘烤、二至四道涂层、按 AAMA 2605 等级指定。它是宝利鑫三条线里的另一半——粉末能覆盖 95% 的场景，PVDF 用于"外立面本身就是品牌"的项目。')}</p>
  <div class="grid g4" style="margin-top:40px">
    <div class="stat" style="background:var(--surface)"><b style="font-size:30px;font-weight:300;color:var(--p700)">≥ 70%</b><small>{t('PVDF in total resin solids','PVDF 占树脂固体比例')}</small></div>
    <div class="stat" style="background:var(--surface)"><b style="font-size:30px;font-weight:300;color:var(--p700)">232 °C</b><small>{t('Bake temperature','烘烤温度')}</small></div>
    <div class="stat" style="background:var(--surface)"><b style="font-size:30px;font-weight:300;color:var(--p700)">AAMA 2605</b><small>{t('Test items (no certificate)','测试项（非认证）')}</small></div>
    <div class="stat" style="background:var(--surface)"><b style="font-size:30px;font-weight:300;color:var(--p700)">20 yr+</b><small>{t('Design life','设计年限')}</small></div>
  </div>
</div></section>

<section class="section alt"><div class="wrap">
  <span class="eyebrow">{t('Coating build','涂装配套')}</span>
  <h2>{t('The system, not just the top coat.','卖的是配套，不只是面漆。')}</h2>
  <p class="lead">{t('PVDF performance depends on the whole build: primer for adhesion and corrosion, top coat for colour and UV, clear coat for metallic protection. Film thicknesses below are the specification, not a suggestion.',
      'PVDF 的性能取决于整套配套：底漆负责附着与防腐，面漆负责颜色与耐候，清漆保护金属颜料。下表的膜厚是规格，不是建议值。')}</p>
  <div class="scroll" style="margin-top:30px"><table>
    <thead><tr><th>{t('System','体系')}</th><th>{t('Layers','涂层结构')}</th><th>{t('Use','适用')}</th><th>{t('Dry film','干膜厚度')}</th><th>{t('Bake','固化')}</th></tr></thead>
    <tbody>{brow}</tbody></table></div>
  <p class="note" style="margin-top:16px">{t('Primer: KYF-30001 / 30002 / 32222 · Top: KYF-3XXXX colour range · Clear: KYF-30000.','底漆：KYF-30001 / 30002 / 32222 · 面漆：KYF-3XXXX 色漆系列 · 清漆：KYF-30000。')}</p>
</div></section>

<section class="section"><div class="wrap">
  <span class="eyebrow">{t('Four process rules','四条工艺铁律')}</span>
  <div class="steps" style="margin-top:26px">
    <div class="step"><div class="n"></div><div><h3>{t('Metallic and pearl always need a clear coat','金属漆与珍珠漆必须罩光')}</h3>
      <p>{t('Aluminium pigment oxidises under acid rain and industrial atmosphere. Without a clear coat the face loses brightness before the warranty period ends.',
           '铝颜料在酸雨与工业大气下会氧化。不罩光，外观会在质保期内先失光。')}</p></div></div>
    <div class="step"><div class="n"></div><div><h3>{t('Pearl colour shifts with film thickness','珍珠漆的色差跟着膜厚走')}</h3>
      <p>{t('Pearl pigments change hue as the film gets thicker. Uniform film build, and a primer tinted to match the top coat, are the only way to hold colour across a façade.',
           '珍珠颜料的色相随膜厚变化。唯一的办法是膜厚均匀 + 底漆颜色与面漆匹配。')}</p></div></div>
    <div class="step"><div class="n"></div><div><h3>{t('Orange, red and yellow need protection','橙红黄必须加保护')}</h3>
      <p>{t('The inorganic pigments behind these colours weather faster. A clear coat is recommended even on solid colours.',
           '这类颜色用的无机颜料耐候性偏弱，即使是素色也建议加清漆。')}</p></div></div>
    <div class="step"><div class="n"></div><div><h3>{t('Film build is a performance parameter','膜厚是性能参数')}</h3>
      <p>{t('Below the specified thickness the anti-contamination and salt-spray behaviour drop off. Measure on the part, not on the test panel.',
           '低于规定膜厚，抗污染与盐雾表现会下降。测工件，不要只测试板。')}</p></div></div>
  </div>
</div></section>

<section class="section alt"><div class="wrap">
  <span class="eyebrow">{t('PVDF or powder','PVDF 还是粉末')}</span>
  <h2>{t('Two systems, one quote.','两套体系，一份报价。')}</h2>
  <div class="scroll" style="margin-top:28px"><table>
    <thead><tr><th>{t('Item','项目')}</th><th>PVDF {t('liquid','液体')}</th><th>{t('Powder (P2000)','粉末（P2000）')}</th></tr></thead>
    <tbody>{crow}</tbody></table></div>
  <p class="note" style="margin-top:10px">{t('We hold no AAMA or QUALICOAT product certificate for either system. The test report is what we can send you today.','两套体系我们都不持有 AAMA 或 QUALICOAT 产品证书，目前能提供的是检测报告。')}</p>
  <p class="note" style="margin-top:16px">{t('Most projects do not need to choose globally: powder for profiles and secondary components, PVDF for the visible Class-A panels, is a normal split.',
      '多数项目不需要全局二选一：型材与次要件用粉末、可见的 Class-A 平板用 PVDF，是常见的组合。')}</p>
</div></section>

<section class="section"><div class="wrap split">
  <div><span class="eyebrow">{t('How it is supplied','怎么供货')}</span>
    <h2>{t('One group, two production lines.','一个集团，两条产线。')}</h2>
    <p>{t('The PVDF line is part of Polyshine Technology, alongside the powder plant at Baolilai and the pre-treatment chemistry. A façade package — chemistry, powder for the profiles, PVDF for the panels — can be quoted with one set of documents and one responsible party.',
         'PVDF 产线属于宝利鑫科技，与宝利莱粉末厂、前处理药剂同属一个集团。幕墙整套——药剂、型材用粉、平板用 PVDF——可以一份文件、一个责任主体报出去。')}</p>
    <p class="note">{t('Ask for the AAMA 2605 test report with your colour and gloss level; the class only means something when it is tied to a specific product and build.','索取与你颜色、光泽对应的 AAMA 2605 检测报告——等级只有绑定到具体产品与配套时才有意义。')}</p>
    <a class="btn" href="contact.html">{t('Request a façade package','索取幕墙配套方案')}</a></div>
  <figure class="figure"><img src="{base}assets/img/facade-panels.jpg" alt="{t('PVDF coated façade panels','PVDF 喷涂幕墙板')}" loading="lazy" decoding="async"><figcaption>{t('Coated façade panels','喷涂幕墙板')}</figcaption></figure>
</div></section>

<section class="section dark"><div class="wrap" style="display:flex;justify-content:space-between;gap:22px;align-items:center;flex-wrap:wrap">
  <h2 style="margin:0">{t('Send the panel spec, we will pick the system.','发板件规格，我们定体系。')}</h2>
  <a class="btn on-dark" href="contact.html">{t('Talk to us','联系我们')}</a>
</div></section>"""
    write_page(lang, base, sub, "pvdf.html",
        L(lang,"PVDF Fluorocarbon Liquid Coatings — AAMA 2605, 2C1B/3C1B/4C2B | Baolilai",
                 "PVDF 氟碳液体涂料 — AAMA 2605，二涂/三涂/四涂 | 宝利莱"),
        L(lang,"PVDF fluorocarbon coatings for aluminium façades: 70% PVDF, 232 °C bake, AAMA 2605 / QUALICOAT III, 20-year design life, 2C1B / 3C1B / 4C2B builds.",
                 "铝幕墙用 PVDF 氟碳涂料：PVDF 占比 70%、232 ℃ 烘烤、AAMA 2605 / QUALICOAT III、设计年限 20 年，二涂/三涂/四涂配套。"), body)


def pg_automotive(lang, base, sub):
    t = lambda en, cn: L(lang, en, cn)
    parts = [
        (t("Engine components","发动机件"), t("Heat and oil resistance, tight tolerances","耐热耐油、尺寸精度高")),
        (t("Aluminium wheels","铝轮毂"), t("Class-A face, stone-chip resistance, UV","正面外观、抗石击、耐紫外")),
        (t("Suspension springs","减震弹簧"), t("Flexibility plus impact — coating must bend with the part","柔韧+抗冲击，涂层要跟着件弯")),
        (t("Chassis &amp; underbody","底盘与车底"), t("Salt spray 1000 h, gravel impact","盐雾 1000h、碎石冲击")),
        (t("Filters","滤清器"), t("Chemical resistance, thin uniform film","耐化学、薄膜均匀")),
        (t("Control levers","操纵杆"), t("Wear resistance, grip feel","耐磨、手感")),
        (t("Mirrors &amp; trim","后视镜与饰件"), t("Colour match, gloss consistency","颜色匹配、光泽一致")),
        (t("Wiper arms","雨刮臂"), t("Detergent and UV resistance","耐洗涤剂、耐紫外")),
        (t("Horns &amp; small parts","喇叭与小件"), t("Edge coverage on complex shapes","复杂件边角覆盖")),
    ]
    part_html = "".join(f"<div class='card rv'><div class='body'><h3 style='font-size:18px'>{a}</h3><p>{b}</p></div></div>" for a,b in parts)
    chem = [
        ("Epoxy", t("Best corrosion and chemical resistance; interior parts only","防腐耐化学最强；仅室内件")),
        ("Epoxy-polyester", t("Balance of cost and appearance; interior and sheltered","性价比与外观平衡；室内与遮蔽区")),
        ("Polyester", t("Exterior durability, UV and gloss retention","户外耐候、保光保色")),
        ("Polyurethane", t("Flow and appearance, low bake possible","流平与外观好，可低温")),
        ("Acrylic", t("Highest gloss retention and clarity","保光性最好、通透")),
    ]
    chem_html = "".join(f"<tr><td><b>{a}</b></td><td>{b}</td></tr>" for a,b in chem)
    body = f"""
<section class="section" style="padding-top:150px"><div class="wrap">
  <span class="eyebrow">{t('Automotive &amp; parts','汽车及零部件')}</span>
  <h1 style="font-size:clamp(30px,4.2vw,50px)">{t('Parts that fail in service, not in the showroom.','零件是在路上失效的，不是在展厅。')}</h1>
  <p class="lead">{t('Automotive coating is a specification business: salt spray, stone chip, detergent, UV, and a colour that has to match a master panel three years later. We supply the five chemistries that cover the part list below, with the test data attached.',
      '汽车涂装是规格生意：盐雾、石击、洗涤剂、紫外，以及三年后仍要对得上标准板的颜色。下面这些零件，我们用五种体系覆盖，并把检测数据一起给你。')}</p>
  <div class="grid g3" style="margin-top:42px">{part_html}</div>
</div></section>

<section class="section alt"><div class="wrap">
  <span class="eyebrow">{t('Five chemistries','五种体系')}</span>
  <h2>{t('Pick the chemistry by where the part lives.','按零件装在哪来选体系。')}</h2>
  <div class="scroll" style="margin-top:30px"><table>
    <thead><tr><th>{t('Chemistry','体系')}</th><th>{t('Where it belongs','适用位置')}</th></tr></thead>
    <tbody>{chem_html}</tbody></table></div>
  <p class="note" style="margin-top:16px">{t('The same part can need two different systems depending on whether it sees road salt or engine heat. Send the drawing and the service condition, not just the part name.',
      '同一个零件，见不见路盐、受不受发动机热，选的体系可能完全不同。发图纸和使用工况，不要只发零件名。')}</p>
</div></section>

<section class="section"><div class="wrap">
  <span class="eyebrow">{t('What gets tested','测什么')}</span>
  <h2>{t('The five numbers a tier-one buyer asks for.','一级供应商一定会问的五个数。')}</h2>
  <div class="grid g2" style="margin-top:34px">
    <div><h3>{t('Corrosion','防腐')}</h3><p class="lead">{t('Neutral salt spray 500–1000 h depending on part class and film build.','中性盐雾 500–1000h，视零件等级与膜厚。')}</p></div>
    <div><h3>{t('Stone chip','抗石击')}</h3><p class="lead">{t('Gravel impact per the OEM standard the part is released against.','按该零件对应的主机厂标准做碎石冲击。')}</p></div>
    <div><h3>{t('Chemical','耐化学')}</h3><p class="lead">{t('Engine oil, brake fluid, coolant, detergent — each with a method and a time.','机油、制动液、冷却液、洗涤剂，每项带方法与时间。')}</p></div>
    <div><h3>{t('Appearance','外观')}</h3><p class="lead">{t('Gloss, DOI and ΔE against the approved master panel.','光泽、鲜映性与 ΔE，对照签样标准板。')}</p></div>
  </div>
  <p class="note" style="margin-top:22px">{t('We are not IATF 16949 certified today. If a programme requires it, we will say so at the quoting stage rather than after the audit. For aftermarket and non-critical parts, PPAP-level documentation can be discussed case by case.',
      '我们目前没有 IATF 16949 认证。项目要求时，我们会在报价阶段就说清楚，而不是等到审核那天。售后件与非关键件，PPAP 级文件可以逐案讨论。')}</p>
</div></section>

<section class="section dark"><div class="wrap" style="display:flex;justify-content:space-between;gap:22px;align-items:center;flex-wrap:wrap">
  <h2 style="margin:0">{t('Send the drawing and the service condition.','发图纸和使用工况。')}</h2>
  <a class="btn on-dark" href="contact.html">{t('Discuss an automotive part','沟通汽车件')}</a>
</div></section>"""
    write_page(lang, base, sub, "automotive.html",
        L(lang,"Automotive & Parts Powder Coatings — Wheels, Springs, Chassis | Baolilai",
                 "汽车及零部件粉末涂料 — 轮毂、弹簧、底盘 | 宝利莱"),
        L(lang,"Powder coatings for automotive parts: epoxy, epoxy-polyester, polyester, PU and acrylic systems for wheels, springs, chassis, filters and trim.",
                 "汽车零部件粉末涂料：环氧、环氧聚酯、聚酯、PU、丙烯酸五种体系，用于轮毂、弹簧、底盘、滤清器与饰件。"), body)

def pg_downloads(lang, base, sub):
    t = lambda en, cn: L(lang, en, cn)
    rows = []
    for p in PRODUCTS:
        s = series_of(p["series"])
        fp = os.path.join(OUT, "assets", "tds", p["code"] + "_TDS.pdf")
        size = ("%.0f KB" % (os.path.getsize(fp) / 1024.0)) if os.path.exists(fp) else "—"
        rows.append(f"""<tr>
      <td><b>{p['code']}</b></td>
      <td>{L(lang, p['en'], p['cn'])}</td>
      <td>{s['code']} {L(lang, s['en'], s['cn'])}</td>
      <td>{p['ral']}</td><td>{p['dft']}</td><td>{p['cure']}</td>
      <td style="white-space:nowrap"><a class="btn ghost sm" href="{base}assets/tds/{p['code']}_TDS.pdf" download>TDS · PDF</a>
        <span class="note" style="display:block;margin-top:7px">{size} · 4 pp. · EN + 中文</span></td></tr>""")
    rows = "".join(rows)

    inside = [
        ("Identity", "身份", t("Code, product name, series, colour reference and revision — so a purchase order and a data sheet can be matched without interpretation.",
                              "编号、品名、系列、参照色与版本——采购单与数据表能直接对上，不用猜。")),
        ("Typical properties", "典型性能", t("Chemistry, gloss, film build, density, cure schedule, particle size, stoving loss, storage stability — and coverage in m²/kg, not just price per kilo.",
                                             "体系、光泽、膜厚、比重、固化条件、粒径、烘烤失重、贮存稳定性——以及 m²/kg 覆盖率，不只讲每公斤多少钱。")),
        ("Performance data", "性能数据", t("Each test carries its method (ISO / ASTM) next to the value. Where we have not run a test, the sheet says so instead of leaving it out.",
                                          "每项测试的方法（ISO / ASTM）都与数值并列。没做的测试，表里写明没做，而不是删掉不提。")),
        ("Application and cure", "施工与固化", t("Pre-treatment per substrate, gun settings, film build, and cure stated as object temperature — the number that actually decides whether the film is cured.",
                                                "按基材写前处理、枪参数、膜厚，固化一栏写工件温度——真正决定涂层是否固化的是这个数，不是炉膛显示。")),
        ("Packing, storage, safety", "包装、贮存、安全", t("Pack size, shelf life, combustible-dust precautions, cure volatiles, and where the SDS comes from.",
                                                        "包装规格、保质期、可燃粉尘防护、固化挥发物，以及 SDS 从哪来。")),
        ("Limits", "边界", t("What the product is not for, and what the document is not: no AAMA / QUALICOAT / GSB / UL certificate is claimed anywhere.",
                            "这款产品不适合用在什么场合，以及这份文件不是什么：任何地方都不宣称持有 AAMA / QUALICOAT / GSB / UL 证书。")),
    ]
    inside_html = "".join(
        f"""<div class="card rv"><div class="body"><span class="kicker">0{i}</span>
        <h3 style="font-size:18px">{L(lang, x[0], x[1])}</h3><p>{L(lang, x[2][0], x[2][1])}</p></div></div>"""
        for i, x in enumerate(inside, 1))

    body = f"""
<section class="section" style="padding-top:150px"><div class="wrap">
  <span class="eyebrow">{t('Documents · technical data','技术资料')}</span>
  <h1 style="font-size:clamp(30px,4.2vw,50px)">{t('Take the data sheet before you take the price.','先拿数据表，再谈价格。')}</h1>
  <p class="lead">{t('Six products, one data sheet each: four pages, English and 中文 in the same file, real text you can search and quote. Every sheet carries the test method next to the value, and states plainly what the product is not for.',
      '六个产品，各一份数据表：四页，英文与中文在同一个文件里，是可检索、可引用的真实文字。每项数值旁边都有测试方法，并明确写出这款产品不适合用在什么场合。')}</p>
  <p class="note" style="margin-top:20px;max-width:78ch">{t('A TDS is not a certificate. We hold no AAMA / QUALICOAT / GSB / UL product certificate, and every sheet says so on page 2 — including the test reports we can send instead.',
      'TDS 不是证书。我们不持有 AAMA / QUALICOAT / GSB / UL 产品认证证书，每份数据表第 2 页都写明这一点——同时写明我们能提供哪些检测报告。')}</p>
</div></section>

<section class="section alt tight"><div class="wrap">
  <div class="scroll"><table>
    <thead><tr>
      <th>{t('Code','编号')}</th><th>{t('Product','产品')}</th><th>{t('Series','系列')}</th>
      <th>{t('Colour','颜色')}</th><th>{t('Film build','膜厚')}</th><th>{t('Cure','固化')}</th>
      <th>{t('Download','下载')}</th>
    </tr></thead>
    <tbody>{rows}</tbody>
  </table></div>
  <p class="note" style="margin-top:16px">{t('One file per product: pages 1–2 English, pages 3–4 中文. Text is selectable, so the numbers can be pasted into a tender document.',
      '每个产品一个文件：第 1–2 页英文，第 3–4 页中文。文字可选中，数值可直接复制进标书。')}</p>
</div></section>

<section class="section"><div class="wrap">
  <span class="eyebrow">{t('Inside a sheet','一份表里有什么')}</span>
  <h2>{t('Six sections, in the order a buyer reads them.','六节，按采购方会读的顺序排。')}</h2>
  <div class="grid g3" style="margin-top:40px">{inside_html}</div>
</div></section>

<section class="section alt"><div class="wrap split">
  <div>
    <span class="eyebrow">{t('Using it in a tender','标书里怎么用')}</span>
    <h2>{t('Three things a data sheet decides.','数据表能定下的三件事。')}</h2>
    <div class="steps" style="margin-top:28px">
      <div class="step"><div class="n"></div><div><h3>{t('Fix the acceptance values','锁定验收值')}</h3>
        <p>{t('The sheet gives typical values. The purchase specification fixes the acceptance values — write them from the trial report, not from this page, so nobody argues at inspection.',
             '表里是典型值，采购规格才是验收值——从试粉报告里抄，不要从这一页抄，检验那天才不会吵。')}</p></div></div>
      <div class="step"><div class="n"></div><div><h3>{t('Prove the method','证明方法')}</h3>
        <p>{t('Each value carries an ISO or ASTM method. A tender that names a method can be answered with a report; a tender that names a certificate cannot — ask us early and we will say which one we can do.',
             '每个数值都带 ISO 或 ASTM 方法号。点名方法的标书可以用报告回答；点名证书的标书不能——早点问，我们会直接说哪一条能做到。')}</p></div></div>
      <div class="step"><div class="n"></div><div><h3>{t('Name the substrate and the pre-treatment','写上基材与前处理')}</h3>
        <p>{t('Salt spray and adhesion numbers in this sheet assume a conversion-coated substrate. Quoting the powder without the pre-treatment line is how a 1,000 h claim becomes a 300 h argument.',
             '本表的盐雾与附着力数据，前提是基材做了转化膜。只报粉末、不写前处理线，1000 h 的承诺就会变成 300 h 的争吵。')}</p></div></div>
    </div>
  </div>
  <figure class="figure rv">
    <div class="ralswatch" style="background:{hexof('RAL 7035')}"><span>RAL 7035 · {nameof(lang,'RAL 7035')}</span></div>
    <figcaption>{t('Swatches in the sheets are digital approximations — approval is on a sprayed panel','表内色块为数字近似——以喷板确认为准')}</figcaption>
  </figure>
</div></section>

<section class="section"><div class="wrap">
  <span class="eyebrow">{t('What is not here','这里没有的东西')}</span>
  <h2>{t('Three documents we do not publish.','三份我们不公开的文件。')}</h2>
  <div class="grid g3" style="margin-top:34px">
    <div><h3>{t('Certificates','认证证书')}</h3><p class="lead">{t('No AAMA 2603/2604/2605, QUALICOAT, GSB or UL product certificate. We test to those methods and hold third-party reports; the certificate itself we do not have.',
      '没有 AAMA 2603/2604/2605、QUALICOAT、GSB 或 UL 产品认证证书。我们按这些方法检测、持有第三方报告；证书本身没有。')}</p></div>
    <div><h3>{t('SDS','SDS 安全数据表')}</h3><p class="lead">{t('Issued per product and per colour, not published as a library — ask for the one that matches the material on your order, and it will carry that batch.',
      '按产品、按颜色逐份签发，不做公开下载库——请索取与你订单物料一致的那一份，会对应到具体批次。')}</p></div>
    <div><h3>{t('A warranty','质保承诺')}</h3><p class="lead">{t('Design life on the durability page is a target tied to test data, pre-treatment and film build. It is not a warranty on its own, and we do not write one into a TDS.',
      '耐候等级页上的设计寿命，是与检测数据、前处理、膜厚绑定的目标值，本身不是质保；我们不会把质保写进 TDS。')}</p></div>
  </div>
</div></section>

<section class="section dark"><div class="wrap" style="display:flex;justify-content:space-between;gap:22px;align-items:center;flex-wrap:wrap">
  <div><span class="eyebrow">{t('Not on the list','不在清单里')}</span>
    <h2 style="margin:0">{t('Need a sheet for a colour, a texture or a system we have not published?','要某个颜色、纹理或体系的表，但没在这里？')}</h2></div>
  <a class="btn on-dark" href="contact.html">{t('Ask for a product-specific TDS','索取指定产品 TDS')}</a>
</div></section>"""
    write_page(lang, base, sub, "downloads.html",
        L(lang, "Technical Data Sheets — Download TDS (EN + 中文) | Baolilai",
                 "技术数据表下载 — TDS（英文 + 中文）| 宝利莱"),
        L(lang, "Download bilingual TDS for six powder coating products: typical properties, test methods and results, application and cure, packing and limits.",
                 "下载六款粉末涂料的中英双语 TDS：典型性能、测试方法与结果、施工与固化、包装与边界说明。"), body)


if __name__ == "__main__":
    main()
