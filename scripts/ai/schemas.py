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

PROJECT_CONTEXT_CHANGE_TYPES = [
    "framing_update",
    "research_question_update",
    "scope_update",
    "terminology_update",
    "claim_safety_update",
    "downstream_instruction_update",
    "to_be_confirmed",
]

PROJECT_CONTEXT_CAUTION_LEVELS = [
    "low",
    "moderate",
    "high",
    "to_be_confirmed",
]

PROJECT_CONTEXT_CHANGE_COLUMNS = [
    "change_id",
    "file_target",
    "change_type",
    "original_point",
    "refined_point",
    "rationale",
    "evidence_source",
    "caution_level",
    "human_review_needed",
    "notes",
]

OUTLINE_READINESS_STATUSES = [
    "ready",
    "partial",
    "blocked",
    "to_be_confirmed",
]

MANUSCRIPT_SECTIONS = [
    "introduction",
    "review_of_related_literature",
    "methodology",
    "results",
    "discussion",
    "conclusion_recommendations",
    "references",
    "appendices",
]

OUTLINE_MAP_COLUMNS = [
    "outline_id",
    "manuscript_section",
    "subsection",
    "purpose",
    "source_basis",
    "suggested_citation_keys",
    "required_inputs",
    "readiness_status",
    "caution_notes",
]

RESULT_AVAILABLE_VALUES = [
    "yes",
    "partial",
    "no",
    "to_be_confirmed",
]

SIGNIFICANCE_STATUSES = [
    "significant",
    "not_significant",
    "mixed",
    "not_tested",
    "not_reported",
    "to_be_confirmed",
]

RESULT_READINESS_VALUES = [
    "ready_for_results_draft",
    "partial",
    "blocked",
    "to_be_confirmed",
]

FINDING_TYPES = [
    "descriptive",
    "correlation",
    "group_comparison",
    "regression",
    "classification",
    "prediction_model",
    "diagnostic_accuracy",
    "other",
    "to_be_confirmed",
]

RESULT_WRITING_USES = [
    "results",
    "discussion",
    "table",
    "figure",
    "limitation",
    "do_not_use",
    "to_be_confirmed",
]

CAUTION_LEVELS = [
    "low",
    "moderate",
    "high",
    "to_be_confirmed",
]

RESULTS_BY_OBJECTIVE_COLUMNS = [
    "objective_id",
    "objective_text",
    "result_available",
    "source_file",
    "statistical_test_or_model",
    "key_numerical_result",
    "p_value_or_ci",
    "significance_status",
    "direction_or_relationship",
    "result_readiness",
    "missing_items",
    "notes",
]

