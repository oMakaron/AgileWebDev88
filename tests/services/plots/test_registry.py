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


    def test_list_plots(self) -> None:
        self.registry.register_as('test 1')(lambda x: x + x)
        self.registry.register_as('test 2')(lambda x, y: x * y)
        self.assertEqual([{'name': 'test 1'}, {'name': 'test 2'}], self.registry.list_plots())


    def test_list_common_args_init_largest(self) -> None:
        self.registry.register_as('test 1')(lambda x, y, z, a, b, c: ...)
        self.registry.register_as('test 2')(lambda x, y,    a, b   : ...)
        self.registry.register_as('test 3')(lambda x,    z,       c: ...)
        self.assertEqual([{'name': 'x', 'required': 'true'}], self.registry.list_common_args())


    def test_list_common_args_init_smallest(self) -> None:
        self.registry.register_as('test 1')(lambda x: x)
        self.registry.register_as('test 2')(lambda x, y, z: x + y + z)
        self.assertEqual([{'name': 'x', 'required': 'true'}], self.registry.list_common_args())

