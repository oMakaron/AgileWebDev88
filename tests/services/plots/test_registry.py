from unittest import TestCase

from app.services.plots.registry import PlotRegistry


class TestPlotRegistry(TestCase):

    def setUp(self) -> None:
        self.registry = PlotRegistry()


    def test_registry_associates_names(self) -> None:
        self.registry.register_as('test')(lambda x: x)
        self.assertIn('test', self.registry.functions)


    def test_errors_on_duplicate_name(self) -> None:
        self.registry.register_as('test')(lambda x: x)
        self.assertRaises(RuntimeError, self.registry.register_as, 'test')


    def test_stores_all_functions(self) -> None:
        self.registry.register_as('test1')(lambda x: x)
        self.registry.register_as('test2')(lambda x: x)
        self.registry.register_as('test3')(lambda x: x)
        self.assertEqual(3, len(self.registry.functions))
