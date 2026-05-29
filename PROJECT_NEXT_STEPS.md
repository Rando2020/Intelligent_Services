# Intelligent Services — Where It Stands & What's Next

*Snapshot at end of build session. Pick up here.*

---

## Shipped / done

- **Website** — live via GitHub Pages (cream editorial + aurora accents, RACI/PASCI, role demos, question routing, team-fit, trust banner). Real contact + LinkedIn wired in.
- **README** — rewritten to match the real system (pipeline, product spine, demos, rule packs, roadmap). *Replace the stale public README with this.*
- **YAML rule engine** (`rule_engine.py` + `scoring_rules.yaml`) — externalizes all scoring numbers, gate caps, rating bands, and launch blockers that were hardcoded in `build_scorecard()`. Runs and validates on load.
- **Spec docs drafted** — `AGENT_GOVERNANCE.md` (grounding/anti-hallucination), `CONNECTED_PAGE_STANDARD.md` (living-doc convention), `CONCEPT_NOTES.md` (Atlassian-layer product direction + doc-gate feature).

---

## Two loose threads to close FIRST (already in your hands, quick)

1. **Reconcile dimension weights.** The source scoring table sums to **110, not 100** — the engine caught this. Decide which dimension(s) lose 10 total, update `scoring_rules.yaml`, then flip the engine's weight check from warning back to hard error.
2. **Wire predicates to real `Intake` fields.** The predicate functions in `rule_engine.py` use guessed field names (`legal_use_approved`, `destination_verified`, etc.). Point each at the actual `Intake` dataclass field. ~10 min pass.

---

## Repo: prototype → trustworthy tool

| Priority | Build | Why it matters |
|---:|---|---|
| 1 | Contradiction detector | Highest-value feature. Structured cross-checks: every Gantt task links to an SOP? ticket data-class matches data map? manifest recipient matches allowlist? Catches the "built twice already" waste. |
| 2 | LICENSE file | Public repo with no license = all-rights-reserved by default, which discourages engagement. Pick one (MIT if open, proprietary if commercial). |
| 3 | Test the rule LOGIC | Current tests prove the package builds; they don't prove scoring is correct. Add tests for gate caps, band thresholds, blocker triggering. |
| 4 | Grounding / anti-hallucination layer | Implement `AGENT_GOVERNANCE.md`: validate every citation against the rule pack/input before publish; hold ungrounded output in draft. The difference between "looks governed" and "is trustworthy." |
| 5 | Move remaining hardcoded logic to YAML | Finish what the rule engine started — findings, required reviews, recommended tickets. |

---

## Project: tool → something real

**The most important next step is NOT code. It's validation.**

Put the site + a short walkthrough in front of **3–5 people from the CVS / Innovaccer network** and ask:
> "Would your team pay for this? What would make it a yes?"

This single conversation decides the whole investment path — and it doubles as the outreach that lands contract income.

### Sequencing (don't skip ahead)
```
1. Validate demand  ── ask the network (also = contract leads)
2. Fix correctness  ── weights, predicates, rule-logic tests
3. Contradiction detector  ── the wedge feature
4. Grounding layer  ── makes output trustworthy
5. THEN consider the Atlassian Marketplace app build
```

Building the Marketplace app before validating demand is the classic trap. The network access to avoid it is the unfair advantage.

---

## The honest north star

The repo is an impressive solo build and a genuine credibility asset. Whether it becomes a **product** or stays a **portfolio piece that wins contract work**, both are wins — but which one to invest months in is answered by *talking to buyers*, not by building more features.

The domain expertise (regulated implementation, real lean-team pain) is the moat. The code is the demonstration of it.
