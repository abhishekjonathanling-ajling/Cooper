#!/usr/bin/env python3
"""Static build for the Cooper Technology Group site.

    python3 build.py            -> dist/      (production: full HTML documents)
    python3 build.py --artifact -> artifact/  (same site, index page without
                                               its own document skeleton)
"""
import json, math, os, re, shutil, sys, datetime, html
from jinja2 import Environment, FileSystemLoader

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "src")
sys.path.insert(0, SRC)
import data as D          # noqa: E402
from posts import POSTS   # noqa: E402

ARTIFACT = "--artifact" in sys.argv
OUT = os.path.join(ROOT, "artifact" if ARTIFACT else "dist")
SITE = "https://coopertechnologygroup.com"
VERSION = datetime.datetime.now().strftime("%Y%m%d%H%M")
YEAR = 2026

# ------------------------------------------------------------------ images
IMG_DIR = os.path.join(ROOT, "assets", "img")
meta = json.load(open(os.path.join(ROOT, "imgmeta.json")))
IMG = {}
for name, (w, h) in meta.items():
    widths = sorted(int(m.group(1)) for f in os.listdir(IMG_DIR)
                    for m in [re.match(re.escape(name) + r"-(\d+)\.webp$", f)] if m)
    if not widths:
        continue
    IMG[name] = {"w": 1600, "h": round(h * 1600 / w), "widths": widths,
                 "mid": 1600 if 1600 in widths else widths[-1]}

# ------------------------------------------------------------------ map
def build_map():
    lon0, lon1, lat0, lat1 = -75.45, -73.85, 40.22, 41.12
    W = 1000
    kx = W / (lon1 - lon0)
    ky = kx / math.cos(math.radians(40.67))
    H = round((lat1 - lat0) * ky)
    X = lambda lon: (lon - lon0) * kx
    Y = lambda lat: (lat1 - lat) * ky
    px_per_km = W / ((lon1 - lon0) * 111.32 * math.cos(math.radians(40.67)))
    out = [f'<div class="map"><svg viewBox="0 0 {W} {H}" role="img" aria-labelledby="map-t map-d" preserveAspectRatio="xMidYMid meet">',
           '<title id="map-t">Cooper Technology Group service area</title>',
           '<desc id="map-d">Office in Alpha, New Jersey, with rings at 15, 30, 45 and 60 miles covering North and Central New Jersey, Eastern Pennsylvania and New York City.</desc>']
    lon = -75.4
    while lon < lon1:
        x = X(lon); out.append(f'<line class="grid-l" x1="{x:.1f}" y1="0" x2="{x:.1f}" y2="{H}"/>')
        out.append(f'<text class="tick" x="{x+4:.1f}" y="{H-8}">{abs(lon):.1f}°W</text>')
        lon = round(lon + 0.2, 2)
    lat = 40.3
    while lat < lat1:
        y = Y(lat); out.append(f'<line class="grid-l" x1="0" y1="{y:.1f}" x2="{W}" y2="{y:.1f}"/>')
        out.append(f'<text class="tick" x="6" y="{y-5:.1f}">{lat:.1f}°N</text>')
        lat = round(lat + 0.2, 2)
    hx, hy = X(D.HQ[1]), Y(D.HQ[0])
    for mi in (15, 30, 45, 60):
        r = mi * 1.609 * px_per_km
        out.append(f'<circle class="ring" cx="{hx:.1f}" cy="{hy:.1f}" r="{r:.1f}"/>')
        out.append(f'<text class="tick" x="{hx + r*0.707 + 4:.1f}" y="{hy - r*0.707 - 4:.1f}">{mi} mi</text>')
    for txt, la, lo in (("North Jersey", 40.98, -74.95), ("Central NJ", 40.40, -74.98), ("NYC", 40.88, -74.12), ("Eastern PA", 40.42, -75.40)):
        out.append(f'<text class="region" x="{X(lo):.1f}" y="{Y(la):.1f}">{txt}</text>')
    for la, lo, name, anchor in D.TOWNS:
        x, y = X(lo), Y(la)
        dx = 9 if anchor == "start" else -9
        out.append(f'<g class="town"><circle cx="{x:.1f}" cy="{y:.1f}" r="3"/><text x="{x+dx:.1f}" y="{y+4:.1f}" text-anchor="{anchor}">{name}</text></g>')
    out.append(f'<g class="hq"><circle class="pulse" cx="{hx:.1f}" cy="{hy:.1f}" r="7"/><circle class="core" cx="{hx:.1f}" cy="{hy:.1f}" r="7"/>'
               f'<text x="{hx-8:.1f}" y="{hy+34:.1f}">Cooper, Alpha NJ</text></g>')
    out.append('</svg>')
    out.append('<div class="map__legend"><span class="mono">1603 Springtown Rd</span><span class="mono">40.67° N, 75.16° W</span></div></div>')
    return "\n".join(out)

