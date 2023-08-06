"""PJScript MemberAccessExpression"""

from pjscript.models.expression.access \
    import AccessExpression


class MemberAccessExpression(AccessExpression):

    """MemberAccessExpression class"""

    def generate(self, top: bool = False, **opts) -> str:

        """Generate MemberAccessExpression"""

        # TODO: figure out, how to offload certain amount of logic to the IdentifierLiteral?

        parts = self.name().token().value().split('.')  # <- split name by the '.' character

        return f'_env->get((char*)"{parts[0]}")' + \
               ''.join([f'->get((char*)"{pt}")' for pt in parts[1:]]) + (';' if top else '')
