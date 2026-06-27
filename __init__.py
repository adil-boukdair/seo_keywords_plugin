"""seo-keywords plugin — registration.

Wires schemas → handlers and registers both tools with Hermes.
"""

import logging

from . import schemas, tools

logger = logging.getLogger(__name__)


def register(ctx):
    """Called once at startup by the Hermes plugin loader."""

    # Tool 1: insert seed keywords into MariaDB
    ctx.register_tool(
        name="insert_seed_keywords",
        toolset="seo-keywords",
        schema=schemas.INSERT_SEED_KEYWORDS,
        handler=tools.insert_seed_keywords,
        check_fn=tools.check_db_requirements,
    )

    # Tool 2: placeholder for future keyword analysis
    ctx.register_tool(
        name="analyze_keyword_opportunities",
        toolset="seo-keywords",
        schema=schemas.ANALYZE_KEYWORD_OPPORTUNITIES,
        handler=tools.analyze_keyword_opportunities,
        # No check_fn — placeholder is always visible so the LLM
        # knows it exists and can tell the user it's coming soon.
    )

    logger.info("seo-keywords plugin registered (2 tools)")
