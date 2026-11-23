# Experimental result tables

These tables contain selected numerical outcomes reported in the manuscript, not SEEG recordings or clinical source data. Values are preserved from the existing analysis exports; this release does not refit models or add experiments. The original figures and local research records are unchanged.

## Files and coverage

| File | Rows | Contents |
|---|---:|---|
| `results/seeg_paired_orders.csv` | 328 | Receivers with evaluable low- and high-synchrony states, their selected orders and support indicators |
| `results/seeg_candidate_curves.csv` | 32 | Four illustrative receivers, two synchrony states and four candidate orders; normalized risks and response benefits |
| `results/seeg_order_summary.csv` | 4 | Counts across 674 evaluable receiver-state combinations, grouped by selected order |
| `results/seeg_paired_summary.csv` | 16 | The 4-by-4 selected-order table for the 328 paired receivers |
| `results/seeg_participant_summary.csv` | 14 | Evaluable-state and support counts grouped by participant pseudonym |

The paired table covers 656 receiver-state combinations. A further 18 have only one evaluable state and contribute to the 674-state summaries but not to paired comparisons. Among 692 possible combinations, 18 lack test coverage. The candidate curves are illustrative cases, not a random sample or evidence of population-wide performance. These files do not constitute a complete export of every fitted candidate or analysis intermediate.

## Labels and variables

- `participant_code`: P followed by two digits; a study pseudonym with no supplied real-identity mapping.
- `record_code`: S followed by two digits; a study record pseudonym, not a hospital or clinical record identifier.
- `receiver_index`: one-based numerical receiver index within a record, without channel names, anatomy, or electrode coordinates.
- `state`: `low` or `high` synchrony, following the manuscript's fixed state definition.
- `q`, `selected_q`, `low_q`, `high_q`: candidate node order, from 1 to 4. `selected` marks the chosen candidate in each illustrative curve.
- `risk_over_C`: estimated coupling approximation risk divided by the fixed training reference scale C. The compression threshold is 0.05; it is not a trajectory-error guarantee.
- `benefit_pct`: response improvement over the own-history comparator, expressed as a percentage of the full model's improvement. Values can be negative or exceed 100.
- `compression`, `task`, `joint`: counts satisfying the compression criterion, the response task criterion, or both. A task pass retains at least 90% of the full coupling's improvement, subject to the manuscript's qualification rules.
- `low_joint`, `high_joint`, `both_joint`: joint-support indicators for the low state, high state, or both. `different_q` indicates unequal selected orders; `joint_different` additionally requires both states to be supported.
- `bootstrap_joint_difference_fraction`: fraction of fixed-model block resamples supporting the paired order difference; this is not a probability of a biological mechanism or an independent replication.
- `n`: number of evaluable receiver-state combinations. `record_count`: number of study records contributing within a participant group.
- `reduced_joint`, `retained_joint`: jointly supported counts at orders 1-3 and order 4. `other` comprises the remaining evaluable combinations.
- `compression_only`: compression passes without a task pass. `compression_fail`: compression failures. `total` and `both_joint` in the paired summary are receiver counts.

The summaries reconcile to 606 compression passes, 244 task passes and 223 joint passes. Of the joint passes, 90 use orders 1-3 and 133 retain order 4. There are 22 jointly supported order differences among the 328 paired receivers. Counts are descriptive; receivers, states and resamples are not independent patients.

## Privacy boundaries

Only experimental outcome fields are released. Signal samples, absolute error components, test-sample counts, clinical characteristics, dates, real identities, identity lookup tables, electrode locations and fitted model parameters are omitted. P/S labels preserve the grouping needed to interpret experimental results but do not by themselves establish anonymity. See [the publication policy](../PRIVACY.md).
