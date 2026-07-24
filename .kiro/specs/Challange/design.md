# Design Document — VAST Challenge 2026 MC1

## Overview

The project is a fully automated visual analytics pipeline that answers the three VAST Challenge MC1 questions. The entire pipeline is triggered by running `main.py`, which calls each analysis module in sequence and saves all output figures to an `output/` folder. No interactive system is built — the deliverables are publication-quality static figures generated from the `MC1_final_00.json` dataset.

---

## Architecture

The project is structured as a set of Python scripts connected through `main.py`. Each script is responsible for one logical layer — data loading, preprocessing, or analysis/visualization. Scripts do not depend on each other directly; they all receive clean DataFrames from the preprocessing layer.

```
main.py
│
├── preprocessing.py         # Loads JSON → produces df_rounds, df_comms
│
├── q1_event_sequence.py     # Answers Question 1
├── q2_behavioral_baseline.py # Answers Question 2
├── q3_leading_indicators.py # Answers Question 3
│
└── output/                  # All figures saved here as PNG
```

---

## Data Layer — preprocessing.py

The JSON has two logical entities that map to two DataFrames:

### df_rounds
One row per hour (23 rows total). Captures the world state each round.

| Column | Source | Description |
|---|---|---|
| `hour` | `rounds[].hour` | ISO timestamp of the round |
| `event_headline` | `rounds[].environment_context.event_headline` | One-line summary of the hour |
| `event_narrative` | `rounds[].environment_context.event_narrative` | Full narrative of the hour |
| `stock_price` | `rounds[].environment_context.market_snapshot.stock_price` | Stock price that hour |
| `percent_change` | `rounds[].environment_context.market_snapshot.percent_change` | Stock % change |
| `market_sentiment` | `rounds[].environment_context.market_snapshot.sentiment` | neutral / negative / critical |
| `social_state` | `rounds[].environment_context.social_state` | External social media state |
| `agents_unavailable` | `rounds[].environment_context.agents_unavailable` | Agents not active this round |
| `critical_deadlines` | `rounds[].environment_context.critical_deadlines` | Deadlines mentioned |
| `trending_hashtags` | `rounds[].environment_context.market_snapshot.trending_hashtags` | Trending tags |
| `media_events` | `rounds[].environment_context.media_events` | External press events |
| `news` | `rounds[].environment_context.news` | News items |

### df_comms
One row per message (all messages across all 23 rounds). The `hour` field is stamped onto each message from its parent round so messages can be linked back to the world state.

| Column | Source | Description |
|---|---|---|
| `hour` | Stamped from parent round | Links message to its round |
| `message_id` | `communications[].message_id` | Unique message identifier |
| `agent_id` | `communications[].agent_id` | Who sent the message |
| `agent_role` | `communications[].agent_role` | Role of the sender |
| `agent_label` | `communications[].agent_label` | Display name |
| `channel` | `communications[].channel` | Where it was sent |
| `recipients` | `communications[].recipients` | Who received it |
| `participants` | `communications[].participants` | Who participated (side/1:1 chats) |
| `message_type` | `communications[].message_type` | broadcast / one_on_one_chat / public_post |
| `responding_to` | `communications[].responding_to` | message_id this replies to (null if new thread) |
| `content` | `communications[].content` | What the agent said publicly |
| `timestamp` | `communications[].timestamp` | Exact message timestamp |
| `sentiment_at_turn` | `communications[].sentiment_at_turn` | neutral / cautious / negative / critical |
| `declared_action` | `communications[].declared_action` | Agent's declared action this turn |
| `action_classification` | `communications[].action_classification` | Classification of the action |
| `internal_state.reacting` | `communications[].internal_state.reacting` | Immediate emotional reaction |
| `internal_state.rationalizing` | `communications[].internal_state.rationalizing` | How the agent justifies their thinking |
| `internal_state.deliberating` | `communications[].internal_state.deliberating` | Full private reasoning (richest field) |

---

## Question 1 — Event Sequence (q1_event_sequence.py)

### Goal
Reconstruct the causal chain from normal operations through to the embargo breach, showing which agents made which decisions and how each decision triggered the next.

### Approach
The `responding_to` field is the key. Every message either starts a thread (`null`) or replies to a specific `message_id`. By tracing backward from the breach post on `flex_official`, we can reconstruct the exact decision chain.

**Known breach chain from data inspection:**
```
flex_official post (breach)
    ← pr_intern_agent instructed by pr_agent
        ← pr_agent instructed by legal_agent ("instruct PR-Intern NOW")
            ← legal_agent executing Scenario B under crisis pressure
                ← crisis triggered by SaltWind article + stock dropping 8%
                    ← near-miss by social_media_agent (@ElenaMarquez post, Week 2)
                        ← no enforcement mechanism for interns
```

### Figures

**Figure 1.1 — Timeline of Key Events**
A horizontal timeline showing all 23 rounds on the x-axis (time) with annotated events:
- Stock price line overlaid
- Vertical markers for key events (AG inquiry, near-miss post, SaltWind article, breach)
- Color-coded by market sentiment (neutral → negative → critical)
- Built using: `seaborn.lineplot` + `matplotlib.axvline` annotations

**Figure 1.2 — Message Response Chain (Breach Trace)**
A directed chain visualization showing the `responding_to` links from the breach post backward through all contributing messages. Each node is a message, colored by `agent_id`, with the channel shown on each edge.
- Filter: only messages in the chain leading to the breach
- Built using: `matplotlib` with arrow annotations, nodes positioned chronologically

