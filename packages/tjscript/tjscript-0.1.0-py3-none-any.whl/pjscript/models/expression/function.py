"""PJScript FunctionExpression"""

# pylint: disable=line-too-long  # it complains about last lines

from typing import List
from pjscript.models.expression.base import BaseExpression
from pjscript.models.literal.identifier import IdentifierLiteral
from pjscript.models.base import BaseModel


class FunctionExpression(BaseExpression):

    """FunctionExpression class"""

    _parameters: List[IdentifierLiteral]
    _body: List[BaseModel]

    def __init__(self,
                 parameters: List[IdentifierLiteral],
                 body: List[BaseModel]) -> None:

        """Instantiate FunctionExpression"""

        self._parameters = parameters
        self._body = body

    def parameters(self) -> List[IdentifierLiteral]:

        """Returns FunctionExpression parameters"""

        return self._parameters

    def body(self) -> list:

        """Returns FunctionExpression body"""

        return self._body

    def to_dict(self) -> dict:

        """Returns dict representation"""

        return {
            "class": 'FunctionExpression',
            "parameters": [param.to_dict() for param in self.parameters()],
            "body": [expr.to_dict() for expr in self.body()]
        }

    def generate(self, top: bool = False, **opts) -> str:

        """Generate FunctionExpression"""

        # TODO: we need to actually generate FunctionObject

        return 'new NullPrimitive()' + (';' if top else '')

    def __repr__(self) -> str:

        """Debugging simplified"""

        return self.__str__()

    def __str__(self) -> str:

        """Custom serializer for FunctionExpression made to simplify debugging"""

        parameters_formatted = ', '.join(map(str, self.parameters()))    # params
        body_formatted = ', '.join(map(str, self.body()))  # formatted body and ^

        return f'FunctionExpression [{parameters_formatted}] [{body_formatted}])'
