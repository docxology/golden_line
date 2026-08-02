# The Golden Line aspirations {#sec:aspirations}

The registry opens with four founding aspirations. They are broad enough to
travel across research and engineering, but each is paired with a concrete
horizon so that it can be tested against a record rather than merely admired.

1. **Let attention precede production.** Make enough room to see what the work
   is actually doing at the next decision. *Horizon:* the next decision.
   *Counter-signal:* automatic output without review.
2. **Make work useful beyond its author.** Leave knowledge, tools, and
   explanations that another person can carry to a collaborator or public
   reader. *Horizon:* a collaborator or public reader. *Counter-signal:* private
   cleverness without transfer.
3. **Prefer systems that can be repaired.** Expose failure early and make
   correction ordinary in the revision cycle. *Horizon:* the revision cycle.
   *Counter-signal:* a defect hidden to preserve appearance.
4. **Keep technical work answerable to human flourishing.** Treat capability as
   a means whose value depends on the lives around it over a long horizon.
   *Horizon:* the long horizon. *Counter-signal:* capability treated as its own
   justification.

Five further entries extend the founding four in the versioned registry, filling
out the long-horizon picture: **durable understanding** that outlasts the tool,
**teachable craft** that can be handed to the next learner, **honest
uncertainty** kept visible at the same prominence as the claim, at least one
**unhurried question** measured in years rather than sprints, and improvements
**returned to the commons** they came from. Each follows the same shape: a
horizon, observable markers, and counter-signals ([@def:aspiration]), with the
same reading rule ([@def:decision_rule]).
Together the nine entries and their signal structure are laid out in
[@fig:aspiration_registry_map].

The order is not a ranking. The aspirations can conflict: usefulness beyond the
author can pull against protecting an unhurried question; returning everything to
the commons can pull against an obligation to a specific collaborator, and an
honest record may need to show that conflict rather than resolve it. The
companion White Line is the proper place to record what the registry cannot see
or what should not be claimed.

The founding four are best read as a loop of correction, drawn in
[@fig:golden_horizon_thread]. Attention protects perception before output;
usefulness tests whether what was learned can travel; repair keeps failure from
becoming identity; answerability to human flourishing asks what the capability
is for. No point is a maturity level. A project can move around this loop, lose
one of its conditions, or find that two aspirations pull against each other. The
useful question is therefore not *How high are we?* but *What does this record
make visible, and what remains unasked?*

![The four founding aspirations held in a revisable loop. Titles, horizons, and marker/counter-signal counts are source-derived; the connecting loop and icons are interpretive. The loop is direction, not a score or ranking.](../output/figures/golden_horizon_thread.png){#fig:golden_horizon_thread width=95%}

![The full nine-entry aspiration registry: four founding aspirations and five further entries, drawn from the versioned source. Each row shows its horizon and declared marker/counter-signal counts; the layout is a taxonomy for review, not a performance scale.](../output/figures/aspiration_registry_map.png){#fig:aspiration_registry_map width=95%}

## The signal vocabulary in aggregate

Read as a whole, the registry declares a deliberately small vocabulary: 18
markers and 9 counter-signals across the nine aspirations — two markers and one
counter-signal per entry, with all 18 marker tokens and all 9 counter-signal
tokens distinct across the registry. The `signal_inventory` helper in the
analysis layer derives these counts from the live source, and
[@fig:signal_inventory] draws them one block per declared token. The
distinctness matters: because no token is shared between aspirations, an
observed marker can never accidentally support two directions at once. The
blocks are vocabulary the evaluator can match, never observations and never
points.

![The aggregate declared-signal vocabulary of the registry, one unit block per token: filled blocks for markers, outlined blocks for counter-signals. The counts describe what the evaluator can match, never fulfilment or performance.](../output/figures/signal_inventory.png){#fig:signal_inventory width=95%}

## The reach of the nine horizons

The nine horizon phrases can also be grouped by *when* their direction becomes
visible. The analysis layer declares four interpretive temporal-reach bands —
immediate (1 aspiration, at the next decision), recurring cycle (2, at revision
or tool turnover), at handoff (4, when the work reaches another person), and
open-ended (2, over years) — and `horizon_distribution` places every registry
entry into exactly one band, refusing loudly if a future registry adds a
horizon the map does not classify. [@fig:horizon_bands] shows the grouping.
The bands are a reading aid declared outside the registry contract: band order
widens reach, and a wider horizon is not a higher rank.

![The nine aspiration horizons grouped into four temporal-reach bands — immediate, recurring cycle, at handoff, and open-ended. An interpretive reading aid, not a maturity ladder and not part of the registry contract.](../output/figures/horizon_bands.png){#fig:horizon_bands width=95%}

The aspirations are exercised in [the worked examples](#sec:examples) and
[the batch reading](#sec:batch-reading).
