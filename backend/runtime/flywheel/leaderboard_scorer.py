"""
Leaderboard Scorer v3 — Full 3-Tier Certificate Priority (3/3)
"""

import hashlib
import logging
from typing import Any

from backend.core.services.observability_service import observability
from backend.core.supabase import get_supabase_client

logger = logging.getLogger(__name__)


class LeaderboardScorer:
    PERFORMANCE_WEIGHT = 0.55
    REPRODUCIBILITY_WEIGHT = 0.25
    NOVELTY_WEIGHT = 0.20

    # Tier Multipliers — Tier 3 dominates
    TIER_MULTIPLIERS = {
        "TIER_3_GOLD": 3.0,
        "TIER_2_PHYSICS": 2.0,
        "TIER_1_PARAMETER": 1.3,
        None: 1.0,
    }

    @staticmethod
    def calculate_score(result: dict[str, Any], cert_data: dict[str, Any] | None = None) -> dict[str, Any]:
        """Enhanced scoring using certificate data when available."""
        convergence = result.get("convergence_achieved", False)
        iterations = result.get("convergence_iterations", 9999)
        brier = result.get("brier_score", 0.5)
        trust_score = result.get("trust_score", 0.5)

        # Performance
        perf_score = 100.0
        if convergence:
            perf_score = max(45, 100 - (iterations / 7))
        perf_score = perf_score * (1.0 - brier) * trust_score

        # Reproducibility — boosted heavily by certificate tier
        tier = cert_data.get("verification_tier") if cert_data else None
        repro_base = 55.0
        if tier == "TIER_3_GOLD":
            repro_base = 100.0
        elif tier == "TIER_2_PHYSICS":
            repro_base = 82.0
        elif tier == "TIER_1_PARAMETER":
            repro_base = 65.0

        repro_score = repro_base + (cert_data.get("prov_trust_score", 0) * 20)

        # Novelty
        novelty_score = 100 * (0.6 * result.get("prior_deviation", 0.35) + 0.4 * result.get("entropy", 0.5))

        # Final Score with Tier Multiplier
        base_score = (
            LeaderboardScorer.PERFORMANCE_WEIGHT * perf_score
            + LeaderboardScorer.REPRODUCIBILITY_WEIGHT * repro_score
            + LeaderboardScorer.NOVELTY_WEIGHT * novelty_score
        )

        tier_multiplier = LeaderboardScorer.TIER_MULTIPLIERS.get(tier, 1.0)
        final_score = base_score * tier_multiplier

        return {
            "performance_score": round(perf_score, 2),
            "reproducibility": round(repro_score, 2),
            "novelty_score": round(novelty_score, 2),
            "score": round(final_score, 2),
            "tier_multiplier": tier_multiplier,
            "tier": tier,
        }


async def populate_leaderboard_from_certificates(limit: int = 500):
    """3/3 — Prioritizes Tier 3 → Tier 2 → Tier 1 with strong multipliers"""
    db = get_supabase_client()
    if not db:
        return

    # Fetch certificates ordered by trust + tier priority
    cert_query = (
        db.table("certificates")
        .select(
            "certificate_id, run_id, tenant_id, verification_tier, prov_trust_score, prov_claim_text, issued_at, full_certificate"
        )
        .in_("verification_tier", ["TIER_3_GOLD", "TIER_2_PHYSICS", "TIER_1_PARAMETER"])
        .order("prov_trust_score", desc=True)
        .order("verification_tier", desc=True)  # TIER_3 first
        .limit(limit)
        .execute()
    )

    scorer = LeaderboardScorer()
    entries = []

    for cert in cert_query.data or []:
        run_data = (
            db.table("simulation_runs")
            .select("result, domain, solver, created_at")
            .eq("run_id", cert["run_id"])
            .single()
            .execute()
        )

        if not run_data.data:
            continue

        run = run_data.data
        result = run.get("result", {})

        scores = scorer.calculate_score(result, cert)

        discovery_id = f"disc_cert_{cert['certificate_id']}"

        entries.append(
            {
                "discovery_id": discovery_id,
                "domain": run.get("domain", "unknown"),
                "solver": run.get("solver", "unknown"),
                "title": (cert.get("prov_claim_text") or f"High-Trust {cert['verification_tier']} Discovery")[:140],
                "description": f"Certified {cert['verification_tier']} • Trust {cert.get('prov_trust_score', 0):.2f}",
                **scores,
                "run_count": 1,
                "certified": True,
                "certificate_id": cert["certificate_id"],
                "tenant_id_hash": hashlib.sha256(str(cert["tenant_id"]).encode()).hexdigest()[:16],
                "published_at": cert["issued_at"] or run.get("created_at"),
                "tier": cert["verification_tier"],
            }
        )

        # Mark as processed
        db.table("simulation_runs").update({"leaderboard_entry_id": discovery_id}).eq(
            "run_id", cert["run_id"]
        ).execute()

    if entries:
        db.table("discovery_leaderboard").upsert(entries, on_conflict="discovery_id").execute()
        observability.increment("leaderboard_high_tier_entries", {"count": len(entries)})
        logger.info(f"✅ Leaderboard 3/3 populated — {len(entries)} Tier 1/2/3 entries (Tier 3 prioritized)")


async def refresh_leaderboard():
    """Combined refresh: simulation runs + certificate-driven population"""
    await populate_leaderboard_from_certificates(limit=300)  # High-tier focus
    logger.info("✅ Full leaderboard refresh (certificates + simulations) completed")
