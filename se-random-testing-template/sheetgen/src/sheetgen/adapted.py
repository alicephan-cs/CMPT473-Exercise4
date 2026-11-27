"""Phase 2 adaptation: your improved generator.

TODO(students): implement generate().

Before changing anything, write down your hypothesis: which pipeline stage
or code your change should reach, and why the naive generator cannot. Then
make one targeted change and measure its effect with run-trials and covtrace.

You may reuse code from naive.py.
"""

from __future__ import annotations

import random

from sheetgen.grammar import (
    GRAMMAR,
    cheapest_expansions,
    is_nonterminal,
)


def generate(rng: random.Random, *, max_depth: int = 20) -> str:
    """Returns one sheet. All randomness must come from `rng`."""
    # Require the first line to contain a cell assignment.
    stack = [("<lines>", 2)]

    for symbol in reversed(GRAMMAR["<line>"][0]):
        stack.append((symbol, 3))

    stack.append(("#sheet v1\n", 1))

    output: list[str] = []

    while stack:
        symbol, depth = stack.pop()

        if not is_nonterminal(symbol):
            output.append(symbol)
            continue

        expansions = GRAMMAR[symbol] if depth < max_depth else cheapest_expansions(symbol)

        expansion = rng.choice(expansions)

        for child in reversed(expansion):
            stack.append((child, depth + 1))

    return "".join(output)
