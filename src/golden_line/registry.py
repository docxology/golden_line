"""The versioned Golden Line aspiration registry.

The founding four aspirations (attention, usefulness, repair, flourishing)
are extended by five further entries that fill out the long-horizon picture:
durable understanding, teachable craft, honest uncertainty, unhurried
questions, and returning improvements to the commons. Every entry pairs a
horizon with observable markers and counter-signals so that direction can be
discussed rather than merely admired.
"""

from __future__ import annotations

from .models import Aspiration


GOLDEN_ASPIRATIONS: tuple[Aspiration, ...] = (
    Aspiration(
        "attention-before-output",
        "Let attention precede production",
        "Make enough room to see what the work is actually doing.",
        "next decision",
        ("question revisited", "context named"),
        ("automatic output without review",),
    ),
    Aspiration(
        "useful-to-others",
        "Make work useful beyond its author",
        "Leave knowledge, tools, and explanations that another person can carry.",
        "collaborator or public reader",
        ("handoff used", "reader question answered"),
        ("private cleverness without transfer",),
    ),
    Aspiration(
        "repairable-systems",
        "Prefer systems that can be repaired",
        "Build practices that expose failure early and make correction ordinary.",
        "revision cycle",
        ("failure named", "revision attempted"),
        ("defect hidden to preserve appearance",),
    ),
    Aspiration(
        "wide-human-flourishing",
        "Keep technical work answerable to human flourishing",
        "Treat capability as a means whose value depends on the lives around it.",
        "long horizon",
        ("affected people considered", "tradeoff written"),
        ("capability treated as its own justification",),
    ),
    Aspiration(
        "durable-understanding",
        "Prefer understanding that outlasts the tool",
        "Invest in explanations and models that stay useful after the current stack is gone.",
        "tool turnover",
        ("idea restated without the tool", "method survives migration"),
        ("knowledge locked to a vendor surface",),
    ),
    Aspiration(
        "teachable-craft",
        "Work so the craft can be taught",
        "Shape practice into steps someone earlier on the path can actually follow.",
        "next learner",
        ("step written for a learner", "novice completes the path"),
        ("skill kept tacit to stay indispensable",),
    ),
    Aspiration(
        "honest-uncertainty",
        "Keep uncertainty visible in finished work",
        "Publish what is unknown next to what is claimed, at the same prominence.",
        "public claim",
        ("limit stated beside claim", "confidence qualified in print"),
        ("doubt edited out for polish",),
    ),
    Aspiration(
        "unhurried-questions",
        "Hold at least one unhurried question",
        "Protect a line of inquiry that is measured in years, not sprints.",
        "multi-year inquiry",
        ("question revisited across seasons", "notes accumulate without deadline"),
        ("every question forced to a deliverable",),
    ),
    Aspiration(
        "commons-returned",
        "Return improvements to the commons",
        "Send fixes, data, and methods back to the shared pools they came from.",
        "shared pool",
        ("improvement contributed upstream", "material released for reuse"),
        ("shared work absorbed without return",),
    ),
)


#: The founding four, named by identifier rather than by registry position.
#: Membership is a property of the aspiration, not of where it happens to sit
#: in the tuple, so reordering or extending the registry cannot silently move
#: an entry between the founding group and the further entries.
FOUNDING_IDS: frozenset[str] = frozenset(
    {
        "attention-before-output",
        "useful-to-others",
        "repairable-systems",
        "wide-human-flourishing",
    }
)


def founding_aspirations(
    aspirations: tuple[Aspiration, ...] = GOLDEN_ASPIRATIONS,
) -> tuple[Aspiration, ...]:
    """Return the founding entries of ``aspirations``, in registry order."""
    return tuple(item for item in aspirations if item.id in FOUNDING_IDS)


def further_aspirations(
    aspirations: tuple[Aspiration, ...] = GOLDEN_ASPIRATIONS,
) -> tuple[Aspiration, ...]:
    """Return the non-founding entries of ``aspirations``, in registry order."""
    return tuple(item for item in aspirations if item.id not in FOUNDING_IDS)


def aspiration_ids() -> tuple[str, ...]:
    return tuple(item.id for item in GOLDEN_ASPIRATIONS)


def find_aspiration(
    aspiration_id: str,
    aspirations: tuple[Aspiration, ...] = GOLDEN_ASPIRATIONS,
) -> Aspiration | None:
    """Return the aspiration with ``aspiration_id``, or ``None`` if absent."""
    for item in aspirations:
        if item.id == aspiration_id:
            return item
    return None
