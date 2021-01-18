import pytest
from typeguard import get_nested_type

# fmt:off
@pytest.mark.parametrize("data,expected",[
    # (["foo"],"typing.List[str]"),
    # (["foo",1],"typing.List[typing.Any]"),
    # ({"a":1,"b":"foo"},"typing.Dict[str,typing.Any]"),
    # ({"a":1,1.0:"foo"},"typing.Dict"),
    # ([{"a":1,"b":"foo"}, {"a":1,1.0:"foo"}], "typing.List[typing.Dict]"),

    ([{"foo":1.0},{"foo":1.0}],"typing.List[typing.Dict[str,float]]"),# TODO
    # (({"foo":1.0},{"foo":1.0}),"typing.Tuple[typing.Dict[str,float],typing.Dict[str,float]]"),
])
# fmt:on


def test_get_tested_type(data, expected):
    nested_type = get_nested_type(data)
    assert nested_type == expected
