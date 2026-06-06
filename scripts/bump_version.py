"""Compute the next patch version from the latest git tag (auto rebuild)."""
import re
import sys

_SEMVER = re.compile(r"^v?(\d+)\.(\d+)\.(\d+)$")


def next_patch(latest_tag):
    """Return the next patch version (always 'v'-prefixed).

    Empty/None -> 'v1.0.0' (first release). Raises ValueError on malformed input.
    """
    if not latest_tag:
        return "v1.0.0"
    m = _SEMVER.match(latest_tag.strip())
    if not m:
        raise ValueError(f"not a semver tag: {latest_tag!r}")
    major, minor, patch = (int(g) for g in m.groups())
    return f"v{major}.{minor}.{patch + 1}"


if __name__ == "__main__":
    print(next_patch(sys.argv[1] if len(sys.argv) > 1 else ""))
