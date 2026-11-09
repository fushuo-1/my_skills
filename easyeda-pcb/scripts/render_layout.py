#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EasyEDA Pro 备份工程 (.epro2) → PCB layout SVG

用法:
    python render_layout.py <工程目录或 .epro2 路径> [-o 输出目录] [--diff 另一份.epro2]
                            [--scale 10.4] [--check]

给目录时自动挑目录里最新的 .epro2。
输出 <工程名>_顶层.svg / _底层.svg / _叠加.svg，并在 stdout 打印统计。
"""
import argparse
import glob
import json
import math
import os
import sys
import zipfile
from collections import defaultdict

MIL = 0.0254  # 文件里坐标单位是 mil


# ---------------------------------------------------------------- 解析

def pick_source(path):
    if os.path.isdir(path):
        cands = sorted(glob.glob(os.path.join(path, '*.epro2')))
        if not cands:
            sys.exit('目录里没有 .epro2：%s' % path)
        return cands[-1]
    return path


def read_epru(path):
    try:
        z = zipfile.ZipFile(path)
    except zipfile.BadZipFile:
        sys.exit('%s 不是 zip。这大概是主工程 .eprj2（SQLite + 加密数据，读不出来），'
                 '改用 PCB/<项目>_backup/ 里的 .epro2' % path)
    inner = [n for n in z.namelist() if n.lower().endswith('.epru')]
    if not inner:
        sys.exit('%s 里没有 .epru（这可能是主工程 .eprj2，其数据是加密的，读不了）' % path)
    return z.read(inner[0]).decode('utf-8', errors='replace')


def split_sections(raw):
    """对象以 | 分隔。文档元数据紧跟在 DOCHEAD 之后那一行 —— 不是之前。"""
    objs = []
    for line in raw.split('|\n'):
        line = line.strip()
        if not line:
            continue
        for piece in line.split('||'):
            piece = piece.strip()
            if piece:
                objs.append(json.loads(piece))
    secs = []
    for i, o in enumerate(objs):
        if o.get('type') == 'DOCHEAD':
            meta = objs[i + 1] if i + 1 < len(objs) else {}
            secs.append({'meta': meta, 'items': []})
        elif secs:
            secs[-1]['items'].append(o)
    return secs


def build_items(items):
    """有 type 的是实体头，紧跟其后没有 type 的是属性补丁，要顺序合并。"""
    ents, cur = [], None
    for o in items:
        if o.get('type'):
            cur = dict(o)
            ents.append(cur)
        elif cur is not None:
            cur.update(o)
    return ents


def load_board(path):
    secs = split_sections(read_epru(path))
    for s in secs:
        ents = build_items(s['items'])
        if any(x['type'] == 'PAD_NET' for x in ents):
            return secs, ents
    sys.exit('%s 里找不到 PCB 板文档（没有 PAD_NET 的 section）' % path)


def rotate(comp, px, py):
    cx, cy, ang = comp['x'], comp['y'], comp['angle'] % 360
    if ang == 90:
        return cx + py, cy - px
    if ang == 180:
        return cx - px, cy - py
    if ang == 270:
        return cx - py, cy + px
    return cx + px, cy + py


class Board:
    def __init__(self, path):
        self.path = path
        secs, ents = load_board(path)
        self.name = os.path.splitext(os.path.basename(path))[0]

        self.desig = {}
        self.fp_ref = {}
        for a in ents:
            if a['type'] == 'ATTR':
                if a.get('key') == 'Designator':
                    self.desig[a['parentId']] = a['value']
                if a.get('key') == 'Footprint':
                    self.fp_ref[a['parentId']] = a['value']

        # 封装文档：meta.uuid 与元件 Footprint 属性直接对表
        self.fp_secs = {}
        for s in secs:
            u = s['meta'].get('uuid')
            pads = [x for x in build_items(s['items']) if x['type'] == 'PAD']
            if u and pads:
                self.fp_secs[u] = pads

        self.comps = [x for x in ents if x['type'] == 'COMPONENT']
        self.lines = [x for x in ents if x['type'] == 'LINE']
        self.vias = [x for x in ents if x['type'] == 'VIA']
        self.pours = [x for x in ents if x['type'] == 'POUR']
        self.pad_nets = [x for x in ents if x['type'] == 'PAD_NET']
        outlines = [x for x in ents if x['type'] == 'POLY'
                    and x.get('polyType') == 'BOARD_OUTLINE']
        if not outlines:
            sys.exit('找不到板框（polyType=BOARD_OUTLINE 的 POLY）')
        self.outline = outlines[0]

        self.designator_texts = [
            (self.desig.get(a['parentId'], '?'), a['x'] * MIL, a['y'] * MIL)
            for a in ents
            if a['type'] == 'ATTR' and a.get('key') == 'Designator'
            and a.get('x') and a.get('y')
        ]

        self._build_pads()
        self._build_boxes()

    def _build_pads(self):
        self.pads = []
        for c in self.comps:
            for p in self.fp_secs.get(self.fp_ref.get(c['id']), []):
                ax, ay = rotate(c, p['centerX'], p['centerY'])
                hole = p.get('hole') or {}
                dp = p.get('defaultPad') or {}
                self.pads.append({
                    'x': ax * MIL, 'y': ay * MIL,
                    'layer': p.get('layerId'),
                    'type': dp.get('padType', 'RECT'),
                    'w': (dp.get('width') or 0) * MIL,
                    'h': (dp.get('height') or 0) * MIL,
                    'hole': (hole.get('width') or 0) * MIL,
                })

    def _build_boxes(self):
        self.boxes = []
        for c in self.comps:
            pads = self.fp_secs.get(self.fp_ref.get(c['id']), [])
            if not pads:
                continue
            xs, ys = [], []
            for p in pads:
                ax, ay = rotate(c, p['centerX'], p['centerY'])
                dp = p.get('defaultPad') or {}
                rw = (dp.get('width') or 0) / 2
                rh = (dp.get('height') or 0) / 2
                xs += [ax - rw, ax + rw]
                ys += [ay - rh, ay + rh]
            self.boxes.append({'x0': min(xs) * MIL, 'x1': max(xs) * MIL,
                               'y0': min(ys) * MIL, 'y1': max(ys) * MIL})

    # ---- 查询 ----

    def nets_on(self, layer):
        return set(x['netName'] for x in self.lines if x['layerId'] == layer)

    def length(self, layer, nets=None):
        return sum(math.hypot(x['endX'] - x['startX'], x['endY'] - x['startY']) * MIL
                   for x in self.lines
                   if x['layerId'] == layer and (nets is None or x['netName'] in nets))

    def count(self, layer):
        return sum(1 for x in self.lines if x['layerId'] == layer)

    def net_stats(self, layer, net):
        """(段数, 总长, 端点列表)"""
        segs = [x for x in self.lines if x['layerId'] == layer and x['netName'] == net]
        return len(segs), self.length(layer, {net}), segs

    def net_index(self):
        """网络 -> [(位号, 脚号)]，用于查某个脚的对端"""
        if getattr(self, '_net_index', None) is not None:
            return self._net_index
        comp_by_id = {c['id']: c for c in self.comps}
        idx = defaultdict(list)
        for pn in self.pad_nets:
            parts = pn['id'].split('","')
            cid = parts[1].strip('["')
            num = parts[2].strip()
            net = pn.get('padNet')
            if not net or cid not in comp_by_id:
                continue
            idx[net].append((self.desig.get(cid, '?'), num))
        self._net_index = idx
        return idx

    def pins_of(self, designator):
        """元件每个脚：(脚号, x_mm, y_mm, 网络, 对端列表)"""
        cid = next((k for k, v in self.desig.items() if v == designator), None)
        if cid is None:
            return None
        comp = next(c for c in self.comps if c['id'] == cid)
        pads = self.fp_secs.get(self.fp_ref.get(cid), [])
        netmap = {}
        for pn in self.pad_nets:
            parts = pn['id'].split('","')
            if parts[1].strip('["') == cid:
                netmap[parts[2].strip()] = pn.get('padNet')
        idx = self.net_index()
        rows = []
        for p in pads:
            ax, ay = rotate(comp, p['centerX'], p['centerY'])
            num = p.get('num') or ''
            net = netmap.get(num)
            peers = []
            if net:
                peers = ['%s.%s' % (d, n) for d, n in idx.get(net, [])
                         if not (d == designator and n == num)]
            rows.append((num, ax * MIL, ay * MIL, net or '-', peers))
        def key(r):
            try:
                return (0, int(r[0]))
            except ValueError:
                return (1, r[0])
        return sorted(rows, key=key)

    def unconnected_nets(self):
        """有焊盘、但板上没有任何走线/过孔/铺铜的网络 —— 通常是漏连"""
        connected = set()
        for x in self.lines:
            connected.add(x['netName'])
        for x in self.vias:
            connected.add(x.get('netName'))
        for x in self.pours:
            connected.add(x.get('netName'))
        counts = defaultdict(int)
        for pn in self.pad_nets:
            net = pn.get('padNet')
            if net:
                counts[net] += 1
        return sorted(((n, c) for n, c in counts.items() if n not in connected),
                      key=lambda kv: -kv[1])

    def min_clearance(self, layer):
        """同层不同网络之间的最小铜边间距 (mm)"""
        segs = [(x['netName'], (x['startX'], x['startY']), (x['endX'], x['endY']), x['width'])
                for x in self.lines if x['layerId'] == layer]
        best = (1e9, None, None)
        for i in range(len(segs)):
            n1, a1, b1, w1 = segs[i]
            for j in range(i + 1, len(segs)):
                n2, a2, b2, w2 = segs[j]
                if n1 == n2:
                    continue
                d = _seg_dist(a1, b1, a2, b2) * MIL - (w1 + w2) / 2 * MIL
                if d < best[0]:
                    best = (d, n1, n2)
        return best


def _seg_dist(p1, p2, p3, p4):
    def d(a, b):
        return math.hypot(a[0] - b[0], a[1] - b[1])

    def pt_seg(p, a, b):
        ax, ay = a
        bx, by = b
        dx, dy = bx - ax, by - ay
        L = dx * dx + dy * dy
        if L == 0:
            return d(p, a)
        t = max(0, min(1, ((p[0] - ax) * dx + (p[1] - ay) * dy) / L))
        return d(p, (ax + t * dx, ay + t * dy))

    def inter(a, b, c, e):
        d1 = (b[0] - a[0], b[1] - a[1])
        d2 = (e[0] - c[0], e[1] - c[1])
        den = d1[0] * d2[1] - d1[1] * d2[0]
        if abs(den) < 1e-12:
            return False
        t = ((c[0] - a[0]) * d2[1] - (c[1] - a[1]) * d2[0]) / den
        u = ((c[0] - a[0]) * d1[1] - (c[1] - a[1]) * d1[0]) / den
        return 0 <= t <= 1 and 0 <= u <= 1

    if inter(p1, p2, p3, p4):
        return 0.0
    return min(pt_seg(p1, p3, p4), pt_seg(p2, p3, p4),
               pt_seg(p3, p1, p2), pt_seg(p4, p1, p2))


# ---------------------------------------------------------------- 渲染

def render(board, out_dir, base, scale=10.4, diff_board=None):
    o = board.outline['path']
    bx0, by1 = o[1] * MIL, o[2] * MIL
    bw, bh = o[3] * MIL, o[4] * MIL
    bx1, by0 = bx0 + bw, by1 - bh
    rad = o[6] * MIL

    new_nets = set()
    if diff_board:
        new_nets = board.nets_on(2) - diff_board.nets_on(2)

    pad = 64
    W = int(bw * scale) + pad * 2
    H = int(bh * scale) + 180

    def tf(x, y):
        return pad + (x - bx0) * scale, 126 + (by1 - y) * scale

    style = '''<style>
  .t1{font-family:'Microsoft YaHei','PingFang SC',sans-serif;font-size:25px;font-weight:bold;fill:#111}
  .t3{font-family:'Microsoft YaHei','PingFang SC',sans-serif;font-size:13px;fill:#555}
  .t4{font-family:'Microsoft YaHei','PingFang SC',sans-serif;font-size:11px;fill:#888}
  .sig{font-family:'Microsoft YaHei','PingFang SC',sans-serif;font-size:9.5px;fill:#666;paint-order:stroke;stroke:#fff;stroke-width:2.6px;stroke-linejoin:round}
  .pad{fill:#c9a227;stroke:#8a6d10;stroke-width:0.8}
  .hole{fill:#fff;stroke:#8a6d10;stroke-width:0.8}
  .via{fill:#e8e8e8;stroke:#666;stroke-width:1}
  .viah{fill:#fff;stroke:#666;stroke-width:1}
  .edge{stroke:#333;stroke-width:1.6;fill:none}
  .box{fill:#f2f2f2;fill-opacity:0.5;stroke:#cfcfcf;stroke-width:0.8}
</style>'''

    def one(layers, fname, title, subtitle, hi=None):
        hi = hi or set()
        out = []
        A = out.append
        A('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d">'
          % (W, H, W, H))
        A(style)
        A('<rect width="%d" height="%d" fill="#fff"/>' % (W, H))
        A('<text x="%d" y="44" class="t1">%s</text>' % (pad, title))
        A('<text x="%d" y="70" class="t3">%s</text>' % (pad, subtitle))
        A('<text x="%d" y="92" class="t4">数据来源：%s · 金色 = 焊盘 · 灰环 = 过孔 · 虚线框 = 元件本体 · %.1f px/mm</text>'
          % (pad, os.path.basename(board.path), scale))

        x0, y0 = tf(bx0, by1)
        x1, y1 = tf(bx1, by0)
        A('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="%.1f" class="edge"/>'
          % (x0, y0, x1 - x0, y1 - y0, rad * scale))

        for b in board.boxes:
            xa, ya = tf(b['x0'], b['y1'])
            xb, yb = tf(b['x1'], b['y0'])
            A('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" class="box"/>'
              % (xa, ya, max(xb - xa, 2), max(yb - ya, 2)))

        for p in board.pours:
            if p.get('layerId') not in layers:
                continue
            col = '#c0392b' if p['layerId'] == 1 else '#1a4fd6'
            flat = (p.get('path') or [[]])[0]
            nums = [v for v in flat if isinstance(v, (int, float))]
            xs, ys = nums[0::2], nums[1::2]
            if len(xs) < 2:
                continue
            xa, ya = tf(min(xs) * MIL, max(ys) * MIL)
            xb, yb = tf(max(xs) * MIL, min(ys) * MIL)
            A('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" fill-opacity="0.08" '
              'stroke="%s" stroke-dasharray="7 5" stroke-width="1.2" stroke-opacity="0.75"/>'
              % (xa, ya, max(xb - xa, 3), max(yb - ya, 3), col, col))
            A('<text x="%.1f" y="%.1f" class="t4" text-anchor="middle">%s 铺铜</text>'
              % ((xa + xb) / 2, yb - 4, p.get('netName') or ''))

        for ln in board.lines:
            if ln['layerId'] not in layers:
                continue
            col = '#c0392b' if ln['layerId'] == 1 else '#1a4fd6'
            if ln['netName'] in hi and ln['layerId'] == 2:
                col = '#0a9b3d'
            w = max(ln['width'] * MIL * scale, 1.5)
            xa, ya = tf(ln['startX'] * MIL, ln['startY'] * MIL)
            xb, yb = tf(ln['endX'] * MIL, ln['endY'] * MIL)
            A('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="%.1f" '
              'stroke-linecap="round" stroke-opacity="%s"/>'
              % (xa, ya, xb, yb, col, w, '0.85' if len(layers) > 1 else '1'))

        for v in board.vias:
            cx, cy = tf(v['centerX'] * MIL, v['centerY'] * MIL)
            A('<circle cx="%.1f" cy="%.1f" r="%.1f" class="via"/>'
              % (cx, cy, max(v['viaDiameter'] * MIL * scale / 2, 2.7)))
            A('<circle cx="%.1f" cy="%.1f" r="%.1f" class="viah"/>'
              % (cx, cy, max(v['holeDiameter'] * MIL * scale / 2, 1.3)))

        for p in board.pads:
            if p['hole'] <= 0:
                if p['layer'] in (1, 2) and p['layer'] not in layers:
                    continue
                if p['layer'] not in (1, 2):
                    continue
            cx, cy = tf(p['x'], p['y'])
            rw, rh = max(p['w'] * scale / 2, 1.3), max(p['h'] * scale / 2, 1.3)
            if p['type'] == 'ELLIPSE':
                A('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" class="pad"/>' % (cx, cy, rw, rh))
            else:
                A('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" class="pad"/>'
                  % (cx - rw, cy - rh, rw * 2, rh * 2))
            if p['hole'] > 0:
                A('<circle cx="%.1f" cy="%.1f" r="%.1f" class="hole"/>'
                  % (cx, cy, max(p['hole'] * scale / 2, 1.0)))

        for name, tx, ty in board.designator_texts:
            cx, cy = tf(tx, ty)
            A('<text x="%.1f" y="%.1f" class="sig" text-anchor="middle">%s</text>' % (cx, cy, name))

        sx, sy = pad, H - 44
        A('<line x1="%d" y1="%d" x2="%.1f" y2="%d" stroke="#333" stroke-width="2"/>'
          % (sx, sy, sx + 10 * scale, sy))
        A('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="#333" stroke-width="2"/>'
          % (sx, sy - 6, sx, sy + 6))
        A('<line x1="%.1f" y1="%d" x2="%.1f" y2="%d" stroke="#333" stroke-width="2"/>'
          % (sx + 10 * scale, sy - 6, sx + 10 * scale, sy + 6))
        A('<text x="%.1f" y="%d" class="t4" text-anchor="middle">10 mm</text>'
          % (sx + 5 * scale, sy - 12))
        A('<text x="%.1f" y="%d" class="t4">板尺寸 %.1f × %.1f mm · 圆角 R%.0f · %d 个元件 · '
          '%d 个焊盘 · %d 个过孔</text>'
          % (sx + 11 * scale, sy + 4, bw, bh, rad, len(board.comps), len(board.pads), len(board.vias)))
        A('</svg>')
        path = os.path.join(out_dir, fname)
        with open(path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(out))
        return path, W, H

    n1, n2 = board.count(1), board.count(2)
    l1, l2 = board.length(1), board.length(2)
    paths = [
        one((1,), '%s_顶层.svg' % base,
            'PCB Layout 顶层（Top Layer）',
            '红色 = 顶层走线 %d 段 / 合计 %.0f mm' % (n1, l1)),
        one((2,), '%s_底层.svg' % base,
            'PCB Layout 底层（Bottom Layer）',
            '蓝色 = 底层走线 %d 段 / 合计 %.0f mm%s'
            % (n2, l2, (' · 绿色 = 相比对照文件新增的 %d 条' % len(new_nets)) if new_nets else ''),
            hi=new_nets),
        one((1, 2), '%s_叠加.svg' % base,
            'PCB Layout 叠加（Top + Bottom）',
            '红 = 顶层 %.0f mm（%d 段）· 蓝 = 底层 %.0f mm（%d 段）' % (l1, n1, l2, n2)),
    ]
    return paths


# ---------------------------------------------------------------- 主流程

def main():
    ap = argparse.ArgumentParser(description='EasyEDA Pro 备份工程 → PCB layout SVG')
    ap.add_argument('src', help='.epro2 文件，或包含 .epro2 的目录（自动取最新）')
    ap.add_argument('-o', '--out', default=None, help='输出目录，默认当前目录')
    ap.add_argument('--diff', default=None, help='对照的另一份 .epro2，标出新增到底层的网络')
    ap.add_argument('--scale', type=float, default=10.4, help='px/mm，默认 10.4')
    ap.add_argument('--check', action='store_true', help='额外输出间距检查和各层网络统计')
    ap.add_argument('--pins', metavar='位号', help='只打印这个元件每个脚的网络和对端，不画图')
    ap.add_argument('--net', metavar='网络名', help='打印这个网络在板上每个焊盘的位置，不画图')
    args = ap.parse_args()

    src = pick_source(args.src)
    out_dir = args.out or os.getcwd()
    os.makedirs(out_dir, exist_ok=True)

    board = Board(src)

    if args.pins:
        rows = board.pins_of(args.pins)
        if rows is None:
            sys.exit('板上没有位号 %s' % args.pins)
        idx = board.net_index()
        print('%s 共 %d 个脚：' % (args.pins, len(rows)))
        for num, x, y, net, peers in rows:
            others = ', '.join(peers) if peers else '(只有这个脚)'
            print('  脚 %-4s (%6.2f,%6.2f)  %-10s %s' % (num, x, y, net, others))
        return

    if args.net:
        idx = board.net_index()
        hits = idx.get(args.net)
        if not hits:
            sys.exit('板上没有网络 %s' % args.net)
        print('网络 %s 连了 %d 个焊盘：' % (args.net, len(hits)))
        for d, n in hits:
            print('  %s.%s' % (d, n))
        return

    diff = Board(pick_source(args.diff)) if args.diff else None
    base = os.path.splitext(os.path.basename(src))[0]

    for path, w, h in render(board, out_dir, base, args.scale, diff):
        print('写出 %s  (%dx%d，转 PNG 时用这个 window-size)' % (path, w, h))

    print()
    print('板尺寸 %.1f × %.1f mm · %d 个元件 · %d 个焊盘 · %d 个过孔'
          % (board.outline['path'][3] * MIL, board.outline['path'][4] * MIL,
             len(board.comps), len(board.pads), len(board.vias)))
    print('顶层 %d 段 / %.0f mm · 底层 %d 段 / %.0f mm'
          % (board.count(1), board.length(1), board.count(2), board.length(2)))

    if args.check:
        for layer, nm in ((1, '顶层'), (2, '底层')):
            gap, a, b = board.min_clearance(layer)
            if a:
                print('%s最小铜边间距 %.3f mm（%s ↔ %s）' % (nm, gap, a, b))

        orphan = board.unconnected_nets()
        print()
        if orphan:
            print('没有连接的网（有焊盘，但板上零走线/零过孔/零铺铜）：')
            for net, n in orphan:
                print('  %-10s %d 个焊盘' % (net, n))
        else:
            print('所有有焊盘的网络都布了线或铺了铜。')
        print()
        print('各网络走线长度（mm，顶层/底层）：')
        nets = defaultdict(lambda: [0.0, 0.0])
        for x in board.lines:
            ln = math.hypot(x['endX'] - x['startX'], x['endY'] - x['startY']) * MIL
            nets[x['netName']][0 if x['layerId'] == 1 else 1] += ln
        for net in sorted(nets, key=lambda k: -(nets[k][0] + nets[k][1])):
            t, b = nets[net]
            print('  %-10s %7.1f  %7.1f' % (net, t, b))

        print()
        print('绕路检查（每条网络两端点的曼哈顿距离 vs 实际走线长度，只看两头都有的层）：')
        for layer, nm in ((1, '顶层'), (2, '底层')):
            rows = []
            for net in board.nets_on(layer):
                segs = [x for x in board.lines if x['layerId'] == layer and x['netName'] == net]
                if not segs:
                    continue
                deg = defaultdict(int)
                for x in segs:
                    deg[(round(x['startX'], 2), round(x['startY'], 2))] += 1
                    deg[(round(x['endX'], 2), round(x['endY'], 2))] += 1
                ends = [k for k, v in deg.items() if v == 1]
                if len(ends) != 2:
                    continue
                a, b = ends
                man = (abs(a[0] - b[0]) + abs(a[1] - b[1])) * MIL
                real = board.length(layer, {net})
                if man > 1:
                    rows.append((real - man, net, real, man))
            if not rows:
                continue
            rows.sort(reverse=True)
            print('  [%s] 超得最多的 5 条：' % nm)
            for extra, net, real, man in rows[:5]:
                print('    %-8s 实际 %6.1f  最短 %6.1f  多绕 %+5.1f mm' % (net, real, man, extra))


if __name__ == '__main__':
    main()
