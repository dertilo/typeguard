import pytest
from typeguard import get_nested_type

@pytest.mark.parametrize("data,expected",[
    (["foo"],"typing.List[str]"),
    (["foo",1],"typing.List[typing.Any]"),
    ([{"foo":1.0},{"foo":1.0}],"typing.List[typing.Dict[str,float]]"),
    (({"foo":1.0},{"foo":1.0}),"typing.Tuple[typing.Dict[str,float],typing.Dict[str,float]]")
])
def test_get_tested_type(data, expected):
    nested_type = get_nested_type(data)
    assert nested_type == expected
