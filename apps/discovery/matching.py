"""
Pluggable Matrimonial Match & Compatibility Scoring Architecture.
Compares a seeker's PartnerPreference against candidate profiles to calculate
a numerical compatibility score and positive matching traits.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class MatchBreakdown:
    score: int
    matched_traits: List[str] = field(default_factory=list)
    unmatched_traits: List[str] = field(default_factory=list)

    @property
    def badge_color(self) -> str:
        """Helper to determine badge display theme."""
        if self.score >= 80:
            return 'gold'
        if self.score >= 60:
            return 'green'
        if self.score >= 40:
            return 'blue'
        return 'gray'


class BaseMatchScorer(ABC):
    """Abstract base class for all match scoring algorithms."""

    @abstractmethod
    def calculate_compatibility(self, searcher_profile, candidate_profile) -> MatchBreakdown:
        pass


class SimplePreferenceScorer(BaseMatchScorer):
    """
    Standard rule-based compatibility engine comparing candidate profile attributes
    against the seeker's PartnerPreference criteria.
    Total weights equal 100 points:
    - Age Range (20 pts)
    - Height Range (10 pts)
    - Religion (20 pts)
    - Mother Tongue (15 pts)
    - Education (15 pts)
    - Country / Location (10 pts)
    - Diet / Lifestyle (10 pts)
    """

    def calculate_compatibility(self, searcher_profile, candidate_profile) -> MatchBreakdown:
        if not searcher_profile:
            return MatchBreakdown(score=50, matched_traits=['Compatible Age'])

        pref = getattr(searcher_profile, 'partner_preference', None)
        if not pref:
            # Fallback when searcher has not set explicit partner preferences
            return self._calculate_heuristic_score(searcher_profile, candidate_profile)

        score = 0
        matched = []
        unmatched = []

        # 1. Age Range (20 pts)
        cand_age = candidate_profile.age
        if cand_age is not None:
            if pref.min_age <= cand_age <= pref.max_age:
                score += 20
                matched.append(f'Age ({cand_age} yrs)')
            else:
                unmatched.append(f'Age ({cand_age} yrs)')
        else:
            score += 10  # neutral

        # 2. Height Range (10 pts)
        cand_height = candidate_profile.height_cm
        if cand_height is not None and (pref.min_height_cm or pref.max_height_cm):
            min_h = pref.min_height_cm or 100
            max_h = pref.max_height_cm or 250
            if min_h <= cand_height <= max_h:
                score += 10
                matched.append('Height matches')
            else:
                unmatched.append('Height outside preference')
        else:
            score += 10  # unspecified is treated as flexible

        # 3. Religion (20 pts)
        if pref.preferred_religion:
            pref_rel = pref.preferred_religion.lower().strip()
            cand_rel = (candidate_profile.religion or '').lower().strip()
            if pref_rel in cand_rel or cand_rel in pref_rel or pref_rel == 'any':
                score += 20
                matched.append(f'Religion ({candidate_profile.religion})')
            else:
                unmatched.append(f'Religion ({candidate_profile.religion})')
        else:
            score += 20

        # 4. Mother Tongue (15 pts)
        if pref.preferred_mother_tongue:
            pref_lang = pref.preferred_mother_tongue.lower().strip()
            cand_lang = (candidate_profile.mother_tongue or '').lower().strip()
            if pref_lang in cand_lang or cand_lang in pref_lang or pref_lang == 'any':
                score += 15
                matched.append(f'Language ({candidate_profile.mother_tongue})')
            else:
                unmatched.append(f'Language ({candidate_profile.mother_tongue})')
        else:
            score += 15

        # 5. Education (15 pts)
        if pref.preferred_education:
            pref_edu = pref.preferred_education.lower().strip()
            cand_edu_val = ''
            cand_edu_disp = ''
            if hasattr(candidate_profile, 'education') and candidate_profile.education:
                cand_edu_val = (candidate_profile.education.highest_education or '').lower()
                cand_edu_disp = (candidate_profile.education.get_highest_education_display() or '').lower()
            if (
                pref_edu == 'any'
                or pref_edu in cand_edu_val
                or cand_edu_val in pref_edu
                or pref_edu in cand_edu_disp
                or cand_edu_disp in pref_edu
                or 'master' in pref_edu and 'master' in cand_edu_disp
                or 'bachelor' in pref_edu and 'bachelor' in cand_edu_disp
                or 'doctor' in pref_edu and 'doctor' in cand_edu_disp
            ):
                score += 15
                matched.append('Education matches')
            else:
                unmatched.append('Education')
        else:
            score += 15

        # 6. Country / Location (10 pts)
        if pref.preferred_country:
            pref_country = pref.preferred_country.lower().strip()
            cand_country = (candidate_profile.country or '').lower().strip()
            if pref_country in cand_country or cand_country in pref_country or pref_country == 'any':
                score += 10
                matched.append(f'Country ({candidate_profile.country})')
            else:
                unmatched.append(f'Country ({candidate_profile.country})')
        else:
            score += 10

        # 7. Diet / Lifestyle (10 pts)
        if pref.preferred_diet:
            pref_diet = pref.preferred_diet.lower().strip()
            cand_diet = ''
            if hasattr(candidate_profile, 'lifestyle') and candidate_profile.lifestyle:
                cand_diet = (candidate_profile.lifestyle.get_diet_display() or '').lower()
            if pref_diet in cand_diet or cand_diet in pref_diet or pref_diet == 'any':
                score += 10
                matched.append('Diet matches')
            else:
                unmatched.append('Diet')
        else:
            score += 10

        total_score = max(0, min(100, score))
        return MatchBreakdown(
            score=total_score,
            matched_traits=matched,
            unmatched_traits=unmatched,
        )

    def _calculate_heuristic_score(self, searcher_profile, candidate_profile) -> MatchBreakdown:
        """Heuristic score based on mutual similarities when searcher has no explicit PartnerPreference."""
        score = 50
        matched = []

        if searcher_profile.religion and searcher_profile.religion == candidate_profile.religion:
            score += 20
            matched.append(f'Same Religion ({candidate_profile.religion})')

        if searcher_profile.mother_tongue and searcher_profile.mother_tongue == candidate_profile.mother_tongue:
            score += 15
            matched.append(f'Same Language ({candidate_profile.mother_tongue})')

        if searcher_profile.country and searcher_profile.country == candidate_profile.country:
            score += 15
            matched.append(f'Same Country ({candidate_profile.country})')

        return MatchBreakdown(
            score=min(100, score),
            matched_traits=matched or ['Compatible Member'],
        )


def score_profile_candidates(searcher_profile, candidates, scorer: Optional[BaseMatchScorer] = None):
    """
    Attach `.match_breakdown` to each candidate profile and return sorted by match score.
    """
    if scorer is None:
        scorer = SimplePreferenceScorer()

    scored_list = []
    for cand in candidates:
        cand.match_breakdown = scorer.calculate_compatibility(searcher_profile, cand)
        scored_list.append(cand)

    scored_list.sort(key=lambda p: p.match_breakdown.score, reverse=True)
    return scored_list