with open(os.path.join(SRC, "templates", "_map.html"), "w") as f:
    f.write(build_map())

# ------------------------------------------------------------------ posts
for p in POSTS:
    words = len(re.sub(r"<[^>]+>", " ", p["body"]).split())
    p["read"] = max(2, round(words / 230))
    d = datetime.date.fromisoformat(p["date"])
    p["date_h"] = d.strftime("%B %-d, %Y")
CATS = []
for p in POSTS[1:]:
    if p["cat"] not in CATS:
        CATS.append(p["cat"])

# ------------------------------------------------------------------ structured data
LD = {
    "@context": "https://schema.org", "@type": "HomeAndConstructionBusiness",
    "@id": SITE + "/#business", "name": "Cooper Technology Group", "url": SITE + "/",
    "telephone": "+1-877-266-7379",
    "image": SITE + "/assets/img/og-hero-dusk.jpg",
    "address": {"@type": "PostalAddress", "streetAddress": "1603 Springtown Rd", "addressLocality": "Alpha",
                "addressRegion": "NJ", "postalCode": "08865-4631", "addressCountry": "US"},
    "geo": {"@type": "GeoCoordinates", "latitude": 40.667, "longitude": -75.157},
    "areaServed": ["North Jersey", "Central New Jersey", "Eastern Pennsylvania", "New York City"],
    "description": "Security and surveillance, access control, smart home automation, home theater, multi-room audio and commercial AV systems for homes and businesses in New Jersey and NYC.",
    "knowsAbout": ["Home security systems", "Smart home automation", "Access control", "Commercial security systems",
                   "Home theater installation", "Multi-room audio", "Commercial AV systems", "Fire alarm systems"],
}

