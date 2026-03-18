import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx

# build the graph
G = nx.DiGraph()

nodes = [
    "__start__",
    "preprocessor",
    "extractor",
    "classifier",
    "router",
    "json_specialist",
    "receipt_specialist",
    "po_specialist",
    "bank_specialist",
    "resume_specialist",
    "validator",
    "__end__"
]

edges = [
    ("__start__",          "preprocessor"),
    ("preprocessor",       "extractor"),
    ("extractor",          "classifier"),
    ("classifier",         "router"),
    ("router",             "json_specialist"),
    ("router",             "receipt_specialist"),
    ("router",             "po_specialist"),
    ("router",             "bank_specialist"),
    ("router",             "resume_specialist"),
    ("json_specialist",    "validator"),
    ("receipt_specialist", "validator"),
    ("po_specialist",      "validator"),
    ("bank_specialist",    "validator"),
    ("resume_specialist",  "validator"),
    ("validator",          "__end__")
]

G.add_nodes_from(nodes)
G.add_edges_from(edges)

# layout — fan out from router
pos = {
    "__start__":          ( 0,    11),
    "preprocessor":       ( 0,    10),
    "extractor":          ( 0,     9),
    "classifier":         ( 0,     8),
    "router":             ( 0,     7),
    "json_specialist":    (-4,     5),
    "receipt_specialist": (-2,     5),
    "po_specialist":      ( 0,     5),
    "bank_specialist":    ( 2,     5),
    "resume_specialist":  ( 4,     5),
    "validator":          ( 0,     3),
    "__end__":            ( 0,     2),
}

# node colors
node_colors = {
    "__start__":          "#C8E6C9",  # light green
    "preprocessor":       "#B3D9FF",  # light blue
    "extractor":          "#B3D9FF",
    "classifier":         "#B3D9FF",
    "router":             "#FFB347",  # orange — routing logic
    "json_specialist":    "#FFD700",  # gold — fine-tuned Mistral
    "receipt_specialist": "#B3D9FF",  # light blue — Gemini
    "po_specialist":      "#B3D9FF",
    "bank_specialist":    "#B3D9FF",
    "resume_specialist":  "#B3D9FF",
    "validator":          "#B3D9FF",
    "__end__":            "#C8A8E9",  # light purple
}

# node labels
labels = {
    "__start__":          "__start__",
    "preprocessor":       "preprocessor\n(OpenCV)",
    "extractor":          "extractor\n(Gemini Vision)",
    "classifier":         "classifier\n(Gemini Flash)",
    "router":             "router\n(conditional)",
    "json_specialist":    "json_specialist\n(Mistral ★)",
    "receipt_specialist": "receipt\n(Gemini Flash)",
    "po_specialist":      "purchase order\n(Gemini Flash)",
    "bank_specialist":    "bank statement\n(Gemini Flash)",
    "resume_specialist":  "resume\n(Gemini Flash)",
    "validator":          "validator\n(jsonschema)",
    "__end__":            "__end__",
}

fig, ax = plt.subplots(1, 1, figsize=(14, 14))
fig.patch.set_facecolor("#1a1a2e")
ax.set_facecolor("#1a1a2e")

# draw edges first (so nodes appear on top)
for (src, dst) in edges:
    x1, y1 = pos[src]
    x2, y2 = pos[dst]

    # offset arrow start/end so they don't overlap node boxes
    dy = y2 - y1
    dx = x2 - x1
    length = (dx**2 + dy**2) ** 0.5
    offset = 0.38
    ox = offset * dx / length
    oy = offset * dy / length

    ax.annotate(
        "",
        xy=(x2 - ox, y2 - oy),
        xytext=(x1 + ox, y1 + oy),
        arrowprops=dict(
            arrowstyle="-|>",
            color="#aaaaaa",
            lw=1.2,
        )
    )

# draw nodes
for node in nodes:
    x, y = pos[node]
    is_terminal = node in ["__start__", "__end__"]
    box_style = "round,pad=0.4" if is_terminal else "round,pad=0.5"

    ax.text(
        x, y, labels[node],
        ha="center", va="center",
        fontsize=9, fontweight="bold",
        color="#1a1a2e",
        bbox=dict(
            boxstyle=box_style,
            facecolor=node_colors[node],
            edgecolor="#ffffff",
            linewidth=1.5
        )
    )

# edge labels on router fan-out
route_labels = {
    ("router", "json_specialist"):    "invoice/product",
    ("router", "receipt_specialist"): "receipt",
    ("router", "po_specialist"):      "purchase_order",
    ("router", "bank_specialist"):    "bank_statement",
    ("router", "resume_specialist"):  "resume",
}

for (src, dst), label in route_labels.items():
    x1, y1 = pos[src]
    x2, y2 = pos[dst]
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    ax.text(
        mx + 0.15, my, label,
        ha="left", va="center",
        fontsize=7, color="#dddddd",
        style="italic"
    )

# title
ax.set_title(
    "Document Processing Pipeline — Multi-Agent System",
    color="white", fontsize=13, fontweight="bold", pad=15
)

# legend
legend_elements = [
    mpatches.Patch(facecolor="#B3D9FF", edgecolor="white", label="Gemini Agent"),
    mpatches.Patch(facecolor="#FFD700", edgecolor="white", label="Fine-tuned Mistral ★"),
    mpatches.Patch(facecolor="#FFB347", edgecolor="white", label="Router (conditional)"),
    mpatches.Patch(facecolor="#C8E6C9", edgecolor="white", label="Start / End"),
    mpatches.Patch(facecolor="#C8A8E9", edgecolor="white", label="End"),
]
ax.legend(
    handles=legend_elements,
    loc="lower right",
    facecolor="#2a2a4e",
    labelcolor="white",
    fontsize=9
)

ax.set_xlim(-5.5, 5.5)
ax.set_ylim(1, 12.5)
ax.axis("off")

plt.tight_layout(rect=[0, 0, 1, 0.97])
plt.savefig("outputs/pipeline_graph.png", dpi=150,
            bbox_inches="tight", facecolor="#1a1a2e")
plt.show()
print("Graph saved to outputs/pipeline_graph.png ✓")