from unittest import TestCase

from pandas import DataFrame

from app.plots import registry
from app.logic.specifier import Parser
from app.logic.plotter_registry import BindError


class Test(TestCase):

    def test_binding_errors_on_missing(self) -> None:
        with self.assertRaises(BindError) as context:
            registry.functions['line'].bind_args()

        missing = ['plot_line requires parameter source', 'plot_line requires parameter x_col', 'plot_line requires parameter y_col']
        self.assertEqual(missing, context.exception.missing())

    def test_binding_errors_on_erroneous(self) -> None:
        with self.assertRaises(BindError) as context:
            registry.functions['line'].bind_args(source = 'bad', x_col = 'Header1', y_col = 'Header2')
        errors = ["Cannot convert 'bad' for use as 'source' in plot_line"]
        self.assertEqual(errors, context.exception.errors())

    def test_binding_returns_unbindable(self) -> None:
        _, unbound = registry.functions['line'].bind_args(
            source = [], x_col = 'Header1', y_col = 'Header2', bad = 'bad'
        )
        self.assertEqual(["Couldn't find parameter 'bad' in plot_line"], unbound)

    def test_binding_returns_unbindable_on_error(self) -> None:
        with self.assertRaises(BindError) as context:
            registry.functions['line'].bind_args(
                source = 'bad', x_col = 'Header1', y_col = 'Header2', bad = 'bad'
            )
        unbound = ["Couldn't find parameter 'bad' in plot_line"]
        self.assertEqual(unbound, context.exception.unbound())

    def test_round_trip(self) -> None:
        spec = "type = line, x_col = Header1, y_col = Header2"
        args = Parser.parse_string(spec)

        plot_type = args.pop('type')
        if isinstance(plot_type, list):
            plot_type = plot_type[0]

        plotter = registry.functions[plot_type.lower()]
        bound, unbound = plotter.bind_args(source = [], **args)

        bound_source: DataFrame = bound.pop('source')

        self.assertEqual([], unbound)
        self.assertEqual({'x_col': 'Header1', 'y_col': 'Header2'}, bound)

