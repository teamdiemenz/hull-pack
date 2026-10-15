import json, os, random, zipfile, hashlib, sys, math
from PIL import Image, ImageDraw
R = sys.argv[1]  # repo dir
random.seed(7)
def w(path, data):
    p = os.path.join(R, path); os.makedirs(os.path.dirname(p), exist_ok=True)
    if isinstance(data, (dict, list)): data = json.dumps(data, indent=1)
    open(p, 'w').write(data)
w('pack/pack.mcmeta', {"pack": {"description": "The Hull test pack v0.2", "min_format": 75, "max_format": 75}})

def lerp(a, b, t): return tuple(int(a[i] + (b[i]-a[i])*t) for i in range(3))
# ---- relic lamp texture 16x16: brass (0,0,8,8) glow (8,0,16,8) dark (0,8,8,16)
t = Image.new('RGBA', (16, 16), (0, 0, 0, 255))
for x in range(8):
    for y in range(8):
        n = random.randint(-14, 14)
        base = lerp((120, 86, 40), (196, 150, 70), (x + y) / 14)
        t.putpixel((x, y), tuple(max(0, min(255, c + n)) for c in base) + (255,))
        d = ((x - 3.5) ** 2 + (y - 3.5) ** 2) ** .5 / 5
        g = lerp((255, 244, 190), (255, 130, 30), min(1, d))
        t.putpixel((x + 8, y), g + (255,))
        t.putpixel((x, y + 8), tuple(max(0, min(255, c + random.randint(-6, 6))) for c in (38, 34, 40)) + (255,))
for x in range(8, 16):
    for y in range(8, 16): t.putpixel((x, y), (255, 255, 255, 255))
os.makedirs(R + '/pack/assets/hull/textures/item', exist_ok=True)
t.save(R + '/pack/assets/hull/textures/item/relic_lamp.png')

def box(a, b, region, rot=None):
    uv = {"brass": [0, 0, 4, 4], "glow": [9, 1, 13, 5], "dark": [1, 9, 5, 13]}[region]
    e = {"from": a, "to": b, "faces": {f: {"uv": uv, "texture": "#0"} for f in ("north", "south", "east", "west", "up", "down")}}
    if rot: e["rotation"] = rot
    return e
els = [box([5, 0, 5], [11, 1.5, 11], "brass"), box([4, 1.5, 4], [12, 9.5, 12], "glow"),
       box([3.4, 1.5, 3.4], [4.6, 9.5, 4.6], "dark"), box([11.4, 1.5, 3.4], [12.6, 9.5, 4.6], "dark"),
       box([3.4, 1.5, 11.4], [4.6, 9.5, 12.6], "dark"), box([11.4, 1.5, 11.4], [12.6, 9.5, 12.6], "dark"),
       box([4.5, 9.5, 4.5], [11.5, 11, 11.5], "brass"), box([7, 11, 7], [9, 12.5, 9], "dark"),
       box([6.2, 12.5, 7.4], [9.8, 13.3, 8.6], "brass"), box([4, 6, 4], [12, 6.6, 12], "dark")]
w('pack/assets/hull/models/item/relic_lamp.json', {"textures": {"0": "hull:item/relic_lamp", "particle": "hull:item/relic_lamp"}, "elements": els,
  "display": {"gui": {"rotation": [20, 35, 0], "scale": [1.1, 1.1, 1.1], "translation": [0, -1, 0]},
              "ground": {"scale": [0.6, 0.6, 0.6], "translation": [0, 3, 0]},
              "thirdperson_righthand": {"scale": [0.7, 0.7, 0.7], "translation": [0, 2, 1]},
              "firstperson_righthand": {"scale": [0.7, 0.7, 0.7], "translation": [1, 2, 0]}}})
w('pack/assets/hull/items/relic_lamp.json', {"model": {"type": "minecraft:model", "model": "hull:item/relic_lamp"}})

# ---- moth v2 (pack v0.2). Texture is 64x64; model UVs are ALWAYS written in the 0..16 space
# (vanilla maps 0..16 onto the whole texture whatever its size), so every pixel rect goes through uvr().
# v0.1 bug: 32x32 texture with pixel-style UVs -> wings sampled the whole sheet (half transparent) and
# the body UVs ran past 16, so the wings looked cut off / detached.
S = 64
def uvr(x0, y0, x1, y1): return [x0 * 16 / S, y0 * 16 / S, x1 * 16 / S, y1 * 16 / S]
def clampc(c): return tuple(max(0, min(255, int(v))) for v in c)
m = Image.new('RGBA', (S, S), (0, 0, 0, 0))

def make_wing(poly, far, eye=None):
    W = 32
    mask = Image.new('L', (W, W), 0)
    ImageDraw.Draw(mask).polygon(poly, fill=255)
    mp = mask.load()
    img = Image.new('RGBA', (W, W), (0, 0, 0, 0))
    bx, by = W - 1, W * 0.55          # wing root: inner edge (u = W-1), middle
    for x in range(W):
        for y in range(W):
            if mp[x, y] == 0: continue
            d = math.hypot(x - bx, (y - by) * 0.9) / 30
            t = min(1, d)
            if t < .45: c = lerp((255, 224, 150), (40, 165, 175), t / .45)
            else: c = lerp((40, 165, 175), far, (t - .45) / .55)
            ang = (math.atan2(y - by, bx - x) * 9 / math.pi) % 1.0
            if ang < .13 or ang > .87: c = lerp(c, (205, 255, 240), .55 * (1 - t * .6))
            if eye:
                ed = math.hypot(x - eye[0], y - eye[1])
                if ed < eye[2]: c = lerp((255, 235, 170), (255, 150, 40), ed / eye[2])
                elif ed < eye[2] + 1.6: c = (18, 14, 34)
            rim = False
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if nx >= W: continue                     # image edge on the root side = inside
                if nx < 0 or ny < 0 or ny >= W or mp[nx, ny] == 0: rim = True
            if rim: c = (16, 13, 32)
            c = tuple(v + random.randint(-6, 6) for v in c)
            img.putpixel((x, y), clampc(c) + (255,))
    return img