**Figure 1.3 — Channel Activity by Round**
A heatmap showing how many messages were sent on each channel per round. The breach round should visually stand out as the round with the highest `flex_official` + `anonymous_post` activity.
- x-axis: rounds (hour), y-axis: channel
- Built using: `seaborn.heatmap`

---

## Question 2 — Behavioral Baseline vs. Anomaly (q2_behavioral_baseline.py)

### Goal
Establish what normal agent behavior looks like across the pre-crisis rounds, then show how the crisis round deviates from that baseline.

### Approach
Normal behavior = rounds 1–18 (pre-crisis). Anomalous behavior = rounds 19–23 (crisis period). Compare message counts, channel usage, sentiment, and declared actions between the two periods.

### Figures

**Figure 2.1 — Agent Message Volume by Round**
A grouped bar chart showing how many messages each agent sent per round. The crisis rounds should show a spike in `legal_agent`, `pr_agent`, and `social_media_agent` activity.
- x-axis: rounds, y-axis: message count
- Color: one color per agent
- Built using: `seaborn.barplot`

**Figure 2.2 — Sentiment Distribution: Baseline vs. Crisis**
Two side-by-side pie or bar charts showing the distribution of `sentiment_at_turn` values in normal rounds vs. crisis rounds. Expected shift: baseline is mostly `neutral/cautious`, crisis is mostly `negative/critical`.
- Built using: `seaborn.countplot`

**Figure 2.3 — Channel Usage Shift**
A stacked bar chart comparing the proportion of messages on each channel in normal rounds vs. crisis rounds. Expected finding: `side_huddle` and `one_on_one_chat` dominate in crisis as agents move off the main channel.
- Built using: `seaborn.histplot` or `matplotlib.bar`

**Figure 2.4 — Agent Declared Action Heatmap**
A heatmap showing each agent's `declared_action` per round. Baseline should show mostly `MONITORING`. Crisis rounds should show `CRITICAL` and `RECOVERING` appearing for the first time.
- x-axis: rounds, y-axis: agent
- Built using: `seaborn.heatmap`

---

## Question 3 — Leading Indicators (q3_leading_indicators.py)

### Goal
Show that the conditions enabling the breach were visible before it happened — in prior near-misses, in sentiment shifts, and in the absence of enforcement after early warning events.

### Approach
Focus on three signals:
1. The `@ElenaMarquez` near-miss post (Week 2, `social_media_agent`) — an early embargo-adjacent post that was caught but not enforced structurally
2. The `internal_state.deliberating` text for `pr_intern_agent` — shows growing pressure and awareness of the embargo
3. The intern hallway leak about "CivicLoom timeline at 6 PM" — an information leak that reached unclearanced agents before the breach

### Figures

**Figure 3.1 — Sentiment Trajectory by Agent Over Time**
A line plot showing `sentiment_at_turn` (mapped to numeric: neutral=0, cautious=1, negative=2, critical=3) per agent across all 23 rounds. Shows which agents escalated earliest and which were the last to reach critical sentiment.
- Built using: `seaborn.lineplot` with hue per agent

**Figure 3.2 — Near-Miss Event Markers**
The same timeline from Figure 1.1 but with additional annotations marking:
- The `@ElenaMarquez` post (near-miss, Week 2)
- The hallway leak about "CivicLoom 6 PM"
- The compliance monitor being added
- The actual breach
This shows the gap between when warnings appeared and when action was taken.
- Built using: `matplotlib` annotations on `seaborn.lineplot`

**Figure 3.3 — Private vs. Public Channel Ratio Over Time**
A line plot showing the ratio of private channel messages (`one_on_one_chat`, `side_huddle`) to public channel messages (`comms_huddle`, `official_post`) per round. A rising ratio means agents are moving sensitive communication off the record — a leading indicator of pressure building.
- Built using: `seaborn.lineplot`

**Figure 3.4 — pr_intern_agent Activity Timeline**
A focused plot showing only `pr_intern_agent` messages across all rounds — channel used, message type, and whether `internal_state` was populated. Highlights the round where the intern first received instructions to post, and the round where the breach occurred.
- Built using: `seaborn.scatterplot` + annotations

---

## Output

All figures are saved as PNG files to the `output/` directory. File naming convention:

```
output/
├── q1_01_timeline.png
├── q1_02_breach_chain.png
├── q1_03_channel_heatmap.png
├── q2_01_message_volume.png
├── q2_02_sentiment_distribution.png
├── q2_03_channel_usage_shift.png
├── q2_04_declared_action_heatmap.png
├── q3_01_sentiment_trajectory.png
├── q3_02_near_miss_markers.png
├── q3_03_private_public_ratio.png
├── q3_04_pr_intern_timeline.png
```

---

## Execution Flow — main.py

```
main.py
  1. Call preprocessing.py → returns df_rounds, df_comms
  2. Call q1_event_sequence.py(df_rounds, df_comms) → saves q1_*.png
  3. Call q2_behavioral_baseline.py(df_rounds, df_comms) → saves q2_*.png
  4. Call q3_leading_indicators.py(df_rounds, df_comms) → saves q3_*.png
  5. Print "All figures saved to output/"
```

---

## Dependencies

| Library | Version | Purpose |
|---|---|---|
| `pandas` | latest | DataFrames |
| `matplotlib` | latest | Base plotting |
| `seaborn` | latest | Statistical visualization |
| `json` | stdlib | JSON parsing |
| `os` | stdlib | Output directory creation |