# ------------------------------------------------------------------ pages
PAGES = [
    dict(id="home", section="home", tpl="index.html", path="", out="index.html", nav="light", theme="paper", preload="hero-dusk",
         title="Cooper Technology Group | Smart Home, Security & AV Systems in New Jersey",
         og_title="Cooper Technology Group: technology, quietly integrated",
         description="Security, surveillance, access control, smart home automation, home theater and commercial AV systems, designed and installed across North and Central New Jersey and NYC for over 30 years."),
    dict(id="about", section="about", tpl="about.html", path="about.html", out="about.html", nav="dark", theme="paper", og_image="blueprint",
         title="About | 30+ Years of Security & Integration in New Jersey | Cooper Technology Group",
         description="For over 30 years Cooper Technology Group has designed, installed and serviced security, fire, automation and AV systems for homes and businesses across New Jersey, Eastern Pennsylvania and NYC."),
    dict(id="residential", section="residential", tpl="residential.html", path="residential.html", out="residential.html", nav="light", theme="paper", preload="dusk-lawn", og_image="dusk-lawn",
         title="Smart Home Automation & Home Security Systems NJ | Cooper Technology Group",
         description="Home security systems, smart locks, Control4 home automation, lighting and shade control, home theater installation and multi-room audio for homes in North and Central New Jersey."),
    dict(id="commercial", section="commercial", tpl="commercial.html", path="commercial.html", out="commercial.html", nav="light", theme="night", og_image="towers",
         title="Commercial Security Systems, Access Control & AV in NJ & NYC | Cooper Technology Group",
         description="Commercial security and fire alarm systems, surveillance, access control and commercial AV for schools, offices, practices, clubs and retail across New Jersey and New York City."),
    dict(id="services", section="services", tpl="services.html", path="services.html", out="services.html", nav="dark", theme="paper",
         title="Services | Security, Automation, Access Control & AV | Cooper Technology Group",
         description="Fourteen residential and commercial services: security and surveillance, smart locks, home automation, lighting, home theater, multi-room audio, access control and commercial AV in New Jersey."),
    dict(id="blog", section="blog", tpl="blog.html", path="blog.html", out="blog.html", nav="dark", theme="paper", og_image="rack",
         title="Journal | Smart Home, Security & AV Advice | Cooper Technology Group",
         description="Practical articles on home security, surveillance cameras, Wi-Fi, smart locks, home theater and commercial systems, from the team that installs them in New Jersey."),
    dict(id="contact", section="contact", tpl="contact.html", path="contact.html", out="contact.html", nav="dark", theme="paper",
         title="Contact | (877) 266-7379 | Cooper Technology Group, Alpha NJ",
         description="Start a project with Cooper Technology Group. Call (877) 266-7379 or send project details. 1603 Springtown Rd, Alpha, NJ 08865, serving New Jersey and NYC."),
]
for i, p in enumerate(POSTS):
    related = [POSTS[(i + k) % len(POSTS)] for k in (1, 2, 3)]
    ld = {"@context": "https://schema.org", "@type": "Article", "headline": p["title"], "datePublished": p["date"],
          "author": {"@type": "Organization", "name": "Cooper Technology Group"},
          "publisher": {"@id": SITE + "/#business"}, "image": f"{SITE}/assets/img/og-{p['img']}.jpg",
          "mainEntityOfPage": f"{SITE}/{p['slug']}.html", "description": p["excerpt"]}
    PAGES.append(dict(id="article", section="blog", tpl="article.html", path=p["slug"] + ".html", out=p["slug"] + ".html",
                      nav="dark", theme="paper", og_type="article", og_image=p["img"], post=p, related=related,
                      title=f"{p['title']} | Cooper Technology Group", description=p["excerpt"],
                      ld=json.dumps(ld)))

# ------------------------------------------------------------------ render
env = Environment(loader=FileSystemLoader(os.path.join(SRC, "templates")), autoescape=True,
                  trim_blocks=False, lstrip_blocks=False)
G = dict(SITE=SITE, VERSION=VERSION, YEAR=YEAR, IMG=IMG, LD_JSON=json.dumps(LD), POSTS=POSTS, CATS=CATS,
         **{k: getattr(D, k) for k in dir(D) if k.isupper()})
env.globals.update(G)

if os.path.exists(OUT):
    shutil.rmtree(OUT)
os.makedirs(os.path.join(OUT, "assets", "img"))
shutil.copytree(os.path.join(SRC, "assets", "css"), os.path.join(OUT, "assets", "css"))
shutil.copytree(os.path.join(SRC, "assets", "js"), os.path.join(OUT, "assets", "js"))
for f in os.listdir(IMG_DIR):
    shutil.copy2(os.path.join(IMG_DIR, f), os.path.join(OUT, "assets", "img", f))

def tidy(s):
    s = re.sub(r"\n\s*\n+", "\n", s)
    return s.strip() + "\n"

for pg in PAGES:
    tpl = env.get_template(pg["tpl"])
    is_root = ARTIFACT and pg["out"] == "index.html"
    if is_root:
        pg = dict(pg, title="Cooper Technology Group")
    s = tpl.render(page=pg, ARTIFACT_ROOT=is_root)
    with open(os.path.join(OUT, pg["out"]), "w") as f:
        f.write(tidy(s))

# prune images no page references
used = set()
for fn in os.listdir(OUT):
    if fn.endswith(".html"):
        used |= set(re.findall(r"assets/img/([\w.-]+?\.(?:webp|jpg))", open(os.path.join(OUT, fn)).read()))
for fn in os.listdir(os.path.join(OUT, "assets", "img")):
    if fn not in used:
        os.remove(os.path.join(OUT, "assets", "img", fn))

# sitemap + robots (production only)
if not ARTIFACT:
    urls = "".join(f"<url><loc>{SITE}/{p['path']}</loc></url>" for p in PAGES)
    open(os.path.join(OUT, "sitemap.xml"), "w").write(
        f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n')
    open(os.path.join(OUT, "robots.txt"), "w").write(f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n")

print("built", len(PAGES), "pages ->", OUT)
