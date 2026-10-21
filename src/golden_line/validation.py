from dataclasses import dataclass, replace

from .models import Aspiration

MAX_COLLECTION_SIZE = 4096


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

    Signal collections must be tuples or lists of unique nonblank strings.
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
            if type(value) is not str or not value.strip():
                issues.append(
                    ValidationIssue(f"{path}.{name}", "expected nonblank text")
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
                or any(type(token) is not str or not token.strip() for token in value)
            ):
                issues.append(
                    ValidationIssue(
                        f"{path}.{name}",
                        "expected nonempty tuple/list of nonblank text",
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
