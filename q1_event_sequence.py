import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns

# Known breach message — pr_intern_agent posting on official_post channel
# Traced from JSON inspection: legal_agent instructed pr_agent -> pr_intern_agent
BREACH_AGENT = "pr_intern_agent"
BREACH_CHANNEL = "official_post"

# Key annotated events found from JSON inspection
KEY_EVENTS = [
    ("2046-05-17", "AG Inquiries\nFlagged"),
    ("2046-05-26", "Near-Miss:\n@ElenaMarquez\nPost"),
    ("2046-05-30", "Judge Arrives\nin Comms Huddle"),
    ("2046-06-03", "SaltWind Article\nStock -8%"),
    ("2046-06-05", "EMBARGO\nBREACH"),
]

AGENT_COLORS = {
    "legal_agent":        "#2196F3",
    "quality_agent":      "#4CAF50",
    "pr_agent":           "#FF9800",
    "social_media_agent": "#9C27B0",
    "pr_intern_agent":    "#F44336",
    "intern_agent":       "#00BCD4",
    "judge_agent":        "#795548",
}


def run(df, output_dir="output"):
    os.makedirs(output_dir, exist_ok=True)

    _fig1_event_timeline(df, output_dir)
    _fig2_breach_chain(df, output_dir)
    _fig3_channel_activity_heatmap(df, output_dir)

    print("[Q1] All figures saved.")


# --- Figure 1: Event timeline with stock price and key event markers ---
def _fig1_event_timeline(df, output_dir):
    # Build per-round summary
    rounds = (
        df.groupby("hour")
        .agg(
            message_count=("message_id", "count"),
            stock_price=("environment_context.market_snapshot.stock_price", "first"),
            headline=("environment_context.event_headline", "first"),
        )
        .reset_index()
    )

    # Parse stock price to float
    rounds["stock_val"] = (
        rounds["stock_price"]
        .str.replace("$", "", regex=False)
        .str.replace(",", "")
        .astype(float)
    )

    rounds["hour_dt"] = pd.to_datetime(rounds["hour"])

    fig, ax1 = plt.subplots(figsize=(18, 6))

    # Stock price line
    ax1.plot(
        rounds["hour_dt"],
        rounds["stock_val"],
        color="#1565C0",
        linewidth=2,
        marker="o",
        markersize=4,
        label="Stock Price ($)",
    )
    ax1.set_ylabel("Stock Price ($)", color="#1565C0", fontsize=10)
    ax1.tick_params(axis="y", labelcolor="#1565C0")

    # Message volume bars on secondary axis
    ax2 = ax1.twinx()
    ax2.bar(
        rounds["hour_dt"],
        rounds["message_count"],
        color="#BBDEFB",
        alpha=0.5,
        width=0.03,
        label="Message Count",
    )
    ax2.set_ylabel("Message Count", color="#90A4AE", fontsize=10)
    ax2.tick_params(axis="y", labelcolor="#90A4AE")

    # Key event vertical markers
    for date_str, label in KEY_EVENTS:
        dt = pd.to_datetime(date_str)
        color = "#F44336" if "BREACH" in label else "#FF6F00" if "Near-Miss" in label else "#546E7A"
        ax1.axvline(dt, color=color, linestyle="--", linewidth=1.2, alpha=0.8)
        ax1.text(
            dt, rounds["stock_val"].min() - 0.5,
            label, fontsize=6.5, color=color,
            ha="center", va="top", rotation=0,
            bbox=dict(boxstyle="round,pad=0.2", fc="white", alpha=0.7),
        )

    ax1.set_title(
        "Q1 — Event Timeline: Stock Price, Message Volume & Key Events",
        fontsize=14, pad=12,
    )
    ax1.set_xlabel("Round (Hour)", fontsize=10)
    plt.xticks(rounds["hour_dt"], [str(h)[:10] for h in rounds["hour"]], rotation=45, ha="right", fontsize=7)

    # Combined legend
    handles = [
        mpatches.Patch(color="#1565C0", label="Stock Price"),
        mpatches.Patch(color="#BBDEFB", label="Message Count"),
        mpatches.Patch(color="#F44336", label="Embargo Breach"),
        mpatches.Patch(color="#FF6F00", label="Near-Miss Event"),
    ]
    ax1.legend(handles=handles, loc="upper right", fontsize=8)

    plt.tight_layout()
    fig.savefig(os.path.join(output_dir, "q1_01_event_timeline.png"), dpi=150)
    plt.close(fig)


