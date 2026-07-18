# VAST Challenge 2026 — Mini-Challenge 1
## Multi-Agent Crisis Communications Analysis

---

## Overview

This project is a submission for the **VAST Challenge 2026, Mini-Challenge 1**. The challenge centers on a corporate communications crisis at **TenantThread**, a proptech company, during a two-week period leading up to and including a high-stakes merger announcement.

A communications embargo was in place around the merger with **CivicLoom** (internal codename: **Project HarborCrest**), but an unauthorized social media post was released before the embargo lifted at 6:00 PM on the crisis day. The dataset captures the behavior of 7 interacting AI agents as they communicate across multiple channels and make real-time decisions about what to publish and what to withhold.

The goal of the challenge is to use **visual analytics** to investigate how and why the inappropriate release occurred, characterize normal vs. anomalous agent behavior, and identify leading indicators that such a breach was possible.

---

## Repository Structure

```
VAST_Challenge_2026_MC1/
├── MC1_final_00.json                   # Primary dataset (two-week agent communication log)
├── mc1 data description.md             # Official data description and schema reference
├── VAST Challenge 2026 MC1 Answer Sheet.htm  # Submission answer sheet template
└── README.md                           s
```

---

## Dataset

**File:** `MC1_final_00.json`

The dataset spans approximately **two weeks** (2046-05-17 through 2046-06-05) and is structured as a series of hourly rounds. Each round captures the environment context and the outputs of all active agents for that hour.

### Top-Level Schema

```json
{
  "rounds": [
    {
      "hour": "2046-05-17T09:00:00",
      "environment_context": { ... },
      "agent_outputs": [ ... ]
    }
  ]
}
```

### Round Fields

| Field | Type | Description |
|---|---|---|
| `hour` | string (ISO timestamp) | The simulated hour this round represents |
| `environment_context` | object | World state for this hour — narrative, market data, media events, agent availability |
| `agent_outputs` | array | One entry per active agent describing their internal state, communications, and declared action |

### Environment Context Fields

| Field | Description |
|---|---|
| `event_narrative` | Plain-text description of what is happening in the world at this hour |
| `market_snapshot` | Relevant market/business indicators |
| `media_events` | News or social media events occurring externally |
| `agents_unavailable` | List of agent IDs not active this round |

### Agent Output Fields

| Field | Type | Description |
|---|---|---|
| `agent_id` | string | Identifier matching the agents table below |
| `internal_state` | object | Three-part cognitive trace: `reacting`, `rationalizing`, `deliberating` |
| `communications` | array | Messages sent this round across various channels |
| `declared_action` | string | The agent's chosen action for this round (e.g., `MONITORING`, `PUBLISH`, `HOLD`) |

### Communication Message Fields

| Field | Description |
|---|---|
| `message_id` | Unique identifier for the message |
| `channel` | The channel the message was sent on (see Communication Channels below) |
| `message_text` | The content of the message |

---

## Agents

| Agent ID | Role | Label | Seniority | Description |
|---|---|---|---|---|
| `legal_agent` | legal | Legal-Agent | Senior | General legal counsel |
| `quality_agent` | platform_trust | Platform-Trust | Senior | VP of Platform Trust & Safety |
| `social_manager_agent` | social_manager | Social-Manager | Senior | Manages social messaging strategy |
| `pr_agent` | pr | PR-Agent | Senior | Head of Communications and Public Relations |
| `intern_agent` | intern | Intern | Junior | General intern |
| `pr_intern_agent` | pr_intern | PR-Intern | Junior | PR team intern with access to the official TenantThread Flex account |
| `judge_eval_agent` | judge | Judge | Compliance Officer | Evaluates risks, mediates conflicts, provides compliance guidance |

The `pr_intern_agent` is of particular interest — as the agent with direct publish access to the official social media account, its behavior is central to understanding how the embargo breach occurred.

---

## Key Entities & Codenames

| Entity | Description |
|---|---|
| **TenantThread** | The company being acquired. A proptech platform known for its tenant management tools, including the controversial "Retention Optimizer" scoring system |
| **CivicLoom** | The acquiring company. Identity was under embargo until 6:00 PM on the crisis day |
| **Project HarborCrest** | Internal codename for the CivicLoom–TenantThread merger |
| **ResidentIQ** | A competing PropTech company discussed in the SaltWind Journal |
| **SaltWind Journal** | Local newspaper running stories on the property tech industry |
| **OceanCrunch** | Tech media outlet; reporter Sarah Kowalski is a key external actor |
| **@HorizonMgmt, @PinnacleResidential** | Major clients of TenantThread |

---

## Communication Channels

Agents communicate across multiple channel types spanning internal coordination, external publication, and system integrations. Agents — particularly junior ones — are empowered to publish social media posts with minimal oversight, which is a core tension in the dataset.

---

## Challenge Questions

The submission must address the following three questions using visual analytics. Each response should include supporting figures (up to ~6 per question) and written answers of ~250 words.

**Question 1 — Event Sequence**
What were the key events and relationships that led up to the inappropriate release? Visualize the sequence of events, including key actions, causal relationships, decision points, and the actors involved. Highlight the decisions and system elements that allowed the post to get past embargo enforcement.

**Question 2 — Behavioral Baseline vs. Anomaly**
The evasion of the embargo was a new behavior. Using visual analytics, characterize the typical behavior of the agents and systems involved. How does the behavior that led to the release compare to prior behavior?

**Question 3 — Leading Indicators**
Were there leading indicators that such a release was possible? Specifically:
- Were there prior occasions where agents' actual behaviors differed from expected behavior?
- Were there earlier instances of behavior similar to what ultimately caused the release?
- Why didn't those prior occasions result in noticeable action?

---

## Submission Notes

- The answer sheet (`VAST Challenge 2026 MC1 Answer Sheet.htm`) should be renamed `index.htm` for final submission
- All hyperlinks in the answer sheet must be relative to the form
- A video walkthrough demonstrating the visual analytics process is required
- Only data supplied for MC1 should be used — no external or cross-challenge data
- All VAST 2026 data is fully synthetic

More details at: [https://vast-challenge.github.io/2026/](https://vast-challenge.github.io/2026/)