STATISTICAL_FINDINGS_COLUMNS = [
    "finding_id",
    "objective_id",
    "source_file",
    "finding_type",
    "variable_or_predictor",
    "outcome",
    "statistical_method",
    "reported_value",
    "p_value",
    "confidence_interval",
    "interpretation",
    "writing_use",
    "caution_level",
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


def project_context_update_schema() -> dict[str, Any]:
    string_array = {"type": "array", "items": {"type": "string"}}
    refined_research_questions = {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "original_research_questions": string_array,
            "refinement_notes": string_array,
            "main_research_question": {"type": "string"},
            "specific_research_questions": string_array,
            "questions_to_remove_merge_or_reword": string_array,
            "rationale_for_changes": string_array,
            "to_be_confirmed": string_array,
        },
        "required": [
            "original_research_questions",
            "refinement_notes",
            "main_research_question",
            "specific_research_questions",
            "questions_to_remove_merge_or_reword",
            "rationale_for_changes",
            "to_be_confirmed",
        ],
    }
    refined_writing_scope = {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "manuscript_positioning": {"type": "string"},
            "included_scope": string_array,
            "excluded_scope": string_array,
            "evidence_boundaries": string_array,
            "literature_use_rules": string_array,
            "local_context_framing": {"type": "string"},
            "terminology_preferences": string_array,
            "claims_allowed": string_array,
            "claims_not_allowed": string_array,
            "to_be_confirmed": string_array,
        },
        "required": [
            "manuscript_positioning",
            "included_scope",
            "excluded_scope",
            "evidence_boundaries",
            "literature_use_rules",
            "local_context_framing",
            "terminology_preferences",
            "claims_allowed",
            "claims_not_allowed",
            "to_be_confirmed",
        ],
    }
    refined_agent_instructions = {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "general_rules": string_array,
            "stage_08_outline_instructions": string_array,
            "stage_09_writer_instructions": string_array,
            "results_and_discussion_instructions": string_array,
            "citation_and_claim_safety_rules": string_array,
            "gap_informed_positioning_rules": string_array,
            "to_be_confirmed": string_array,
        },
        "required": [
            "general_rules",
            "stage_08_outline_instructions",
            "stage_09_writer_instructions",
            "results_and_discussion_instructions",
            "citation_and_claim_safety_rules",
            "gap_informed_positioning_rules",
            "to_be_confirmed",
        ],
    }
    outline_context = {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "refined_paper_positioning": {"type": "string"},
            "defensible_gap": {"type": "string"},
            "refined_research_questions": string_array,
            "recommended_argument_flow": string_array,
            "sections_needing_caution": string_array,
            "required_inputs_before_final_outline": string_array,
        },
        "required": [
            "refined_paper_positioning",
            "defensible_gap",
            "refined_research_questions",
            "recommended_argument_flow",
            "sections_needing_caution",
            "required_inputs_before_final_outline",
        ],
    }
    writer_context = {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "core_framing": {"type": "string"},
            "safe_claims": string_array,
            "claims_to_avoid": string_array,
            "citation_use_rules": string_array,
            "evidence_hierarchy": string_array,
            "preferred_terms": string_array,
            "gap_and_contribution_language": string_array,
            "to_be_confirmed": string_array,
        },
        "required": [
            "core_framing",
            "safe_claims",
            "claims_to_avoid",
            "citation_use_rules",
            "evidence_hierarchy",
            "preferred_terms",
            "gap_and_contribution_language",
            "to_be_confirmed",
        ],
    }
    change_row = {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "file_target": {"type": "string"},
            "change_type": {"type": "string", "enum": PROJECT_CONTEXT_CHANGE_TYPES},
            "original_point": {"type": "string"},
            "refined_point": {"type": "string"},
            "rationale": {"type": "string"},
            "evidence_source": {"type": "string"},
            "caution_level": {"type": "string", "enum": PROJECT_CONTEXT_CAUTION_LEVELS},
            "human_review_needed": {"type": "string", "enum": ["yes", "no"]},
            "notes": {"type": "string"},
        },
        "required": [
            "file_target",
            "change_type",
            "original_point",
            "refined_point",
            "rationale",
            "evidence_source",
            "caution_level",
            "human_review_needed",
            "notes",
        ],
    }
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "completion_status": {"type": "string", "enum": ["completed", "partial", "blocked"]},
            "original_study_focus": {"type": "string"},
            "evidence_informed_study_focus": {"type": "string"},
            "refined_background": {"type": "string"},
            "defensible_research_gap": {"type": "string"},
            "refined_contribution": {"type": "string"},
            "current_study_positioning": {"type": "string"},
            "scope_boundaries": string_array,
            "claims_to_avoid": string_array,
            "to_be_confirmed": string_array,
            "refined_research_questions": refined_research_questions,
            "refined_writing_scope": refined_writing_scope,
            "refined_agent_instructions": refined_agent_instructions,
            "outline_context": outline_context,
            "writer_context": writer_context,
            "main_framing_changes": string_array,
            "research_question_changes": string_array,
            "scope_changes": string_array,
            "downstream_cascade_notes": string_array,
            "human_review_checklist": string_array,
            "change_rows": {"type": "array", "items": change_row},
        },
        "required": [
            "completion_status",
            "original_study_focus",
            "evidence_informed_study_focus",
            "refined_background",
            "defensible_research_gap",
            "refined_contribution",
            "current_study_positioning",
            "scope_boundaries",
            "claims_to_avoid",
            "to_be_confirmed",
            "refined_research_questions",
            "refined_writing_scope",
            "refined_agent_instructions",
            "outline_context",
            "writer_context",
            "main_framing_changes",
            "research_question_changes",
            "scope_changes",
            "downstream_cascade_notes",
            "human_review_checklist",
            "change_rows",
        ],
    }


