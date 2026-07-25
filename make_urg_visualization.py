"""Render a Unified Reflective Graph diagram from a real graph.

Builds the worked example that the architecture papers describe -- two
observations deriving one piece of evidence through a *multi-parent* provenance
edge, a contested hypothesis carrying both supporting and contradicting evidence,
an inquiry that targets the contest, and an explanation that traces back to the
evidence -- then draws it.

The layout is computed from the graph's own structure (nodes are placed in layers
by type), so the picture cannot drift from the data the way a hand-drawn one can.

Writes `urg_visualization.png`. Requires Pillow; no other dependency.
"""
from PIL import Image, ImageDraw, ImageFont

from shadow_mirror import UnifiedReflectiveGraph

# ---------------------------------------------------------------- palette
BG = (255, 255, 255)
INK = (20, 22, 27)
MUTED = (110, 118, 132)

TYPE_STYLE = {
    "Observation": ((234, 242, 252), (52, 106, 176)),
    "Evidence":    ((231, 245, 236), (43, 130, 79)),
    "Context":     ((248, 243, 231), (163, 122, 30)),
    "Hypothesis":  ((243, 237, 250), (117, 79, 168)),
    "Inquiry":     ((252, 240, 233), (188, 96, 46)),
    "Explanation": ((236, 240, 245), (70, 82, 102)),
}
EDGE_STYLE = {
    "provenance":    ((43, 130, 79), 0),      # solid
    "supports":      ((52, 106, 176), 0),
    "contradicts":   ((198, 55, 62), 1),      # dashed
    "targets":       ((188, 96, 46), 1),
    "explains":      ((70, 82, 102), 0),
    "contextualises": ((163, 122, 30), 1),
}

# layer per node type, left to right
LAYER = {"Observation": 0, "Context": 0, "Evidence": 1,
         "Hypothesis": 2, "Inquiry": 3, "Explanation": 3}


def build_graph():
    g = UnifiedReflectiveGraph()
    o1 = g.add_node("Observation", {"label": "self-report\n'I don't want this'", "value": 0.15})
    o2 = g.add_node("Observation", {"label": "behaviour log\napproached 4x", "value": 0.80})
    o3 = g.add_node("Observation", {"label": "arousal\nelevated", "value": 0.75})
    ctx = g.add_node("Context", {"label": "context\nhigh-pressure period"})

    # the multi-parent derivation: one evidence node, two provenance parents
    e1 = g.add_node("Evidence", {"label": "stated/behaviour\nmismatch"})
    g.add_edge(o1, e1, "provenance")
    g.add_edge(o2, e1, "provenance")

    e2 = g.add_node("Evidence", {"label": "arousal without\navoidance measure"})
    g.add_edge(o3, e2, "provenance")

    h1 = g.add_node("Hypothesis", {"label": "latent_approach\n'hidden want'"})
    h2 = g.add_node("Hypothesis", {"label": "threat_compliance\n'complies under threat'"})

    # contradiction retained as an edge rather than resolved
    g.add_edge(e1, h1, "supports")
    g.add_edge(e1, h2, "supports")
    g.add_edge(e2, h1, "contradicts")
    g.add_edge(e2, h2, "supports")
    g.add_edge(ctx, h2, "contextualises")

    q = g.add_node("Inquiry", {"label": "inquiry\n'avoidance channel?'\nEIG 0.61 bits"})
    g.add_edge(q, h1, "targets")
    g.add_edge(q, h2, "targets")

    x = g.add_node("Explanation", {"label": "explanation\nunresolved_approach\n+ uncertainty"})
    g.add_edge(x, e1, "explains")
    g.add_edge(x, e2, "explains")
    return g


def font(size, bold=False):
    for name in (("calibrib.ttf", "calibri.ttf") if bold else ("calibri.ttf",)):
        try:
            return ImageFont.truetype(r"C:\Windows\Fonts\%s" % name, size)
        except Exception:
            pass
    return ImageFont.load_default()


def dashed(d, p0, p1, colour, width=2, dash=7, gap=5):
    (x0, y0), (x1, y1) = p0, p1
    dx, dy = x1 - x0, y1 - y0
    dist = max(1.0, (dx * dx + dy * dy) ** 0.5)
    ux, uy = dx / dist, dy / dist
    t = 0.0
    while t < dist:
        a = (x0 + ux * t, y0 + uy * t)
        b = (x0 + ux * min(t + dash, dist), y0 + uy * min(t + dash, dist))
        d.line([a, b], fill=colour, width=width)
        t += dash + gap


def arrow_head(d, p0, p1, colour, size=9):
    import math
    (x0, y0), (x1, y1) = p0, p1
    ang = math.atan2(y1 - y0, x1 - x0)
    for s in (2.6, -2.6):
        d.line([(x1, y1),
                (x1 - size * math.cos(ang + s / 3.0),
                 y1 - size * math.sin(ang + s / 3.0))], fill=colour, width=2)


