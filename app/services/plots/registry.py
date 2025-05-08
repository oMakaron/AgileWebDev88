from typing import Any, Callable
from inspect import Parameter, signature


def unbound_error(param_name: str, f_name: str) -> str:
    return f"Couldn't find parameter {param_name!r} in {f_name}"


class BindError(Exception):

    def __init__(self, missing: list[str], errors: list[tuple[str, Any]], unbound: list[str], func_name: str) -> None:
        self._missing, self._errors, self._unbound = missing, errors, unbound
        self._name = func_name

    def missing(self) -> list[str]:
        return [f"{self._name} requires parameter {name}" for name in self._missing]

    def errors(self) -> list[str]:
        return [f"Cannot convert {value!r} for use as {param!r} in {self._name}" for value, param in self._errors]

    def unbound(self) -> list[str]:
        return [name for name in self._unbound]


class PlotterFunction:
    function: Callable
    required: list[str] # parameters that don't have a default value will be required
    optional: list[str] # parameters that do have a default value will be optional
    combined: list[str] # contains the total list of parameter names
    annotations: dict[str, Callable] # maps between parameter name and type

    def __init__(self, function: Callable, remaps: dict[Callable, Callable]) -> None:
        sig = signature(function)

        self.function = function
        self.required, self.optional, self.combined  = [], [], []
        self.annotations = dict()

        for name, param in sig.parameters.items():
            self.combined.append(name)
            self.annotations[name] = remaps.get(param.annotation, param.annotation)
            if param.default is Parameter.empty:
                self.required.append(name)
            else:
                self.optional.append(name)

    def bind_args(self, **kwargs) -> tuple[dict[str, Any], list[str]]:
        # finds any args that should be present but are not
        missing = [arg for arg in self.required if not arg in kwargs]

        # attempts to cast arguments to the appropriate type and makes note of errors
        errors = []
        bound = {name: self._cast(name, value, errors) for name, value in kwargs.items() if name in self.combined}

        # makes note of any arguments that are present but unexpected
        unbound = [unbound_error(arg, self.function.__name__) for arg in kwargs.keys() if arg not in self.combined]

        # missing arguments or failed conversions will raise an error
        if missing or errors:
            raise BindError(missing, errors, unbound, self.function.__name__)

        return bound, unbound

    def _cast(self, name: str, value: Any, errors: list) -> Any:
        try:
            cast_func = self.annotations[name]
            return cast_func(value) if cast_func is not Parameter.empty else value
        except (TypeError, ValueError):
            errors.append((value, name))
            return None


class PlotRegistry:
    functions: dict[str, PlotterFunction]
    _remaps: dict[Any, Callable]

    def __init__(self, remaps: dict[Any, Callable] | None = None) -> None:
        self.functions = dict()
        self._remaps = remaps or dict()

    def register_as(self, name: str) -> Callable:
        def register(function: Callable) -> Callable:
            self.functions[name] = PlotterFunction(function, self._remaps)
            return function

        if name in self.functions:
            raise RuntimeError(f"Cannot register function as there is already a function registered by {name!r}")

        return register

