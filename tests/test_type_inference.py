import pytest
from typeguard import get_nested_type

# fmt:off
dict_str2any = {"str": 2, "an": "y"}
dict_any2any = {"any": 2, 1.0: "any"}
dict_str2float = {"str-to-float": 1.0}

class Bar:
    pass

class Bazz:
    pass

@pytest.mark.parametrize("data,expected",[
    (["foo"],"typing.List[str]"),
    (["foo",1],"typing.List[typing.Any]"),
    (dict_str2any, "typing.Dict[str,typing.Any]"),
    (dict_any2any, "typing.Dict[typing.Any]"),
    ([dict_str2any, dict_str2any], "typing.List[typing.Dict[str,typing.Any]]"),
    ([dict_str2any, dict_any2any], "typing.List[typing.Dict[typing.Any]"),
    ([dict_str2float, dict_str2float], "typing.List[typing.Dict[str,float]]"),
    ((dict_str2float, dict_str2float), "typing.Tuple[typing.Dict[str,float],typing.Dict[str,float]]"),
    ((1,2,3,4,5), "typing.Tuple[int,int,int,int,int]"),
    ((1,2,3,4,5,6), "typing.Tuple[int, ...]"),# tuple limit
    ((1,"foo",3,4,5,6), "typing.Tuple[typing.Any, ...]"),# tuple limit
    ({"a","b"}, "typing.Set[str]"),# tuple limit
    ([Bar(), Bazz()], "typing.List[typing.Any]"),
])
# fmt:on


def test_get_tested_type(data, expected):
    nested_type = get_nested_type(data)
    assert nested_type == expected