def outline_schema() -> dict[str, Any]:
    string_array = {"type": "array", "items": {"type": "string"}}
    section_level_outline = {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "introduction": string_array,
            "review_of_related_literature": string_array,
            "methodology": string_array,
            "results": string_array,
            "discussion": string_array,
            "conclusion_recommendations": string_array,
        },
        "required": [
            "introduction",
            "review_of_related_literature",
            "methodology",
            "results",
            "discussion",
            "conclusion_recommendations",
        ],
    }
    introduction_outline = {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "opening_context": string_array,
            "problem_background": string_array,
            "evidence_based_gap": string_array,
            "local_context": string_array,
            "study_purpose": string_array,
            "research_questions_or_objectives": string_array,
            "significance": string_array,
            "scope_and_delimitations": string_array,
            "suggested_citation_anchors": string_array,
            "claims_to_avoid": string_array,
            "to_be_confirmed": string_array,
        },
        "required": [
            "opening_context",
            "problem_background",
            "evidence_based_gap",
            "local_context",
            "study_purpose",
            "research_questions_or_objectives",
            "significance",
            "scope_and_delimitations",
            "suggested_citation_anchors",
            "claims_to_avoid",
            "to_be_confirmed",
        ],
    }
    rrl_theme = {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "theme": {"type": "string"},
            "key_evidence_to_discuss": string_array,
            "suggested_citation_anchors": string_array,
            "relationship_to_current_study": {"type": "string"},
            "limitations_or_cautions": string_array,
        },
        "required": [
            "theme",
            "key_evidence_to_discuss",
            "suggested_citation_anchors",
            "relationship_to_current_study",
            "limitations_or_cautions",
        ],
    }
    rrl_outline = {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "rrl_framing": {"type": "string"},
            "themes": {"type": "array", "items": rrl_theme},
            "direct_evidence_section": string_array,
            "indirect_evidence_section": string_array,
            "methodological_literature_section": string_array,
            "synthesis_toward_gap": string_array,
            "claims_to_avoid": string_array,
            "to_be_confirmed": string_array,
        },
        "required": [
            "rrl_framing",
            "themes",
            "direct_evidence_section",
            "indirect_evidence_section",
            "methodological_literature_section",
            "synthesis_toward_gap",
            "claims_to_avoid",
            "to_be_confirmed",
        ],
    }
    methodology_outline = {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "research_design": {"type": "string"},
            "study_setting": {"type": "string"},
            "population_and_sampling": {"type": "string"},
            "variables": string_array,
            "data_sources": string_array,
            "measures_and_operational_definitions": string_array,
            "statistical_analysis_plan": string_array,
            "ethical_considerations": {"type": "string"},
            "limitations_of_method": string_array,
            "to_be_confirmed": string_array,
        },
        "required": [
            "research_design",
            "study_setting",
            "population_and_sampling",
            "variables",
            "data_sources",
            "measures_and_operational_definitions",
            "statistical_analysis_plan",
            "ethical_considerations",
            "limitations_of_method",
            "to_be_confirmed",
        ],
    }
    results_outline = {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "completion_status": {"type": "string", "enum": OUTLINE_READINESS_STATUSES},
            "available_statistical_inputs": string_array,
            "proposed_results_organization": string_array,
            "table_and_figure_plan": string_array,
            "results_by_research_question": string_array,
            "required_statistical_outputs": string_array,
            "missing_results_to_confirm": string_array,
            "claims_not_allowed_yet": string_array,
        },
        "required": [
            "completion_status",
            "available_statistical_inputs",
            "proposed_results_organization",
            "table_and_figure_plan",
            "results_by_research_question",
            "required_statistical_outputs",
            "missing_results_to_confirm",
            "claims_not_allowed_yet",
        ],
    }
    discussion_outline = {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "opening_summary_of_expected_results": string_array,
            "interpretation_plan": string_array,
            "relationship_to_literature_synthesis": string_array,
            "implications": string_array,
            "limitations": string_array,
            "recommendations": string_array,
            "conclusion_direction": string_array,
            "claims_to_avoid": string_array,
            "to_be_confirmed": string_array,
        },
        "required": [
            "opening_summary_of_expected_results",
            "interpretation_plan",
            "relationship_to_literature_synthesis",
            "implications",
            "limitations",
            "recommendations",
            "conclusion_direction",
            "claims_to_avoid",
            "to_be_confirmed",
        ],
    }
    outline_map_row = {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "manuscript_section": {"type": "string", "enum": MANUSCRIPT_SECTIONS},
            "subsection": {"type": "string"},
            "purpose": {"type": "string"},
            "source_basis": {"type": "string"},
            "suggested_citation_keys": {"type": "string"},
            "required_inputs": {"type": "string"},
            "readiness_status": {"type": "string", "enum": OUTLINE_READINESS_STATUSES},
            "caution_notes": {"type": "string"},
        },
        "required": [
            "manuscript_section",
            "subsection",
            "purpose",
            "source_basis",
            "suggested_citation_keys",
            "required_inputs",
            "readiness_status",
            "caution_notes",
        ],
    }
    readiness = {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "ready_for_drafting": string_array,
            "partially_ready": string_array,
            "blocked_until_more_inputs": string_array,
            "human_review_needed": string_array,
            "recommended_next_step": {"type": "string"},
        },
        "required": [
            "ready_for_drafting",
            "partially_ready",
            "blocked_until_more_inputs",
            "human_review_needed",
            "recommended_next_step",
        ],
    }
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "completion_status": {"type": "string", "enum": ["completed", "partial", "blocked"]},
            "refined_manuscript_positioning": {"type": "string"},
            "working_title_direction": {"type": "string"},
            "central_argument": {"type": "string"},
            "intended_manuscript_flow": string_array,
            "section_level_outline": section_level_outline,
            "introduction_outline": introduction_outline,
            "rrl_outline": rrl_outline,
            "methodology_outline": methodology_outline,
            "results_outline": results_outline,
            "discussion_outline": discussion_outline,
            "citation_and_evidence_use_rules": string_array,
            "claims_to_avoid": string_array,
            "items_to_confirm": string_array,
            "outline_map_rows": {"type": "array", "items": outline_map_row},
            "readiness": readiness,
        },
        "required": [
            "completion_status",
            "refined_manuscript_positioning",
            "working_title_direction",
            "central_argument",
            "intended_manuscript_flow",
            "section_level_outline",
            "introduction_outline",
            "rrl_outline",
            "methodology_outline",
            "results_outline",
            "discussion_outline",
            "citation_and_evidence_use_rules",
            "claims_to_avoid",
            "items_to_confirm",
            "outline_map_rows",
            "readiness",
        ],
    }