FORE = [(31, 8), (24, 4), (14, 5), (5, 9), (0, 17), (2, 24), (9, 28), (18, 30), (31, 31)]
HIND = [(31, 5), (24, 2), (14, 3), (6, 8), (2, 15), (5, 22), (13, 26), (24, 27), (31, 26)]
m.paste(make_wing(FORE, (75, 55, 130)), (0, 0))
m.paste(make_wing(HIND, (95, 50, 120), eye=(12, 14, 3.2)), (32, 0))
# body fur (0,32,16,48), glow (16,32,32,48), dark (0,48,16,64)
for x in range(16):
    for y in range(16):
        fl = random.random() < .12
        base = (74, 66, 100) if fl else (44, 38, 62)
        m.putpixel((x, y + 32), clampc(tuple(v + random.randint(-8, 8) for v in base)) + (255,))
        d = ((x - 7.5) ** 2 + (y - 7.5) ** 2) ** .5 / 9
        m.putpixel((x + 16, y + 32), lerp((255, 255, 220), (255, 190, 60), min(1, d)) + (255,))
        m.putpixel((x, y + 48), clampc(tuple(v + random.randint(-4, 4) for v in (30, 26, 44))) + (255,))
os.makedirs(R + '/pack/assets/hull/textures/item', exist_ok=True)
m.save(R + '/pack/assets/hull/textures/item/moth.png')
REG = {"body": uvr(0, 32, 16, 48), "glow": uvr(16, 32, 32, 48), "ant": uvr(0, 48, 16, 64), "edge": uvr(0, 33, 3, 36),
       "fore": uvr(0, 0, 32, 32), "hind": uvr(32, 0, 64, 32)}
def mb(a, b, region, rot=None):
    e = {"from": a, "to": b, "faces": {f: {"uv": REG[region], "texture": "#0"} for f in ("north", "south", "east", "west", "up", "down")}}
    if rot: e["rotation"] = rot
    return e
def wb(a, b, quad, rot, flip):
    uv = list(REG[quad])
    if flip: uv = [uv[2], uv[1], uv[0], uv[3]]       # mirror u for the right-hand wing (outer edge stays at u=0 side)
    faces = {f: {"uv": REG["edge"], "texture": "#0"} for f in ("north", "south", "east", "west")}
    faces["up"] = {"uv": uv, "texture": "#0"}
    faces["down"] = {"uv": uv, "texture": "#0"}
    return {"from": a, "to": b, "rotation": rot, "faces": faces}
# Body unchanged in shape (head toward +z / south). Wings now start INSIDE the body (x 6..10) and tilt about their root.
me = [mb([6, 5, 4], [10, 9, 12], "body"), mb([6.5, 5.5, 1], [9.5, 8.5, 4], "glow"),
      mb([6.3, 6.2, 12], [9.7, 9.2, 14.6], "body"), mb([6.4, 7.2, 14.6], [7.4, 8.4, 14.9], "glow"), mb([8.6, 7.2, 14.6], [9.6, 8.4, 14.9], "glow"),
      mb([6.8, 9.2, 13.4], [7.2, 13, 13.8], "ant", {"angle": 22.5, "axis": "x", "origin": [7, 9.2, 13.6]}),
      mb([8.8, 9.2, 13.4], [9.2, 13, 13.8], "ant", {"angle": 22.5, "axis": "x", "origin": [9, 9.2, 13.6]}),
      # forewings (front) and hindwings (back, slightly lower); root 1.5 units inside the body
      wb([-6.5, 8, 5.5], [7.5, 8.5, 12.5], "fore", {"angle": -22.5, "axis": "z", "origin": [7.5, 8, 9]}, False),
      wb([8.5, 8, 5.5], [22.5, 8.5, 12.5], "fore", {"angle": 22.5, "axis": "z", "origin": [8.5, 8, 9]}, True),
      wb([-3.5, 7.2, 1], [7.5, 7.7, 7.5], "hind", {"angle": -22.5, "axis": "z", "origin": [7.5, 7.2, 4]}, False),
      wb([8.5, 7.2, 1], [19.5, 7.7, 7.5], "hind", {"angle": 22.5, "axis": "z", "origin": [8.5, 7.2, 4]}, True)]
w('pack/assets/hull/models/item/moth.json', {"textures": {"0": "hull:item/moth", "particle": "hull:item/moth"}, "elements": me})
w('pack/assets/hull/items/moth.json', {"model": {"type": "minecraft:model", "model": "hull:item/moth"}})

# zip (pack.mcmeta at the zip root)
zp = os.path.join(R, 'hull-pack.zip')
if os.path.exists(zp): os.remove(zp)
with zipfile.ZipFile(zp, 'w', zipfile.ZIP_DEFLATED) as z:
    base = os.path.join(R, 'pack')
    for d, _, fs in sorted(os.walk(base)):
        for f in sorted(fs):
            full = os.path.join(d, f); z.write(full, os.path.relpath(full, base))
            os.utime(zp)
print(hashlib.sha1(open(zp, 'rb').read()).hexdigest(), os.path.getsize(zp))
