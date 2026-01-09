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

        # Major
        if self.major < other.major:
            return False

        if self.major > other.major:
            return True

        # Minor
        if self.minor is None or self.minor < other.minor:
            return False

        if other.minor is None or self.minor > other.minor:
            return True

        # Patch
        if self.patch is None or self.patch < other.patch:
            return False

        if other.patch is None or self.patch > other.patch:
            return True

        return False
