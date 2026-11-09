from dataclasses import dataclass, replace
from datetime import date

from .models import Aspiration

MAX_COLLECTION_SIZE = 4096


def _is_scalar_text(value: object) -> bool:
    """Whether text contains only Unicode scalar values, usable in UTF-8."""
    return isinstance(value, str) and not any(
        "\ud800" <= character <= "\udfff" for character in value
    )


def _calendar_date(value: str) -> date:
    """Parse exactly ASCII YYYY-MM-DD, independent of Python's ISO grammar."""
    if (
        len(value) != 10
        or value[4] != "-"
        or value[7] != "-"
        or any(
            character < "0" or character > "9"
            for index, character in enumerate(value)
            if index not in (4, 7)
        )
    ):
        raise ValueError("expected an ASCII YYYY-MM-DD calendar date")
    return date.fromisoformat(value)


@dataclass(frozen=True)
class ValidationIssue:
    path: str
    message: str


class RegistryValidationError(ValueError):
    def __init__(self, issues: tuple[ValidationIssue, ...]):
        self.issues = issues
        super().__init__(
            "invalid registry: "
            + "; ".join(f"{issue.path}: {issue.message}" for issue in issues)
        )


def validate_registry(aspirations: object) -> tuple[Aspiration, ...]:
    """Normalize finite tuple/list registry data once; reject empty scopes.

    Signal collections must be tuples or lists of unique nonblank scalar text.
    Iterators and arbitrary objects are never executed by validation.
    The returned registry and its signal fields are immutable tuples.
    """
    issues: list[ValidationIssue] = []
    if not isinstance(aspirations, (tuple, list)) or type(aspirations) not in (
        tuple,
        list,
    ):
        raise RegistryValidationError(
            (ValidationIssue("registry", "expected tuple or list"),)
        )
    if not aspirations or len(aspirations) > MAX_COLLECTION_SIZE:
        raise RegistryValidationError(
            (ValidationIssue("registry", "empty or oversized scope"),)
        )
    result: list[Aspiration] = []
    ids: set[str] = set()
    for index, item in enumerate(aspirations):
        path = f"registry[{index}]"
        if type(item) is not Aspiration:
            issues.append(ValidationIssue(path, "expected Aspiration"))
            continue
        for name in ("id", "title", "thread", "horizon"):
            value = getattr(item, name)
            if (
                type(value) is not str
                or not _is_scalar_text(value)
                or not value.strip()
            ):
                issues.append(
                    ValidationIssue(
                        f"{path}.{name}", "expected nonblank Unicode scalar text"
                    )
                )
        if type(item.id) is str:
            if item.id in ids:
                issues.append(ValidationIssue(f"{path}.id", "duplicate identifier"))
            ids.add(item.id)
        signals: dict[str, tuple[str, ...]] = {}
        for name in ("markers", "counter_signals"):
            value = getattr(item, name)
            if (
                type(value) not in (tuple, list)
                or not value
                or len(value) > MAX_COLLECTION_SIZE
                or any(
                    type(token) is not str
                    or not _is_scalar_text(token)
                    or not token.strip()
                    for token in value
                )
            ):
                issues.append(
                    ValidationIssue(
                        f"{path}.{name}",
                        "expected nonempty tuple/list of nonblank Unicode scalar text",
                    )
                )
                continue
            if len(set(value)) != len(value):
                issues.append(ValidationIssue(f"{path}.{name}", "duplicate signal"))
            signals[name] = tuple(value)
        if len(signals) == 2:
            if set(signals["markers"]) & set(signals["counter_signals"]):
                issues.append(ValidationIssue(path, "marker/counter-signal overlap"))
            result.append(
                replace(
                    item,
                    markers=signals["markers"],
                    counter_signals=signals["counter_signals"],
                )
            )
    if issues:
        raise RegistryValidationError(tuple(issues))
    return tuple(result)
