"""Main task, part 3 of your submission: generators of resolution problems.

TODO(students): implement problems() and planted_problems().

Grading runs your generators against incorrect resolvers. Some are wrong on
almost any input; others are wrong only on inputs a naive generator rarely
produces. Your generators are measured by how many of those they expose,
with a fixed number of examples per test.

  * problems(): any well-formed problems, satisfiable or not. Every
    Problem you build is checked when it is constructed (see the dataclasses
    in pbt/resolver.py).

  * planted_problems(): pairs (problem, witness) where `witness` is a valid
    solution for `problem` by construction. A resolver that returns None for
    such a problem is wrong. Every witness you produce is checked against a
    reference implementation of the properties; a single invalid witness
    makes this generator score zero.

Think about what makes resolution hard, and make sure your generators
produce it often. Filtering with assume() or .filter() to reach the
interesting cases tends to fail Hypothesis's health checks; construct them
instead. Do not change the imports, except to add more from hypothesis.
"""

from __future__ import annotations

from hypothesis import strategies as st

from pbt.resolver import Problem, Release, Requirement


def problems() -> st.SearchStrategy[Problem]:
    """Well-formed problems, satisfiable or not."""

    @st.composite
    def generate(draw: st.DrawFn) -> Problem:
        packages = ["a", "b", "c", "d", "e"]
        targets = [*packages, "missing"]

        def requirement() -> Requirement:
            package = draw(st.sampled_from(targets))
            low = draw(st.integers(1, 5))
            high = draw(st.integers(low, 5))
            return Requirement(package, low, high)

        releases: list[Release] = []

        for package in packages:
            versions = draw(
                st.lists(
                    st.integers(1, 5),
                    unique=True,
                    max_size=3,
                )
            )

            for version in versions:
                count = draw(st.integers(0, 3))
                requires = tuple(requirement() for _ in range(count))

                releases.append(Release(package, version, requires))

        root_count = draw(st.integers(0, 4))
        root = tuple(requirement() for _ in range(root_count))

        return Problem(tuple(releases), root)

    return generate()


def planted_problems() -> st.SearchStrategy[tuple[Problem, dict[str, int]]]:
    """Problems paired with a valid solution built in."""

    @st.composite
    def generate(draw: st.DrawFn) -> tuple[Problem, dict[str, int]]:
        packages = draw(
            st.lists(
                st.sampled_from(["a", "b", "c", "d", "e"]),
                unique=True,
                max_size=5,
            )
        )

        witness = {package: draw(st.integers(1, 5)) for package in packages}

        releases: list[Release] = []

        def compatible_requirement(package: str) -> Requirement:
            version = witness[package]
            low = draw(st.integers(1, version))
            high = draw(st.integers(version, 5))
            return Requirement(package, low, high)

        for i, package in enumerate(packages):
            version = witness[package]
            requires: list[Requirement] = []

            # Connect packages into a dependency chain.
            if i + 1 < len(packages):
                requires.append(compatible_requirement(packages[i + 1]))

            # Add extra compatible dependencies.
            if packages:
                targets = draw(
                    st.lists(
                        st.sampled_from(packages),
                        max_size=3,
                    )
                )

                for target in targets:
                    requires.append(compatible_requirement(target))

            releases.append(Release(package, version, tuple(requires)))

            # Add alternative versions.
            alternatives = [v for v in range(1, 6) if v != version]

            extra_versions = draw(
                st.lists(
                    st.sampled_from(alternatives),
                    unique=True,
                    max_size=2,
                )
            )

            for extra_version in extra_versions:
                releases.append(Release(package, extra_version))

        root: tuple[Requirement, ...] = ()

        if packages:
            root = (compatible_requirement(packages[0]),)

        problem = Problem(tuple(releases), root)

        return problem, witness

    return generate()
