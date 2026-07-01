"""seo-keywords plugin — registration.

Wires schemas → handlers and registers both tools with Hermes.
"""

import logging

from . import schemas, tools

logger = logging.getLogger(__name__)


def register(ctx):
    """Called once at startup by the Hermes plugin loader."""

    # Tool 1: insert seed keywords into MariaDB
    # Lambda unpacks the dict Hermes passes into explicit named parameters
    ctx.register_tool(
        name="insert_seed_keywords",
        toolset="seo-keywords",
        schema=schemas.INSERT_SEED_KEYWORDS,
        handler=lambda args, **kw: tools.insert_seed_keywords(
            market=args.get("market", ""),
            seed_keywords=args.get("seed_keywords", []),
        ),
    )

    # Tool 2: placeholder for future keyword analysis
    ctx.register_tool(
        name="analyze_keyword_opportunities",
        toolset="seo-keywords",
        schema=schemas.ANALYZE_KEYWORD_OPPORTUNITIES,
        handler=lambda args, **kw: tools.analyze_keyword_opportunities(
            market=args.get("market", ""),
            mode=args.get("mode", "expand"),
        ),
    )
 
    logger.info("seo-keywords plugin registered (2 tools)")
