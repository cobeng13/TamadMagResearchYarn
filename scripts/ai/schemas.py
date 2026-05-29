from __future__ import annotations

from typing import Any


SCREENING_LABELS = [
    "highly_relevant",
    "possibly_relevant",
    "background_only",
    "out_of_scope",
    "insufficient_metadata",
]

SCREENING_ACTIONS = [
    "screen_full_text",
    "keep_for_background",
    "exclude_after_human_review",
    "needs_metadata_check",
    "needs_query_followup",
]

EVIDENCE_COLUMNS = [
    "paper_id",
    "citation_key",
    "theme",
    "study_design",
    "population",
    "variables",
    "key_finding",
    "relevance_to_current_study",
    "source_location",
    "confidence_rating",
    "notes",
]

SUMMARY_SECTIONS = [
    "paper_id",
    "full_citation",
    "research_purpose",
    "study_design",
    "population_sample",
    "setting_context",
    "variables",
    "instruments_measures",
    "statistical_methods",
    "key_findings",
    "limitations",
    "relevance_to_current_study",
    "useful_concepts_for_introduction",
    "useful_concepts_for_rrl",
    "useful_concepts_for_discussion",
    "exact_source_location_if_available",
    "confidence_rating",
]

QUERY_PROVIDERS = [
    "openalex",
    "crossref",
    "semantic_scholar",
    "pubmed",
    "europe_pmc",
    "arxiv",
    "core",
    "general",
]

QUERY_EXPECTED_LEVELS = ["high", "medium", "low"]

SYNTHESIS_EVIDENCE_ROLES = [
    "direct_support",
    "indirect_support",
    "background_context",
    "methodological_support",
    "mixed_or_conflicting",
    "weak_or_limited",
    "out_of_scope",
    "to_be_confirmed",
]

SYNTHESIS_STRENGTHS = [
    "strong",
    "moderate",
    "limited",
    "weak",
    "to_be_confirmed",
]

SYNTHESIS_MANUSCRIPT_USES = [
    "introduction",
    "review_of_related_literature",
    "methodology_context",
    "results_context",
    "discussion",
    "limitations",
    "recommendations",
    "background_only",
    "do_not_use",
    "to_be_confirmed",
]

SYNTHESIS_MATRIX_COLUMNS = [
    "synthesis_id",
    "theme",
    "subtheme",
    "citation_key",
    "paper_id",
    "study_design",
    "population",
    "variables",
    "key_finding",
    "evidence_role",
    "relationship_to_current_study",
    "strength_of_evidence",
    "limitations_or_cautions",
    "use_in_manuscript",
    "source_location",
    "confidence_rating",
    "notes",
]

GAP_TYPES = [
    "population_context_gap",
    "local_philippine_gap",
    "methodological_gap",
    "variable_measurement_gap",
    "evidence_consistency_gap",
    "practical_application_gap",
    "literature_availability_gap",
    "to_be_confirmed",
]

GAP_STRENGTHS = [
    "strong",
    "moderate",
    "limited",
    "weak",
    "to_be_confirmed",
]

GAP_CAUTION_LEVELS = [
    "low",
    "moderate",
    "high",
    "to_be_confirmed",
]

GAP_RECOMMENDED_USES = [
    "introduction",
    "review_of_related_literature",
    "problem_statement",
    "significance_of_the_study",
    "methodology_rationale",
    "discussion",
    "limitations",
    "do_not_use",
    "to_be_confirmed",
]

CONTRIBUTION_TYPES = [
    "local_context_contribution",
    "population_specific_contribution",
    "methodological_contribution",
    "variable_measurement_contribution",
    "practical_program_evaluation_contribution",
    "replication_or_validation_contribution",
    "to_be_confirmed",
]

GAP_MATRIX_COLUMNS = [
    "gap_id",
    "gap_type",
    "gap_statement",
    "supporting_synthesis_source",
    "related_theme",
    "evidence_basis",
    "strength_of_gap",
    "relevance_to_current_study",
    "caution_level",
    "recommended_use",
    "notes",
]


