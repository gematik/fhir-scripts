class Version:
    def __init__(self, version_string: str | None = None):
        parts = version_string.split(".", 2) if version_string is not None else []

        self.major = parts[0] if len(parts) > 0 else None
        self.minor = parts[1] if len(parts) > 1 else None
        self.patch = parts[2] if len(parts) > 2 else None

        self.add_version: Version | None = None

    def __str__(self) -> str:
        if self.unknown:
            return "n/a"

        else:
            return ".".join(
                [p for p in [self.major, self.minor, self.patch] if p is not None]
            )

    def __repr__(self) -> str:
        return str(self)

    @property
    def long(self):
        return (
            "{} [{}]".format(self, self.add_version.long)
            if self.add_version
            else str(self)
        )

    @property
    def unknown(self):
        return self.major is None and self.minor is None and self.patch is None

    def __eq__(self, other) -> bool:
        return (self.unknown and other.unknown) or (
            self.major == other.major
            and self.minor == other.minor
            and self.patch == other.patch
        )

    def __gt__(self, other) -> bool:
        if self.unknown or other.unknown:
            return False

        if res := _gt_helper(self.major, other.major) is not None:
            return res

        if res := _gt_helper(self.minor, other.minor) is not None:
            return res

        if res := _gt_helper(self.patch, other.patch) is not None:
            return res

        return False

    def __ge__(self, other):
        return self == other or self > other


def _gt_helper(one, two) -> bool | None:
    if one is None:
        return False

    if two is None:
        return True

    if one < two:
        return False

    if one > two:
        return True

    return None
