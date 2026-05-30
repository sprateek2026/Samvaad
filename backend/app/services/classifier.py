import json
from ..rules.categories import CATEGORY_RULES, CATEGORY_LIST
from ..config import OLLAMA_MODEL, OLLAMA_HOST

OLLAMA_CLASSIFICATION_PROMPT = """You are a civic complaint classifier for Pune city, India. Classify the following complaint into exactly one category.

Categories: {categories}

Rules:
- Garbage: waste collection, trash, bins, kacra
- Potholes: road damage, broken roads, khadda
- Streetlights: lights not working, dark roads, lamp posts
- Drainage: sewage, drain block, water logging, gutter
- Water Supply: no water, pipe leakage, pani purvatha

Respond ONLY with valid JSON: {{"category": "...", "confidence": 0.0-1.0, "reason": "..."}}

Complaint Title: {title}
Description: {description}

JSON:"""


def classify_with_rules(title: str, description: str) -> dict | None:
    text = (title + " " + description).lower()

    for category, rule in CATEGORY_RULES.items():
        for keyword in rule["keywords"]:
            if keyword.lower() in text:
                return {
                    "category": category,
                    "confidence": 0.95,
                    "method": "rule",
                    "routing": rule["routing"],
                    "sla_hours": rule["sla_hours"]
                }
    return None


def classify_with_ollama(title: str, description: str) -> dict:
    try:
        import ollama
        prompt = OLLAMA_CLASSIFICATION_PROMPT.format(
            categories=", ".join(CATEGORY_LIST),
            title=title,
            description=description
        )
        response = ollama.generate(
            model=OLLAMA_MODEL,
            prompt=prompt,
            host=OLLAMA_HOST,
            options={"temperature": 0.1, "num_predict": 128}
        )
        text = response.get("response", "").strip()
        text = text.replace("```json", "").replace("```", "").strip()
        result = json.loads(text)
        category = result.get("category", "").lower().strip()
        if category in CATEGORY_RULES:
            rule = CATEGORY_RULES[category]
            return {
                "category": category,
                "confidence": result.get("confidence", 0.8),
                "method": "llm",
                "routing": rule["routing"],
                "sla_hours": rule["sla_hours"]
            }
    except Exception as e:
        print(f"Ollama classification failed: {e}")

    return {
        "category": "other",
        "confidence": 0.5,
        "method": "fallback",
        "routing": "corporator",
        "sla_hours": 168
    }


def classify_complaint(title: str, description: str) -> dict:
    result = classify_with_rules(title, description)
    if result:
        return result
    return classify_with_ollama(title, description)
