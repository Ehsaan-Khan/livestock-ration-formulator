"""Basic livestock ration evaluator.

Educational decision-support tool by Dr. Ehsaan Ullah Khan.
All nutrient concentrations are entered on a dry-matter basis except DM and
price. Requirements and feed values must be replaced with locally appropriate,
laboratory-supported values before professional use.
"""

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class FeedItem:
    name: str
    as_fed_kg: float
    dm_percent: float
    cp_percent_dm: float
    me_mj_per_kg_dm: float
    ndf_percent_dm: float
    adf_percent_dm: float
    price_per_kg_as_fed: float


@dataclass(frozen=True)
class Targets:
    dmi_kg: float
    cp_kg: float
    me_mj: float
    ndf_min_percent_dm: float
    ndf_max_percent_dm: float
    adf_min_percent_dm: float
    adf_max_percent_dm: float


def contribution(feed: FeedItem) -> dict[str, float]:
    """Calculate daily nutrient and cost contribution of one feed."""
    dm_kg = feed.as_fed_kg * feed.dm_percent / 100
    return {
        "dm_kg": dm_kg,
        "cp_kg": dm_kg * feed.cp_percent_dm / 100,
        "me_mj": dm_kg * feed.me_mj_per_kg_dm,
        "ndf_kg": dm_kg * feed.ndf_percent_dm / 100,
        "adf_kg": dm_kg * feed.adf_percent_dm / 100,
        "cost": feed.as_fed_kg * feed.price_per_kg_as_fed,
    }


def evaluate_ration(feeds: Iterable[FeedItem]) -> dict[str, float]:
    """Aggregate all feed contributions into ration totals."""
    totals = {key: 0.0 for key in ("as_fed_kg", "dm_kg", "cp_kg", "me_mj", "ndf_kg", "adf_kg", "cost")}
    for feed in feeds:
        values = contribution(feed)
        totals["as_fed_kg"] += feed.as_fed_kg
        for key, value in values.items():
            totals[key] += value

    dm = totals["dm_kg"]
    totals["cp_percent_dm"] = totals["cp_kg"] / dm * 100 if dm else 0.0
    totals["ndf_percent_dm"] = totals["ndf_kg"] / dm * 100 if dm else 0.0
    totals["adf_percent_dm"] = totals["adf_kg"] / dm * 100 if dm else 0.0
    totals["cost_per_kg_dm"] = totals["cost"] / dm if dm else 0.0
    return totals


def status(actual: float, target: float, tolerance: float = 0.05) -> str:
    """Classify actual supply relative to a target using a ±5% default band."""
    if actual < target * (1 - tolerance):
        return "Below target"
    if actual > target * (1 + tolerance):
        return "Above target"
    return "Within target range"


def range_status(actual: float, minimum: float, maximum: float) -> str:
    if actual < minimum:
        return "Below range"
    if actual > maximum:
        return "Above range"
    return "Within range"


def print_report(feeds: list[FeedItem], targets: Targets) -> None:
    totals = evaluate_ration(feeds)

    print("\nLIVESTOCK RATION EVALUATION")
    print("=" * 76)
    print(f"{'Feed':<22}{'As-fed kg':>11}{'DM kg':>10}{'CP kg':>10}{'ME MJ':>10}{'Cost':>13}")
    print("-" * 76)
    for feed in feeds:
        values = contribution(feed)
        print(
            f"{feed.name:<22}{feed.as_fed_kg:>11.2f}{values['dm_kg']:>10.2f}"
            f"{values['cp_kg']:>10.2f}{values['me_mj']:>10.1f}{values['cost']:>13.2f}"
        )
    print("-" * 76)
    print(
        f"{'TOTAL':<22}{totals['as_fed_kg']:>11.2f}{totals['dm_kg']:>10.2f}"
        f"{totals['cp_kg']:>10.2f}{totals['me_mj']:>10.1f}{totals['cost']:>13.2f}"
    )

    print("\nRATION SUMMARY")
    print(f"Dry matter intake:       {totals['dm_kg']:.2f} kg — {status(totals['dm_kg'], targets.dmi_kg)}")
    print(f"Crude protein supply:    {totals['cp_kg']:.2f} kg ({totals['cp_percent_dm']:.1f}% DM) — {status(totals['cp_kg'], targets.cp_kg)}")
    print(f"Metabolizable energy:    {totals['me_mj']:.1f} MJ — {status(totals['me_mj'], targets.me_mj)}")
    print(
        f"NDF concentration:       {totals['ndf_percent_dm']:.1f}% DM — "
        f"{range_status(totals['ndf_percent_dm'], targets.ndf_min_percent_dm, targets.ndf_max_percent_dm)}"
    )
    print(
        f"ADF concentration:       {totals['adf_percent_dm']:.1f}% DM — "
        f"{range_status(totals['adf_percent_dm'], targets.adf_min_percent_dm, targets.adf_max_percent_dm)}"
    )
    print(f"Daily feed cost:         {totals['cost']:.2f}")
    print(f"Feed cost per kg DM:     {totals['cost_per_kg_dm']:.2f}")

    print("\nIMPORTANT")
    print("Demo values are illustrative. Replace feed composition, prices and targets")
    print("with verified farm-specific inputs before using the output for decisions.")


def demo_data() -> tuple[list[FeedItem], Targets]:
    """Return an editable demonstration ration and illustrative targets."""
    feeds = [
        FeedItem("Maize silage", 30.0, 32.0, 8.0, 10.5, 46.0, 28.0, 20.0),
        FeedItem("Concentrate", 10.0, 88.0, 20.0, 12.5, 25.0, 12.0, 100.0),
        FeedItem("Wheat straw", 3.0, 90.0, 4.0, 6.0, 78.0, 50.0, 35.0),
    ]
    targets = Targets(
        dmi_kg=21.0,
        cp_kg=3.2,
        me_mj=220.0,
        ndf_min_percent_dm=28.0,
        ndf_max_percent_dm=36.0,
        adf_min_percent_dm=18.0,
        adf_max_percent_dm=25.0,
    )
    return feeds, targets


if __name__ == "__main__":
    demo_feeds, demo_targets = demo_data()
    print_report(demo_feeds, demo_targets)
