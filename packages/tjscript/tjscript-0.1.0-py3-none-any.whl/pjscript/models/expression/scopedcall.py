"""PJScript ScopedCallExpression"""

# pylint: disable=line-too-long  # :)

from pjscript.models.expression.call \
    import CallExpression


class ScopedCallExpression(CallExpression):

    """ScopedCallExpression class"""

    def generate(self, top: bool = False, **opts) -> str:

        """Generate ScopedCallExpression"""

        append = '#constructor' if self.instantiation() else ''  # look up for 'constructor' in this case

        cast = 'constructor' if self.instantiation() else 'function'  # determine the right 'cast' method

        args = '{' + ', '.join(map(lambda argument:  argument.generate() + '->some()', self.args())) + '}'

        return f'_env->get({self.name().generate(append=append)})->{cast}()({args})' + (';'if top else '')