def main():
    g = build_graph()
    data = g.to_dict()
    nodes = data["nodes"] if isinstance(data.get("nodes"), list) else \
        [dict(id=k, **v) for k, v in data["nodes"].items()]

    # group by layer
    layers = {}
    for n in nodes:
        nt = n.get("node_type") or n.get("type")
        layers.setdefault(LAYER.get(nt, 3), []).append(n)

    SCALE = 2                                  # supersample, then downscale
    NW, NH = 196 * SCALE, 74 * SCALE
    HGAP, VGAP = 96 * SCALE, 30 * SCALE
    MX, MY = 46 * SCALE, 92 * SCALE

    LEGEND_H = 62 * SCALE
    ncols = max(layers) + 1
    nrows = max(len(v) for v in layers.values())
    W = MX * 2 + ncols * NW + (ncols - 1) * HGAP
    content_h = nrows * NH + (nrows - 1) * VGAP
    H = MY + content_h + LEGEND_H + 26 * SCALE

    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    f_title = font(23 * SCALE, True)
    f_sub = font(12 * SCALE)
    f_node = font(10 * SCALE, True)
    f_small = font(9 * SCALE)
    f_edge = font(8 * SCALE)

    d.text((MX, 30 * SCALE), "The Unified Reflective Graph", font=f_title, fill=INK)
    d.text((MX, 62 * SCALE),
           "Typed nodes, multi-parent provenance closure, and contradiction as a first-class edge. "
           "Generated from the graph, not drawn by hand.",
           font=f_sub, fill=MUTED)

    # place nodes
    pos = {}
    for col in sorted(layers):
        col_nodes = layers[col]
        total = len(col_nodes) * NH + (len(col_nodes) - 1) * VGAP
        y0 = MY + (content_h - total) / 2
        for i, n in enumerate(col_nodes):
            x = MX + col * (NW + HGAP)
            y = y0 + i * (NH + VGAP)
            pos[n["id"]] = (x, y)

    # edges first, so boxes sit on top
    for e in data["edges"]:
        s, t = e.get("source"), e.get("target")
        rel = e.get("relationship") or e.get("type")
        if s not in pos or t not in pos:
            continue
        colour, dash_it = EDGE_STYLE.get(rel, (MUTED, 0))
        (x0, y0), (x1, y1) = pos[s], pos[t]
        # anchor on the facing edge of each box
        if x1 > x0:
            p0, p1 = (x0 + NW, y0 + NH / 2), (x1, y1 + NH / 2)
        elif x1 < x0:
            p0, p1 = (x0, y0 + NH / 2), (x1 + NW, y1 + NH / 2)
        else:
            p0, p1 = (x0 + NW / 2, y0 + NH), (x1 + NW / 2, y1)
        if dash_it:
            dashed(d, p0, p1, colour, width=2 * SCALE)
        else:
            d.line([p0, p1], fill=colour, width=2 * SCALE)
        arrow_head(d, p0, p1, colour, size=9 * SCALE)
        mx, my = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2
        tw = d.textlength(rel, font=f_edge)
        d.rectangle([mx - tw / 2 - 3 * SCALE, my - 8 * SCALE,
                     mx + tw / 2 + 3 * SCALE, my + 7 * SCALE], fill=BG)
        d.text((mx - tw / 2, my - 7 * SCALE), rel, font=f_edge, fill=colour)

    # boxes
    for n in nodes:
        nt = n.get("node_type") or n.get("type")
        x, y = pos[n["id"]]
        fill, edge = TYPE_STYLE.get(nt, ((240, 240, 240), MUTED))
        d.rounded_rectangle([x, y, x + NW, y + NH], radius=7 * SCALE,
                            fill=fill, outline=edge, width=2 * SCALE)
        d.text((x + 11 * SCALE, y + 8 * SCALE), nt, font=f_node, fill=edge)
        label = (n.get("data") or {}).get("label", "")
        for j, line in enumerate(label.split("\n")[:3]):
            d.text((x + 11 * SCALE, y + 27 * SCALE + j * 14 * SCALE),
                   line, font=f_small, fill=INK)

    # legend
    ly = MY + content_h + 30 * SCALE
    lx = MX
    d.text((lx, ly - 20 * SCALE), "Edges", font=f_node, fill=INK)
    for rel, (colour, dash_it) in EDGE_STYLE.items():
        if dash_it:
            dashed(d, (lx, ly + 6 * SCALE), (lx + 26 * SCALE, ly + 6 * SCALE), colour, 2 * SCALE)
        else:
            d.line([(lx, ly + 6 * SCALE), (lx + 26 * SCALE, ly + 6 * SCALE)],
                   fill=colour, width=2 * SCALE)
        d.text((lx + 32 * SCALE, ly), rel, font=f_edge, fill=colour)
        lx += 32 * SCALE + d.textlength(rel, font=f_edge) + 26 * SCALE

    img = img.resize((W // SCALE, H // SCALE), Image.LANCZOS)
    img.save("urg_visualization.png", "PNG")

    print("wrote urg_visualization.png  (%d x %d)" % img.size)
    print("  nodes: %d   edges: %d" % (len(nodes), g.n_edges()))
    ev = [n for n in nodes if (n.get("node_type") or n.get("type")) == "Evidence"]
    for e in ev:
        print("  ancestors(%s) = %d" % ((e.get("data") or {}).get("label", "?").split("\n")[0],
                                        len(g.ancestors(e["id"]))))
    print("  contested hypotheses: %d" % len(g.contested_hypotheses()))


if __name__ == "__main__":
    main()
