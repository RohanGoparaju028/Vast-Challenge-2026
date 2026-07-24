import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns

PRIVATE_CHANNELS = ["one_on_one_chat", "side_huddle"]
PUBLIC_CHANNELS = ["comms_huddle", "official_post", "personal_post", "anonymous_post"]

AGENT_COLORS = {
    "legal_agent":        "#2196F3",
    "quality_agent":      "#4CAF50",
    "pr_agent":           "#FF9800",
    "social_media_agent": "#9C27B0",
    "pr_intern_agent":    "#F44336",
    "intern_agent":       "#00BCD4",
    "judge_agent":        "#795548",
}

# Key leading indicator events from JSON inspection
INDICATOR_EVENTS = [
    ("2046-05-26", "#FF6F00", "Near-Miss:\n@ElenaMarquez\nPost (social_media_agent)"),
    ("2046-05-30", "#795548", "Judge Added\nto Comms Huddle"),
    ("2046-06-03", "#E53935", "SaltWind Article\nStock -8%"),
    ("2046-06-04", "#B71C1C", "Intern Hallway\nLeak: CivicLoom\n6PM Timeline"),
    ("2046-06-05", "#000000", "EMBARGO\nBREACH"),
]


def run(df, output_dir="output"):
    os.makedirs(output_dir, exist_ok=True)

    _fig1_private_public_ratio(df, output_dir)
    _fig2_near_miss_timeline(df, output_dir)
    _fig3_pr_intern_activity(df, output_dir)

    print("[Q3] All figures saved.")


# --- Figure 1: Private vs Public channel ratio per round ---
def _fig1_private_public_ratio(df, output_dir):
    df = df.copy()
    df["channel_type"] = df["channel"].apply(
        lambda c: "Private" if c in PRIVATE_CHANNELS else "Public"
    )

    ratio_df = (
        df.groupby(["hour", "channel_type"])
        .size()
        .reset_index(name="count")
        .pivot(index="hour", columns="channel_type", values="count")
        .fillna(0)
        .reset_index()
    )

    # Ensure both columns exist
    for col in ["Private", "Public"]:
        if col not in ratio_df.columns:
            ratio_df[col] = 0

    ratio_df["ratio"] = ratio_df["Private"] / (ratio_df["Public"] + 1)  # +1 to avoid div/0
    ratio_df["hour_dt"] = pd.to_datetime(ratio_df["hour"])

    fig, ax = plt.subplots(figsize=(16, 5))
    ax.plot(
        ratio_df["hour_dt"],
        ratio_df["ratio"],
        color="#7B1FA2",
        linewidth=2,
        marker="o",
        markersize=5,
        label="Private / Public Ratio",
    )
    ax.fill_between(ratio_df["hour_dt"], ratio_df["ratio"], alpha=0.15, color="#CE93D8")

    # Annotate key events
    for date_str, color, label in INDICATOR_EVENTS:
        dt = pd.to_datetime(date_str)
        ax.axvline(dt, color=color, linestyle="--", linewidth=1.2, alpha=0.85)
        ax.text(
            dt, ratio_df["ratio"].max() * 0.95,
            label, fontsize=6.5, color=color,
            ha="center", va="top",
            bbox=dict(boxstyle="round,pad=0.2", fc="white", alpha=0.75),
        )

    ax.axhline(ratio_df["ratio"].mean(), color="#9E9E9E", linestyle=":", linewidth=1, label="Mean Ratio")
    ax.set_title(
        "Q3 — Private vs Public Channel Ratio per Round\n"
        "(Rising ratio = agents moving sensitive talk off the record → leading indicator)",
        fontsize=13, pad=12,
    )
    ax.set_xlabel("Round (Hour)", fontsize=10)
    ax.set_ylabel("Private / Public Message Ratio", fontsize=10)
    ax.legend(fontsize=8)
    plt.xticks(
        ratio_df["hour_dt"],
        [str(h)[:10] for h in ratio_df["hour"]],
        rotation=45, ha="right", fontsize=7,
    )
    plt.tight_layout()
    fig.savefig(os.path.join(output_dir, "q3_01_private_public_ratio.png"), dpi=150)
    plt.close(fig)


