from __future__ import annotations


class Specifier:
    dimensions: tuple[int, int]
    x: str | None
    y: str | None

    def __init__(self) -> None:
        self.x, self.y = None, None
        self.dimensions = (10, 8)

    def set_x(self, x: str) -> Specifier:
        self.x = x
        return self

    def set_y(self, y: str) -> Specifier:
        self.y = y
        return self

    @staticmethod
    def from_string(format: str) -> Specifier:

        # TODO: parse in a more robust manner than just split + replace
        spec = dict(elem.split('=') for elem in format.replace(' ', '').split(','))

        if not 'x' in spec or not 'y' in spec:
            raise ValueError("Graph needs both x and y axes to be plotted.")

        return Specifier().set_x(spec['x']).set_y(spec['y'])

