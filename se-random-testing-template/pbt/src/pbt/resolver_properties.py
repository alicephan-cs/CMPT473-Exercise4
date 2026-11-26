"""Main task, part 2 of your submission: properties of a resolution.

TODO(students): implement is_valid_solution().

It must return True exactly when `solution` is valid for `problem` according
to the specification in pbt/resolver.py. Grading calls it with outputs of
incorrect resolvers and of several correct ones, including correct resolvers
that choose different solutions than the provided one.

Hint: the specification has four conditions. A function that checks three
of them will accept some incorrect resolvers.
"""

from __future__ import annotations

from pbt.resolver import Problem, Solution


def is_valid_solution(problem: Problem, solution: Solution) -> bool:
    """True if `solution` is a valid solution for `problem`."""
    # Property 1: Every selected release must exist.
    for package, version in solution.items():
        if problem.release(package, version) is None:
            return False

    # Property 2: Every root requirement must be satisfied.
    for req in problem.root:
        if req.package not in solution:
            return False

        if not req.allows(solution[req.package]):
            return False

    # Property 3: Every dependency must be satisfied.
    for package, version in solution.items():
        release = problem.release(package, version)

        if release is None:
            return False

        for req in release.requires:
            if req.package not in solution:
                return False

            if not req.allows(solution[req.package]):
                return False

    # Property 4: Every selected package must be reachable.
    reachable: set[str] = set()
    pending = [req.package for req in problem.root]

    while pending:
        package = pending.pop()

        if package in reachable:
            continue

        reachable.add(package)

        release = problem.release(package, solution[package])

        if release is None:
            return False

        for req in release.requires:
            pending.append(req.package)

    return reachable == set(solution)
