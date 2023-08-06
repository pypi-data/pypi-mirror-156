"""PJScript MemberCallExpression"""

# pylint: disable=line-too-long  # :)

from pjscript.models.expression.call \
    import CallExpression


class MemberCallExpression(CallExpression):

    """MemberCallExpression class"""

    def generate(self, top: bool = False, **opts) -> str:

        """Generate MemberCallExpression"""

        # TODO: need to figure out how to offload certain amount of logic to the IdentifierLiteral class

        parts = self.name().token().value().split('.')  # <---- split a member name by the dot-character

        parts[-1] += ('#constructor' if self.instantiation() else '')   # look up for constructor, if so

        generated = f'_env->get((char*)"{parts[0]}")' \
                    + ''.join([f'->get((char*)"{p}")' for p in parts[1:]])  # <-- get the generated form

        cast = 'constructor' if self.instantiation() else 'function'   # determine the right cast method

        args = '{' + ','.join(map(lambda argum: '(' + argum.generate() + ')->some()', self.args())) + '}'

        return f'{generated}->{cast}()({args})' + (';'if top else '')  # <-- return generated expression