def candidate_screening_schema() -> dict[str, Any]:
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "screenings": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "row_index": {"type": "integer"},
                        "candidate_id": {"type": "string"},
                        "ai_relevance_label": {"type": "string", "enum": SCREENING_LABELS},
                        "ai_confidence": {"type": "number", "minimum": 0, "maximum": 1},
                        "ai_reason": {"type": "string"},
                        "ai_suggested_action": {"type": "string", "enum": SCREENING_ACTIONS},
                        "ai_key_terms": {"type": "array", "items": {"type": "string"}},
                        "ai_metadata_warnings": {"type": "string"},
                    },
                    "required": [
                        "row_index",
                        "candidate_id",
                        "ai_relevance_label",
                        "ai_confidence",
                        "ai_reason",
                        "ai_suggested_action",
                        "ai_key_terms",
                        "ai_metadata_warnings",
                    ],
                },
            }
        },
        "required": ["screenings"],
    }


def metadata_check_schema(metadata_columns: list[str]) -> dict[str, Any]:
    field_properties = {column: {"type": "string"} for column in metadata_columns if column != "citation_key"}
    field_properties["row_index"] = {"type": "integer"}
    field_properties["citation_key"] = {"type": "string"}
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "records": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        **field_properties,
                        "ai_metadata_status": {"type": "string", "enum": ["complete", "needs_review"]},
                        "ai_change_summary": {"type": "string"},
                        "ai_evidence_snippets": {"type": "array", "items": {"type": "string"}},
                        "ai_unresolved_fields": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": [
                        "row_index",
                        *metadata_columns,
                        "ai_metadata_status",
                        "ai_change_summary",
                        "ai_evidence_snippets",
                        "ai_unresolved_fields",
                    ],
                },
            }
        },
        "required": ["records"],
    }


def evidence_extraction_schema() -> dict[str, Any]:
    summary_properties = {section: {"type": "string"} for section in SUMMARY_SECTIONS}
    evidence_properties = {column: {"type": "string"} for column in EVIDENCE_COLUMNS}
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "row_index": {"type": "integer"},
            "paper_id": {"type": "string"},
            "citation_key": {"type": "string"},
            "summary": {
                "type": "object",
                "additionalProperties": False,
                "properties": summary_properties,
                "required": SUMMARY_SECTIONS,
            },
            "evidence_rows": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": evidence_properties,
                    "required": EVIDENCE_COLUMNS,
                },
            },
            "extraction_issues": {"type": "array", "items": {"type": "string"}},
        },
        "required": ["row_index", "paper_id", "citation_key", "summary", "evidence_rows", "extraction_issues"],
    }


def query_generation_schema() -> dict[str, Any]:
    query_item = {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "provider": {"type": "string", "enum": QUERY_PROVIDERS},
            "query_text": {"type": "string"},
            "purpose": {"type": "string"},
            "expected_recall": {"type": "string", "enum": QUERY_EXPECTED_LEVELS},
            "expected_precision": {"type": "string", "enum": QUERY_EXPECTED_LEVELS},
            "notes": {"type": "string"},
        },
        "required": ["provider", "query_text", "purpose", "expected_recall", "expected_precision", "notes"],
    }
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "topic_summary": {"type": "string"},
            "core_concepts": {"type": "array", "items": {"type": "string"}},
            "inclusion_boundaries": {"type": "array", "items": {"type": "string"}},
            "exclusion_boundaries": {"type": "array", "items": {"type": "string"}},
            "provider_strategy": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "provider": {"type": "string", "enum": QUERY_PROVIDERS},
                        "recommended_use": {"type": "string"},
                        "notes": {"type": "string"},
                    },
                    "required": ["provider", "recommended_use", "notes"],
                },
            },
            "query_families": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "family_name": {"type": "string"},
                        "purpose": {"type": "string"},
                        "queries": {"type": "array", "items": query_item},
                    },
                    "required": ["family_name", "purpose", "queries"],
                },
            },
            "warnings": {"type": "array", "items": {"type": "string"}},
            "recommended_general_queries": {"type": "array", "items": {"type": "string"}},
            "suggested_next_step": {"type": "string"},
        },
        "required": [
            "topic_summary",
            "core_concepts",
            "inclusion_boundaries",
            "exclusion_boundaries",
            "provider_strategy",
            "query_families",
            "warnings",
            "recommended_general_queries",
            "suggested_next_step",
        ],
    }