def results_interpretation_schema() -> dict[str, Any]:
    string_array = {"type": "array", "items": {"type": "string"}}
    finding_by_objective = {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "objective_id": {"type": "string"},
            "objective_text": {"type": "string"},
            "available_results": string_array,
            "statistical_test_or_model": {"type": "string"},
            "key_numerical_findings": string_array,
            "p_value_or_ci": {"type": "string"},
            "significance_status": {"type": "string", "enum": SIGNIFICANCE_STATUSES},
            "plain_language_result": {"type": "string"},
            "interpretation_boundary": {"type": "string"},
            "result_readiness": {"type": "string", "enum": RESULT_READINESS_VALUES},
            "missing_items": string_array,
            "notes": {"type": "string"},
        },
        "required": [
            "objective_id",
            "objective_text",
            "available_results",
            "statistical_test_or_model",
            "key_numerical_findings",
            "p_value_or_ci",
            "significance_status",
            "plain_language_result",
            "interpretation_boundary",
            "result_readiness",
            "missing_items",
            "notes",
        ],
    }
    table_item = {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "table_title": {"type": "string"},
            "purpose": {"type": "string"},
            "source_result_files": string_array,
            "required_columns": string_array,
            "available": string_array,
            "missing": string_array,
            "notes": {"type": "string"},
        },
        "required": ["table_title", "purpose", "source_result_files", "required_columns", "available", "missing", "notes"],
    }
    figure_item = {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "figure_title": {"type": "string"},
            "purpose": {"type": "string"},
            "source_result_files": string_array,
            "available": string_array,
            "missing": string_array,
            "notes": {"type": "string"},
        },
        "required": ["figure_title", "purpose", "source_result_files", "available", "missing", "notes"],
    }
    missing = {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "required_before_results_drafting": string_array,
            "required_before_discussion_drafting": string_array,
            "missing_by_objective": string_array,
            "missing_tables_or_figures": string_array,
            "missing_statistical_details": string_array,
            "human_or_statistician_followup_questions": string_array,
        },
        "required": [
            "required_before_results_drafting",
            "required_before_discussion_drafting",
            "missing_by_objective",
            "missing_tables_or_figures",
            "missing_statistical_details",
            "human_or_statistician_followup_questions",
        ],
    }
    statistical_finding = {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "objective_id": {"type": "string"},
            "source_file": {"type": "string"},
            "finding_type": {"type": "string", "enum": FINDING_TYPES},
            "variable_or_predictor": {"type": "string"},
            "outcome": {"type": "string"},
            "statistical_method": {"type": "string"},
            "reported_value": {"type": "string"},
            "p_value": {"type": "string"},
            "confidence_interval": {"type": "string"},
            "interpretation": {"type": "string"},
            "writing_use": {"type": "string", "enum": RESULT_WRITING_USES},
            "caution_level": {"type": "string", "enum": CAUTION_LEVELS},
            "notes": {"type": "string"},
        },
        "required": [
            "objective_id",
            "source_file",
            "finding_type",
            "variable_or_predictor",
            "outcome",
            "statistical_method",
            "reported_value",
            "p_value",
            "confidence_interval",
            "interpretation",
            "writing_use",
            "caution_level",
            "notes",
        ],
    }
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "completion_status": {"type": "string", "enum": ["completed", "partial", "blocked"]},
            "inputs_used": string_array,
            "study_objectives_or_research_questions": string_array,
            "results_availability_summary": {"type": "string"},
            "findings_by_objective": {"type": "array", "items": finding_by_objective},
            "overall_results_pattern": {"type": "string"},
            "results_ready_to_write": string_array,
            "results_partial": string_array,
            "results_missing": string_array,
            "statistical_claims_allowed": string_array,
            "statistical_claims_not_allowed": string_array,
            "notes_for_results_writer": string_array,
            "notes_for_discussion_writer": string_array,
            "recommended_tables": {"type": "array", "items": table_item},
            "recommended_figures": {"type": "array", "items": figure_item},
            "missing_results_to_confirm": missing,
            "statistical_findings": {"type": "array", "items": statistical_finding},
        },
        "required": [
            "completion_status",
            "inputs_used",
            "study_objectives_or_research_questions",
            "results_availability_summary",
            "findings_by_objective",
            "overall_results_pattern",
            "results_ready_to_write",
            "results_partial",
            "results_missing",
            "statistical_claims_allowed",
            "statistical_claims_not_allowed",
            "notes_for_results_writer",
            "notes_for_discussion_writer",
            "recommended_tables",
            "recommended_figures",
            "missing_results_to_confirm",
            "statistical_findings",
        ],
    }
