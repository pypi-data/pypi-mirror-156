"""PJScript MemberAssignmentExpression"""

from pjscript.models.expression.assignment \
    import AssignmentExpression


class MemberAssignmentExpression(AssignmentExpression):

    """MemberAssignmentExpression class"""

    def generate(self, top: bool = False, **opts) -> str:

        """Generate MemberAssignmentExpression"""

        # TODO: figure out, how to offload certain logic to the IdentifierLiteral

        parts = self.lhs().token().value().split('.')  # <--- split name by a dot

        generated = f'_env->get((char*)"{parts[0]}")'  # <- start with first: get

        for part in parts[1:-1]:
            generated += f'->get((char*)"{part}")'  # <-- then continue with gets

        generated += f'->set((char*)"{parts[-1]}"'  # <- and finally generate set

        return f'{generated}, ' \
               f'{self.rhs().generate()}, ' \
               f'{"true" if self.mutable() else "false"})' + (';' if top else '')
