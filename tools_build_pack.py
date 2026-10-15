import json, os, random, zipfile, hashlib, sys
from PIL import Image
R = sys.argv[1]  # repo dir
random.seed(7)
def w(path, data):
    p = os.path.join(R, path); os.makedirs(os.path.dirname(p), exist_ok=True)
    if isinstance(data, (dict, list)): data = json.dumps(data, indent=1)
    open(p, 'w').write(data)
w('pack/pack.mcmeta', {"pack": {"description": "The Hull test pack v0.1", "min_format": 75, "max_format": 75}})

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

# ---- moth texture 32x32: wing (0,0,16,16) body (16,0,32,8) glow (16,8,24,16) antenna (24,8,32,16)
m = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
for x in range(16):
    for y in range(16):
        cx = abs(x - 7.5) / 8; cy = abs(y - 7.5) / 8
        edge = max(cx, cy)
        base = lerp((70, 60, 120), (20, 150, 160), y / 15)
        vein = ((x * 3 + y * 2) % 11 == 0) or ((x * 2 - y * 3) % 13 == 0)
        c = lerp(base, (190, 255, 240), 0.75) if vein else base
        if edge > 0.85: c = lerp(c, (15, 12, 30), (edge - .85) / .15)
        m.putpixel((x, y), tuple(max(0, min(255, v + random.randint(-8, 8))) for v in c) + (255,))
for x in range(16, 32):
    for y in range(8):
        m.putpixel((x, y), tuple(max(0, min(255, v + random.randint(-10, 10))) for v in (44, 38, 62)) + (255,))
for x in range(16, 24):
    for y in range(8, 16):
        d = ((x - 19.5) ** 2 + (y - 11.5) ** 2) ** .5 / 5
        m.putpixel((x, y), lerp((255, 255, 220), (255, 190, 60), min(1, d)) + (255,))
for x in range(24, 32):
    for y in range(8, 16): m.putpixel((x, y), (30, 26, 44, 255))
os.makedirs(R + '/pack/assets/hull/textures/item', exist_ok=True)
m.save(R + '/pack/assets/hull/textures/item/moth.png')
REG = {"wing": [0, 0, 16, 16], "body": [17, 1, 21, 5], "glow": [18, 10, 22, 14], "ant": [25, 9, 28, 12], "wingedge": [0, 0, 2, 2]}
def mb(a, b, region, rot=None, wing=False):
    faces = {}
    for f in ("north", "south", "east", "west", "up", "down"):
        r = REG["wing"] if (wing and f in ("up", "down")) else (REG["wingedge"] if wing else REG[region])
        faces[f] = {"uv": r, "texture": "#0"}
    e = {"from": a, "to": b, "faces": faces}
    if rot: e["rotation"] = rot
    return e
# head toward +z (south) so it faces travel direction when the display shares the creature's yaw
me = [mb([6, 5, 4], [10, 9, 12], "body"), mb([6.5, 5.5, 1], [9.5, 8.5, 4], "glow"),
      mb([6.3, 6.2, 12], [9.7, 9.2, 14.6], "body"), mb([6.4, 7.2, 14.6], [7.4, 8.4, 14.9], "glow"), mb([8.6, 7.2, 14.6], [9.6, 8.4, 14.9], "glow"),
      mb([6.8, 9.2, 13.4], [7.2, 13, 13.8], "ant", {"angle": 22.5, "axis": "x", "origin": [7, 9.2, 13.6]}),
      mb([8.8, 9.2, 13.4], [9.2, 13, 13.8], "ant", {"angle": 22.5, "axis": "x", "origin": [9, 9.2, 13.6]}),
      mb([-6, 8, 4], [6, 8.4, 12], "wing", {"angle": 22.5, "axis": "z", "origin": [6, 8, 8]}, True),
      mb([10, 8, 4], [22, 8.4, 12], "wing", {"angle": -22.5, "axis": "z", "origin": [10, 8, 8]}, True)]
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
