from unittest import TestCase

from app.services.plots.registry import PlotterFunction, BindError


class TestPlotterFunction(TestCase):

    def test_finds_required(self) -> None:
        def test_function(a):
            ...
        captured = PlotterFunction(test_function, {})
        self.assertEqual(['a'], captured.required)


    def test_finds_optional(self) -> None:
        def test_function(a = 1):
            ...
        captured = PlotterFunction(test_function, {})
        self.assertEqual(['a'], captured.optional)


    def test_multiple_arguments(self) -> None:
        def test_function(a, b, c = 2):
            ...
        captured = PlotterFunction(test_function, {})
        self.assertEqual(['a', 'b'], captured.required)
        self.assertEqual(['c'], captured.optional)


    def test_finds_annotations(self) -> None:
        def test_function(a: int):
            ...
        captured = PlotterFunction(test_function, {})
        self.assertEqual({'a': int}, captured.annotations)


    def test_remaps_present(self) -> None:
        def test_function(a: int):
            ...
        captured = PlotterFunction(test_function, {int: str})
        self.assertEqual({'a': str}, captured.annotations)


    def test_binding_all_present(self) -> None:
        def test_function(a: int, b: int):
            ...
        captured = PlotterFunction(test_function, {})
        self.assertEqual(({'a': 3, 'b': 4}, []), captured.bind_args(a = 3, b = 4))


    def test_binding_all_present_no_annotations(self) -> None:
        def test_function(a, b):
            ...
        captured = PlotterFunction(test_function, {})
        self.assertEqual(({'a': 3, 'b': 4}, []), captured.bind_args(a = 3, b = 4))


    def test_binding_casts_args(self) -> None:
        def test_function(a: int, b: float, c = 2):
            ...
        captured = PlotterFunction(test_function, {})
        self.assertEqual(({'a': 3, 'b': 4.5}, []), captured.bind_args(a = '3', b = '4.5'))


    def test_reports_unbound_args(self) -> None:
        def test_function(a = 2):
            ...
        captured = PlotterFunction(test_function, {})
        bound, unbound = captured.bind_args(fred = 2)
        self.assertIn('fred', unbound[0])


    def test_raises_on_missing(self) -> None:
        def test_function(a):
            ...
        captured = PlotterFunction(test_function, {})
        with self.assertRaises(BindError) as context:
            captured.bind_args()
        self.assertIn("test_function requires parameter a", context.exception.missing())


    def test_raised_on_error(self) -> None:
        def test_function(a: float):
            ...
        captured = PlotterFunction(test_function, {})
        with self.assertRaises(BindError) as context:
            captured.bind_args(a = 'frederick')
        self.assertIn("Cannot convert 'frederick' for use as 'a' in test_function", context.exception.errors())


    def test_raises_unbound_on_error(self) -> None:
        def test_function(a: int):
            ...
        captured = PlotterFunction(test_function, {})
        with self.assertRaises(BindError) as context:
            captured.bind_args(a = 'frederick', b = 10)
        self.assertIn("b", context.exception.unbound()[0])