def synthesis_schema() -> dict[str, Any]:
    theme_item = {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "theme": {"type": "string"},
            "subthemes": {"type": "array", "items": {"type": "string"}},
            "summary": {"type": "string"},
            "direct_evidence": {"type": "array", "items": {"type": "string"}},
            "indirect_evidence": {"type": "array", "items": {"type": "string"}},
            "mixed_or_conflicting_findings": {"type": "array", "items": {"type": "string"}},
            "methodological_notes": {"type": "array", "items": {"type": "string"}},
            "limitations_or_cautions": {"type": "array", "items": {"type": "string"}},
            "use_in_manuscript": {"type": "array", "items": {"type": "string"}},
        },
        "required": [
            "theme",
            "subthemes",
            "summary",
            "direct_evidence",
            "indirect_evidence",
            "mixed_or_conflicting_findings",
            "methodological_notes",
            "limitations_or_cautions",
            "use_in_manuscript",
        ],
    }


def gap_analysis_schema() -> dict[str, Any]:
    contribution = {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "proposed_contribution_statement": {"type": "string"},
            "contribution_types": {"type": "array", "items": {"type": "string", "enum": CONTRIBUTION_TYPES}},
            "contribution_rationale": {"type": "string"},
            "safe_claims": {"type": "array", "items": {"type": "string"}},
            "claims_to_avoid": {"type": "array", "items": {"type": "string"}},
            "likely_stakeholders": {"type": "array", "items": {"type": "string"}},
            "manuscript_ready_contribution_statement": {"type": "string"},
        },
        "required": [
            "proposed_contribution_statement",
            "contribution_types",
            "contribution_rationale",
            "safe_claims",
            "claims_to_avoid",
            "likely_stakeholders",
            "manuscript_ready_contribution_statement",
        ],
    }
    problem_statement = {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "working_problem_statement": {"type": "string"},
            "research_problem_context": {"type": "string"},
            "evidence_based_rationale": {"type": "string"},
            "local_or_institutional_relevance": {"type": "string"},
            "variables_and_outcome_focus": {"type": "string"},
            "research_questions_alignment": {"type": "string"},
            "final_refined_problem_statement_draft": {"type": "string"},
            "assumptions_and_items_to_confirm": {"type": "array", "items": {"type": "string"}},
        },
        "required": [
            "working_problem_statement",
            "research_problem_context",
            "evidence_based_rationale",
            "local_or_institutional_relevance",
            "variables_and_outcome_focus",
            "research_questions_alignment",
            "final_refined_problem_statement_draft",
            "assumptions_and_items_to_confirm",
        ],
    }
    gap_row = {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "gap_type": {"type": "string", "enum": GAP_TYPES},
            "gap_statement": {"type": "string"},
            "supporting_synthesis_source": {"type": "string"},
            "related_theme": {"type": "string"},
            "evidence_basis": {"type": "string"},
            "strength_of_gap": {"type": "string", "enum": GAP_STRENGTHS},
            "relevance_to_current_study": {"type": "string"},
            "caution_level": {"type": "string", "enum": GAP_CAUTION_LEVELS},
            "recommended_use": {"type": "string", "enum": GAP_RECOMMENDED_USES},
            "notes": {"type": "string"},
        },
        "required": [
            "gap_type",
            "gap_statement",
            "supporting_synthesis_source",
            "related_theme",
            "evidence_basis",
            "strength_of_gap",
            "relevance_to_current_study",
            "caution_level",
            "recommended_use",
            "notes",
        ],
    }
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "completion_status": {"type": "string", "enum": ["completed", "partial", "blocked"]},
            "current_study_focus": {"type": "string"},
            "what_is_known": {"type": "array", "items": {"type": "string"}},
            "what_remains_unknown": {"type": "array", "items": {"type": "string"}},
            "population_or_context_gaps": {"type": "array", "items": {"type": "string"}},
            "local_or_philippine_gaps": {"type": "array", "items": {"type": "string"}},
            "methodological_gaps": {"type": "array", "items": {"type": "string"}},
            "variable_or_measurement_gaps": {"type": "array", "items": {"type": "string"}},
            "evidence_limitations": {"type": "array", "items": {"type": "string"}},
            "direct_vs_indirect_evidence_balance": {"type": "string"},
            "safe_gap_statement": {"type": "string"},
            "gap_claims_requiring_caution": {"type": "array", "items": {"type": "string"}},
            "to_be_confirmed": {"type": "array", "items": {"type": "string"}},
            "contribution": contribution,
            "problem_statement": problem_statement,
            "gap_rows": {"type": "array", "items": gap_row},
            "recommended_next_step": {"type": "string"},
        },
        "required": [
            "completion_status",
            "current_study_focus",
            "what_is_known",
            "what_remains_unknown",
            "population_or_context_gaps",
            "local_or_philippine_gaps",
            "methodological_gaps",
            "variable_or_measurement_gaps",
            "evidence_limitations",
            "direct_vs_indirect_evidence_balance",
            "safe_gap_statement",
            "gap_claims_requiring_caution",
            "to_be_confirmed",
            "contribution",
            "problem_statement",
            "gap_rows",
            "recommended_next_step",
        ],
    }
    synthesis_row = {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "theme": {"type": "string"},
            "subtheme": {"type": "string"},
            "citation_key": {"type": "string"},
            "paper_id": {"type": "string"},
            "study_design": {"type": "string"},
            "population": {"type": "string"},
            "variables": {"type": "string"},
            "key_finding": {"type": "string"},
            "evidence_role": {"type": "string", "enum": SYNTHESIS_EVIDENCE_ROLES},
            "relationship_to_current_study": {"type": "string"},
            "strength_of_evidence": {"type": "string", "enum": SYNTHESIS_STRENGTHS},
            "limitations_or_cautions": {"type": "string"},
            "use_in_manuscript": {"type": "string", "enum": SYNTHESIS_MANUSCRIPT_USES},
            "source_location": {"type": "string"},
            "confidence_rating": {"type": "string"},
            "notes": {"type": "string"},
        },
        "required": [
            "theme",
            "subtheme",
            "citation_key",
            "paper_id",
            "study_design",
            "population",
            "variables",
            "key_finding",
            "evidence_role",
            "relationship_to_current_study",
            "strength_of_evidence",
            "limitations_or_cautions",
            "use_in_manuscript",
            "source_location",
            "confidence_rating",
            "notes",
        ],
    }
    literature_map = {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "current_study_focus": {"type": "string"},
            "evidence_clusters": {"type": "array", "items": {"type": "string"}},
            "directly_relevant_studies": {"type": "array", "items": {"type": "string"}},
            "adjacent_evidence": {"type": "array", "items": {"type": "string"}},
            "methodological_evidence": {"type": "array", "items": {"type": "string"}},
            "gaps_identified": {"type": "array", "items": {"type": "string"}},
            "contradictions_or_mixed_findings": {"type": "array", "items": {"type": "string"}},
            "next_stage_support": {"type": "string"},
        },
        "required": [
            "current_study_focus",
            "evidence_clusters",
            "directly_relevant_studies",
            "adjacent_evidence",
            "methodological_evidence",
            "gaps_identified",
            "contradictions_or_mixed_findings",
            "next_stage_support",
        ],
    }
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "completion_status": {"type": "string", "enum": ["completed", "partial", "blocked"]},
            "themes": {"type": "array", "items": theme_item},
            "synthesis_rows": {"type": "array", "items": synthesis_row},
            "literature_map": literature_map,
            "claims_safe_to_use_later": {"type": "array", "items": {"type": "string"}},
            "claims_requiring_caution": {"type": "array", "items": {"type": "string"}},
            "missing_evidence": {"type": "array", "items": {"type": "string"}},
            "recommended_next_step": {"type": "string"},
        },
        "required": [
            "completion_status",
            "themes",
            "synthesis_rows",
            "literature_map",
            "claims_safe_to_use_later",
            "claims_requiring_caution",
            "missing_evidence",
            "recommended_next_step",
        ],
    }
