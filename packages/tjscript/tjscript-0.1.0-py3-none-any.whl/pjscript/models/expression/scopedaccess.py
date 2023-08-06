"""PJScript ScopedAccessExpression"""

from pjscript.models.expression.access \
    import AccessExpression


class ScopedAccessExpression(AccessExpression):

    """ScopedAccessExpression class"""

    def generate(self, top: bool = False, **opts) -> str:

        """Generate ScopedAccessExpression"""

        return f'_env->get({self.name().generate()})' + (';' if top else '')
