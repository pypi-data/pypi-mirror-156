"""PJScript ScopedAssignmentExpression"""

from pjscript.models.expression.assignment \
    import AssignmentExpression


class ScopedAssignmentExpression(AssignmentExpression):

    """ScopedAssignmentExpression class"""

    def generate(self, top: bool = False, **opts) -> str:

        """Generate ScopedAssignmentExpression"""

        return f'_env->set(' \
               f'{self.lhs().generate()}, ' \
               f'{self.rhs().generate()}, ' \
               f'{"true" if self.mutable() else "false"})' + (';' if top else '')
