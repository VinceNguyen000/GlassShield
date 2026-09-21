"""
GlassShield Policy RAG (Retrieval-Augmented Generation) Module
Retrieves grounded regulatory statutes and bystander consent policies for detected visual PII.
"""

import json
import math
import os
import re
from typing import Dict, Any, List, Optional


class PolicyRAG:
    """Lightweight, self-contained regulatory policy retriever."""

    def __init__(self, kb_path: Optional[str] = None):
        if kb_path is None:
            kb_path = os.path.join(os.path.dirname(__file__), "privacy_knowledge_base.json")
        self.kb_path = kb_path
        self.knowledge_base: List[Dict[str, Any]] = []
        self._load_knowledge_base()

    def _load_knowledge_base(self) -> None:
        if os.path.exists(self.kb_path):
            with open(self.kb_path, "r", encoding="utf-8") as f:
                self.knowledge_base = json.load(f)
        else:
            self.knowledge_base = []

    def _tokenize(self, text: str) -> List[str]:
        return [w.lower() for w in re.findall(r"\b[a-zA-Z0-9_\-]{2,}\b", text)]

    def retrieve(
        self,
        query: str = "",
        detected_classes: Optional[List[str]] = None,
        min_confidence: float = 0.0,
        top_k: int = 3,
    ) -> List[Dict[str, Any]]:
        """
        Retrieves top-k relevant privacy policies given context and optional search query.
        """
        if not self.knowledge_base:
            return []

        detected_classes = detected_classes or []
        query_tokens = set(self._tokenize(query))

        # Augment query tokens with detected context
        if "face" in detected_classes:
            query_tokens.update(["face", "bystander", "biometric", "facial"])
        if "license_plate" in detected_classes or "lp" in detected_classes:
            query_tokens.update(["license", "plate", "vehicle", "car", "identifier"])
        if not detected_classes and not query:
            query_tokens.update(["nature", "clean", "low-risk", "empty", "no", "pii"])
        if min_confidence > 0.0 and min_confidence < 0.50:
            query_tokens.update(["uncertain", "low", "confidence", "obscured", "partial"])

        scored_policies = []
        for policy in self.knowledge_base:
            # Combine policy text fields
            doc_text = " ".join([
                policy.get("title", ""),
                policy.get("category", ""),
                policy.get("summary", ""),
                policy.get("rule_text", ""),
                " ".join(policy.get("keywords", [])),
            ])
            doc_tokens = self._tokenize(doc_text)
            doc_token_set = set(doc_tokens)

            # Compute term overlap score
            overlap = query_tokens.intersection(doc_token_set)
            if not overlap and not query:
                # Fallback score based on default applicability
                base_score = 0.1
            else:
                base_score = len(overlap) / (math.sqrt(len(query_tokens) * len(doc_token_set)) + 1e-6)

            # Keyword priority boosts
            for kw in policy.get("keywords", []):
                if kw in query_tokens:
                    base_score += 0.25

            # Contextual alignment
            if "face" in detected_classes and ("face" in policy.get("keywords", []) or "biometric" in policy.get("keywords", [])):
                base_score += 0.35
            if ("license_plate" in detected_classes or "lp" in detected_classes) and ("license plate" in policy.get("keywords", []) or "vehicle" in policy.get("keywords", [])):
                base_score += 0.35
            if not detected_classes and policy.get("id") == "POL-CLEAN-ENV":
                base_score += 0.80
            if min_confidence > 0.0 and min_confidence < 0.50 and policy.get("id") == "POL-SITARA-UNCERTAIN":
                base_score += 0.90

            normalized_score = min(round(base_score, 3), 1.0)
            result_item = dict(policy)
            result_item["relevance_score"] = normalized_score
            scored_policies.append(result_item)

        # Sort descending by relevance score
        scored_policies.sort(key=lambda x: x["relevance_score"], reverse=True)
        return scored_policies[:top_k]
