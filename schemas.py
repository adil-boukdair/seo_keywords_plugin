"""Tool schemas — what the LLM sees to decide when to call each tool."""

INSERT_SEED_KEYWORDS = {
    "name": "insert_seed_keywords",
    "description": (
        "Insert one or more seed keywords into the SEO database for a given market. "
        "Use this when the user wants to add, save, or store seed keywords for a market or niche. "
        "A market is a broad topic or category (e.g. 'running shoes', 'home automation', 'keto diet'). "
        "Seed keywords are the initial keyword ideas to explore for that market. "
        "Duplicate keywords for the same market are ignored automatically."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "market": {
                "type": "string",
                "description": (
                    "The market or niche these keywords belong to "
                    "(e.g. 'running shoes', 'home automation', 'keto diet'). "
                    "Used to group keywords by topic."
                ),
            },
            "seed_keywords": {
                "type": "array",
                "items": {"type": "string"},
                "description": (
                    "List of seed keywords to insert for this market. "
                    "Each entry is a single keyword or short phrase "
                    "(e.g. ['best running shoes', 'trail running shoes', 'running shoes for flat feet']). "
                    "Minimum 1 keyword required."
                ),
                "minItems": 1,
            },
        },
        "required": ["market", "seed_keywords"],
    },
}

ANALYZE_KEYWORD_OPPORTUNITIES = {
    "name": "analyze_keyword_opportunities",
    "description": (
        "PLACEHOLDER — not yet implemented. "
        "Will analyze stored seed keywords for a market and suggest keyword expansion opportunities, "
        "cluster them by intent, and identify gaps. "
        "Use this when the user asks to analyze, expand, or cluster keywords for a market."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "market": {
                "type": "string",
                "description": "The market to analyze keywords for.",
            },
            "mode": {
                "type": "string",
                "enum": ["cluster", "expand", "gaps"],
                "description": (
                    "Analysis mode: "
                    "'cluster' groups keywords by search intent, "
                    "'expand' suggests related keywords, "
                    "'gaps' identifies missing keyword categories."
                ),
                "default": "expand",
            },
        },
        "required": ["market"],
    },
}
