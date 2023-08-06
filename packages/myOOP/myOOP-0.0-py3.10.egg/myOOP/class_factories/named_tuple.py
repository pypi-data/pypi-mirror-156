from typing import Any, Iterable
from keyword import iskeyword


def named_tuple(typename: str, field_names: str | Iterable[str]) -> type:
    """Returns a new subscriptable class with named fields.
    """

    # Convert str or Iterable into list.
    if isinstance(field_names, str):
        field_names = field_names.replace(',', ' ').split()
    if not isinstance(field_names, Iterable):
        field_names = (field_names, )
    field_names = list(field_names)

    # Validate the field names.
    for name in [typename] + field_names:
        if type(name) is not str:
            raise TypeError('Type names and field names must be strings')
        if not name.isidentifier():
            raise ValueError(
                f'Type names and field names must be valid identifiers: '
                f'{name!r}')
        if iskeyword(name):
            raise ValueError(
                f'Type names and field names cannot be a keyword: {name!r}')
        if name.startswith('_'):
            raise ValueError(
                f'Field names cannot start with an underscore: {name!r}')

    # Refuse repeated feild names.
    seen = set()
    for name in field_names:
        if name in seen:
            raise ValueError(f'Encountered duplicate field name: {name!r}')
        seen.add(name)

    class nt:
        map = field_names

        __doc__ = f"{typename}({', '.join(field_names)})"

        def __init__(self, *args, **kwargs):
            cur_pos = 0
            for arg in args:
                if cur_pos >= len(field_names):
                    raise ValueError(f'Expected {len(field_names)} arguments,'
                                     f'got {len(args)} (too many).')
                self[cur_pos] = arg
                cur_pos += 1
            for kwarg in kwargs:
                self[kwarg] = kwargs[kwarg]

        def __getitem__(self, key):
            if isinstance(key, int):
                if key >= len(field_names):
                    raise IndexError("Index out of range.")
                return self[self.map[key]]
            elif isinstance(key, str):
                return getattr(self, key)
            else:
                raise TypeError("Expected type 'str' or 'int',"
                                f"got {type(key).__name__.__repr__()}")

        def __setitem__(self, key, value):
            if isinstance(key, int):
                if key >= len(field_names):
                    raise IndexError("Index out of range.")
                self[self.map[key]] = value
            elif isinstance(key, str):
                setattr(self, key, value)
            else:
                raise TypeError("Expected type 'str' or 'int',"
                                f"got {type(key).__name__.__repr__()}")

        def __setattr__(self, name: str, value: Any) -> None:
            if name in field_names:
                super().__setattr__(name, value)
            else:
                raise AttributeError(
                    f"{typename.__repr__()} object has no "
                    f"attribute {name.__repr__()}")

        def __str__(self) -> str:
            string = typename + "("
            for key in field_names:
                string += key
                string += "="
                string += str(getattr(self, key))
                string += ", "
            string = string[:-2] + ")"
            return string

        __repr__ = __str__

        def asdict(self) -> dict[str, Any]:
            result = {}
            for key in field_names:
                result[key] = getattr(self, key)
            return result

        def astuple(self) -> tuple:
            result = []
            for key in field_names:
                result.append(getattr(self, key))
            return tuple(result)

        def replace(self, /, **kwargs) -> None:
            for key in kwargs:
                setattr(self, key, kwargs[key])

    nt.__name__ = typename

    return nt