# --- Figure 2: Breach chain — trace responding_to backward from breach post ---
def _fig2_breach_chain(df, output_dir):
    # Find the breach post — pr_intern_agent on official_post channel in last round
    breach_candidates = df[
        (df["agent_id"] == BREACH_AGENT) &
        (df["channel"] == BREACH_CHANNEL)
    ].sort_values("timestamp")

    if breach_candidates.empty:
        print("[Q1] Warning: breach post not found, skipping Fig 2.")
        return

    breach_msg = breach_candidates.iloc[-1]

    # Build a lookup from message_id -> row
    msg_lookup = df.set_index("message_id")

    # Walk backward through responding_to chain (max 15 steps)
    chain = [breach_msg]
    current = breach_msg
    for _ in range(15):
        parent_id = current.get("responding_to")
        if pd.isna(parent_id) or parent_id not in msg_lookup.index:
            break
        current = msg_lookup.loc[parent_id]
        chain.append(current)

    chain = list(reversed(chain))  # oldest first

    # Plot as a vertical chain of annotated boxes
    fig, ax = plt.subplots(figsize=(14, len(chain) * 1.6 + 1))
    ax.set_xlim(0, 10)
    ax.set_ylim(-0.5, len(chain))
    ax.axis("off")

    ax.set_title(
        "Q1 — Breach Decision Chain (Traced via responding_to)",
        fontsize=13, pad=12,
    )

    for i, row in enumerate(chain):
        agent = row.get("agent_id", "unknown")
        channel = row.get("channel", "")
        content = str(row.get("content", ""))[:120]
        timestamp = str(row.get("timestamp", ""))[:16]
        color = AGENT_COLORS.get(agent, "#BDBDBD")
        is_breach = (i == len(chain) - 1)

        box_color = "#FFEBEE" if is_breach else "#F5F5F5"
        edge_color = "#F44336" if is_breach else color

        # Box
        ax.add_patch(
            mpatches.FancyBboxPatch(
                (0.3, i - 0.35), 9.4, 0.8,
                boxstyle="round,pad=0.05",
                facecolor=box_color,
                edgecolor=edge_color,
                linewidth=2 if is_breach else 1,
            )
        )

        # Agent label dot
        ax.add_patch(plt.Circle((0.75, i + 0.05), 0.18, color=color, zorder=3))

        # Text
        ax.text(1.1, i + 0.2, f"{agent}  [{channel}]  {timestamp}",
                fontsize=8, fontweight="bold", color=edge_color, va="center")
        ax.text(1.1, i - 0.1, content + ("..." if len(str(row.get("content", ""))) > 120 else ""),
                fontsize=7, color="#424242", va="center")

        # Arrow to next
        if i < len(chain) - 1:
            ax.annotate(
                "", xy=(5, i + 0.45), xytext=(5, i + 0.55),
                arrowprops=dict(arrowstyle="->", color="#757575", lw=1.2),
            )

    plt.tight_layout()
    fig.savefig(os.path.join(output_dir, "q1_02_breach_chain.png"), dpi=150, bbox_inches="tight")
    plt.close(fig)


# --- Figure 3: Channel activity heatmap per round ---
def _fig3_channel_activity_heatmap(df, output_dir):
    pivot = (
        df.groupby(["hour", "channel"])
        .size()
        .reset_index(name="count")
        .pivot(index="channel", columns="hour", values="count")
        .fillna(0)
    )
    pivot.columns = [str(c)[:10] for c in pivot.columns]

    fig, ax = plt.subplots(figsize=(18, 5))
    sns.heatmap(
        pivot,
        ax=ax,
        cmap="Blues",
        linewidths=0.4,
        linecolor="white",
        annot=True,
        fmt=".0f",
        cbar_kws={"label": "Message Count"},
    )
    ax.set_title(
        "Q1 — Channel Activity per Round\n(High official_post / anonymous_post in breach round = anomaly)",
        fontsize=13, pad=12,
    )
    ax.set_xlabel("Round (Hour)", fontsize=10)
    ax.set_ylabel("Channel", fontsize=10)
    plt.xticks(rotation=45, ha="right", fontsize=7)
    plt.tight_layout()
    fig.savefig(os.path.join(output_dir, "q1_03_channel_activity_heatmap.png"), dpi=150)
    plt.close(fig)
