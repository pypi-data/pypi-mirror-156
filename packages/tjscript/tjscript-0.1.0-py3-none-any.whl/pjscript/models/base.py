"""PJScript BaseModel"""

# pylint: disable=R0903


class BaseModel:

    """BaseModel class"""

    def to_dict(self) -> dict:

        """Returns dict representation"""

    def generate(self, top: bool = False, **opts) -> str:

        """Generate C++ for some expression or literal"""
