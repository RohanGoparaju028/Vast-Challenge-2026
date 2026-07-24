import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns

# Crisis period starts at round 19 (index-based on hour)
CRISIS_START = "2046-06-03"

AGENT_COLORS = {
    "legal_agent": "#2196F3",
    "quality_agent": "#4CAF50",
    "pr_agent": "#FF9800",
    "social_media_agent": "#9C27B0",
    "pr_intern_agent": "#F44336",
    "intern_agent": "#00BCD4",
    "judge_agent": "#795548",
}

PRIVATE_CHANNELS = ["one_on_one_chat", "side_huddle"]
PUBLIC_CHANNELS = ["comms_huddle", "official_post", "personal_post", "anonymous_post"]


def run(df, output_dir="output"):
    os.makedirs(output_dir, exist_ok=True)

    # Tag each row as baseline or crisis
    df = df.copy()
    df["period"] = df["hour"].apply(
        lambda h: "Crisis" if h >= CRISIS_START else "Baseline"
    )

    _fig1_message_volume_heatmap(df, output_dir)
    _fig2_agent_message_count_by_period(df, output_dir)
    _fig3_channel_shift(df, output_dir)
    _fig4_internal_state_pie(df, output_dir)

    print("[Q2] All figures saved.")


# --- Figure 1: Agent x Round message count heatmap ---
def _fig1_message_volume_heatmap(df, output_dir):
    pivot = (
        df.groupby(["hour", "agent_id"])
        .size()
        .reset_index(name="count")
        .pivot(index="agent_id", columns="hour", values="count")
        .fillna(0)
    )

    # Shorten hour labels to date only for readability
    pivot.columns = [str(c)[:10] for c in pivot.columns]

    fig, ax = plt.subplots(figsize=(18, 5))
    sns.heatmap(
        pivot,
        ax=ax,
        cmap="YlOrRd",
        linewidths=0.4,
        linecolor="white",
        annot=True,
        fmt=".0f",
        cbar_kws={"label": "Message Count"},
    )
    ax.set_title("Q2 — Agent Message Volume per Round (Baseline vs Crisis)", fontsize=14, pad=12)
    ax.set_xlabel("Round (Hour)", fontsize=10)
    ax.set_ylabel("Agent", fontsize=10)
    plt.xticks(rotation=45, ha="right", fontsize=7)
    plt.tight_layout()
    fig.savefig(os.path.join(output_dir, "q2_01_message_volume_heatmap.png"), dpi=150)
    plt.close(fig)


# --- Figure 2: Message count per agent — Baseline vs Crisis grouped bar ---
def _fig2_agent_message_count_by_period(df, output_dir):
    counts = (
        df.groupby(["agent_id", "period"])
        .size()
        .reset_index(name="count")
    )

    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(
        data=counts,
        x="agent_id",
        y="count",
        hue="period",
        palette={"Baseline": "#90CAF9", "Crisis": "#F44336"},
        ax=ax,
    )
    ax.set_title("Q2 — Message Count per Agent: Baseline vs Crisis", fontsize=14, pad=12)
    ax.set_xlabel("Agent", fontsize=10)
    ax.set_ylabel("Total Messages", fontsize=10)
    plt.xticks(rotation=20, ha="right")
    plt.legend(title="Period")
    plt.tight_layout()
    fig.savefig(os.path.join(output_dir, "q2_02_agent_message_count_by_period.png"), dpi=150)
    plt.close(fig)


# --- Figure 3: Channel usage shift — Baseline vs Crisis stacked bars ---
def _fig3_channel_shift(df, output_dir):
    channel_counts = (
        df.groupby(["period", "channel"])
        .size()
        .reset_index(name="count")
    )

    baseline = channel_counts[channel_counts["period"] == "Baseline"].set_index("channel")["count"]
    crisis = channel_counts[channel_counts["period"] == "Crisis"].set_index("channel")["count"]
    all_channels = sorted(set(baseline.index) | set(crisis.index))
    baseline = baseline.reindex(all_channels, fill_value=0)
    crisis = crisis.reindex(all_channels, fill_value=0)

    x = range(len(all_channels))
    width = 0.35

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar([i - width / 2 for i in x], baseline, width, label="Baseline", color="#90CAF9")
    ax.bar([i + width / 2 for i in x], crisis, width, label="Crisis", color="#F44336")
    ax.set_xticks(list(x))
    ax.set_xticklabels(all_channels, rotation=25, ha="right")
    ax.set_title("Q2 — Channel Usage Shift: Baseline vs Crisis", fontsize=14, pad=12)
    ax.set_xlabel("Channel", fontsize=10)
    ax.set_ylabel("Message Count", fontsize=10)
    ax.legend(title="Period")
    plt.tight_layout()
    fig.savefig(os.path.join(output_dir, "q2_03_channel_shift.png"), dpi=150)
    plt.close(fig)


# --- Figure 4: Internal state composition per agent — pie charts ---
def _fig4_internal_state_pie(df, output_dir):
    # Count non-null internal state fields per agent
    agents = df["agent_id"].unique()
    state_cols = {
        "reacting": "internal_state.reacting",
        "rationalizing": "internal_state.rationalizing",
        "deliberating": "internal_state.deliberating",
    }

    # Only keep rows where at least one internal state field is populated
    state_df = df[
        df["internal_state.reacting"].notna()
        | df["internal_state.rationalizing"].notna()
        | df["internal_state.deliberating"].notna()
    ].copy()

    fig, axes = plt.subplots(2, 4, figsize=(20, 10))
    axes = axes.flatten()
    colors = ["#2196F3", "#FF9800", "#F44336"]

    for i, agent in enumerate(sorted(agents)):
        agent_df = state_df[state_df["agent_id"] == agent]
        counts = [
            agent_df["internal_state.reacting"].notna().sum(),
            agent_df["internal_state.rationalizing"].notna().sum(),
            agent_df["internal_state.deliberating"].notna().sum(),
        ]
        labels = ["Reacting", "Rationalizing", "Deliberating"]

        # Filter out zero slices
        non_zero = [(l, c, col) for l, c, col in zip(labels, counts, colors) if c > 0]
        if not non_zero:
            axes[i].set_visible(False)
            continue

        lz, cz, colz = zip(*non_zero)
        axes[i].pie(cz, labels=lz, colors=colz, autopct="%1.0f%%", startangle=90)
        axes[i].set_title(agent.replace("_", " ").title(), fontsize=10)

    # Hide unused subplots
    for j in range(len(agents), len(axes)):
        axes[j].set_visible(False)

    fig.suptitle(
        "Q2 — Internal State Composition per Agent\n(Proportion of populated reacting / rationalizing / deliberating fields)",
        fontsize=13,
        y=1.01,
    )
    plt.tight_layout()
    fig.savefig(os.path.join(output_dir, "q2_04_internal_state_pie.png"), dpi=150, bbox_inches="tight")
    plt.close(fig)