# --- Figure 2: Near-miss timeline — message volume with all indicator events marked ---
def _fig2_near_miss_timeline(df, output_dir):
    # Message volume per agent per round
    vol = (
        df.groupby(["hour", "agent_id"])
        .size()
        .reset_index(name="count")
    )
    vol["hour_dt"] = pd.to_datetime(vol["hour"])

    fig, ax = plt.subplots(figsize=(18, 6))

    for agent, grp in vol.groupby("agent_id"):
        color = AGENT_COLORS.get(agent, "#9E9E9E")
        ax.plot(
            grp["hour_dt"], grp["count"],
            color=color, linewidth=1.5, marker="o", markersize=4,
            label=agent.replace("_", " ").title(),
        )

    # Annotate all leading indicator events
    for date_str, color, label in INDICATOR_EVENTS:
        dt = pd.to_datetime(date_str)
        ax.axvline(dt, color=color, linestyle="--", linewidth=1.3, alpha=0.85)
        ax.text(
            dt, vol["count"].max() * 0.92,
            label, fontsize=6.5, color=color,
            ha="center", va="top",
            bbox=dict(boxstyle="round,pad=0.2", fc="white", alpha=0.75),
        )

    ax.set_title(
        "Q3 — Leading Indicator Timeline: Agent Activity with Near-Miss & Breach Events\n"
        "(Spikes before breach show escalating pressure; near-miss shows structural risk existed earlier)",
        fontsize=13, pad=12,
    )
    ax.set_xlabel("Round (Hour)", fontsize=10)
    ax.set_ylabel("Messages Sent", fontsize=10)
    ax.legend(title="Agent", fontsize=8, loc="upper left")

    all_hours = sorted(vol["hour_dt"].unique())
    plt.xticks(all_hours, [str(h)[:10] for h in all_hours], rotation=45, ha="right", fontsize=7)
    plt.tight_layout()
    fig.savefig(os.path.join(output_dir, "q3_02_near_miss_timeline.png"), dpi=150)
    plt.close(fig)


# --- Figure 3: pr_intern_agent full activity timeline ---
def _fig3_pr_intern_activity(df, output_dir):
    intern_df = df[df["agent_id"] == "pr_intern_agent"].copy()
    intern_df["hour_dt"] = pd.to_datetime(intern_df["hour"])
    intern_df["ts_dt"] = pd.to_datetime(intern_df["timestamp"])

    # Map channels to y positions for scatter
    channels = sorted(intern_df["channel"].unique())
    channel_y = {ch: i for i, ch in enumerate(channels)}
    intern_df["channel_y"] = intern_df["channel"].map(channel_y)

    # Whether internal state was populated this message
    intern_df["has_internal_state"] = (
        intern_df["internal_state.deliberating"].notna()
        | intern_df["internal_state.reacting"].notna()
        | intern_df["internal_state.rationalizing"].notna()
    )

    fig, ax = plt.subplots(figsize=(16, 5))

    # Plot each message as a scatter point
    for _, row in intern_df.iterrows():
        marker = "★" if row["has_internal_state"] else "o"
        color = "#F44336" if row["channel"] == "official_post" else "#FF9800" if row["channel"] == "anonymous_post" else "#90A4AE"
        ax.scatter(
            row["ts_dt"], row["channel_y"],
            color=color, s=120 if row["has_internal_state"] else 60,
            zorder=3, marker="*" if row["has_internal_state"] else "o",
        )

    # Annotate key events
    for date_str, color, label in INDICATOR_EVENTS:
        dt = pd.to_datetime(date_str)
        ax.axvline(dt, color=color, linestyle="--", linewidth=1.2, alpha=0.85)
        ax.text(
            dt, len(channels) - 0.3,
            label, fontsize=6.5, color=color,
            ha="center", va="top",
            bbox=dict(boxstyle="round,pad=0.2", fc="white", alpha=0.75),
        )

    ax.set_yticks(list(channel_y.values()))
    ax.set_yticklabels(list(channel_y.keys()), fontsize=9)
    ax.set_title(
        "Q3 — pr_intern_agent Activity Timeline\n"
        "(★ = message with internal state populated | Red = official_post | Orange = anonymous_post)",
        fontsize=13, pad=12,
    )
    ax.set_xlabel("Timestamp", fontsize=10)
    ax.set_ylabel("Channel", fontsize=10)

    # Legend
    legend_handles = [
        mpatches.Patch(color="#F44336", label="official_post (breach channel)"),
        mpatches.Patch(color="#FF9800", label="anonymous_post"),
        mpatches.Patch(color="#90A4AE", label="other channels"),
        plt.scatter([], [], marker="*", color="black", s=100, label="Internal state populated"),
    ]
    ax.legend(handles=legend_handles, fontsize=8, loc="upper left")

    plt.xticks(rotation=45, ha="right", fontsize=7)
    plt.tight_layout()
    fig.savefig(os.path.join(output_dir, "q3_03_pr_intern_activity.png"), dpi=150)
    plt.close(fig)
