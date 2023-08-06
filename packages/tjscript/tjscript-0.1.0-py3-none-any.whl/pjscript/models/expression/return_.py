"""PJScript ReturnExpression"""

from pjscript.models.expression.base \
    import BaseExpression
from pjscript.models.base import BaseModel


class ReturnExpression(BaseExpression):

    """ReturnExpression class"""

    _value: BaseModel

    def __init__(self, value: BaseModel) -> None:

        """Instantiate ReturnExpression"""

        self._value = value

    def value(self) -> BaseModel:

        """Returns ReturnExpression parameters"""

        return self._value

    def to_dict(self) -> dict:

        """Returns dict representation"""

        return {
            "class": 'ReturnExpression',
            'value': self.value().to_dict()
        }

    def __repr__(self) -> str:

        """Debugging simplified"""

        return self.__str__()

    def __str__(self) -> str:

        """Custom serializer, for ReturnExpression"""

        return f'ReturnExpression ({ self.value() })'
