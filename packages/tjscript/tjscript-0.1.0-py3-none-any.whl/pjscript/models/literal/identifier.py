"""PJScript IdentifierLiteral"""

from .base import BaseLiteral


class IdentifierLiteral(BaseLiteral):

    """IdentifierLiteral class"""

    def generate(self, top: bool = False, **opts):

        """Generate "IdentifierLiteral"""

        append = opts.get('append', '')  # <- could be #constructor or None ('')

        return f'(char*)"{self.token().value()}{append}"' + (';' if top else '')
