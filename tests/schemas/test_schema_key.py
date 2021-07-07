import typing
import pytest
from functools import partial
from dataclasses import dataclass
from dataclasses_avroschema import AvroModel


def test_key__str():
    @dataclass
    class UserWithStrId(AvroModel):
        _id: str

        class Meta:
            key = "_id"

    user = UserWithStrId.fake()
    assert user.key == user._id.encode()


def test_key__bytes():
    @dataclass
    class UserWithBytesId(AvroModel):
        _id: bytes

        class Meta:
            key = "_id"

    user = UserWithBytesId.fake()
    assert user.key == user._id


def test_key__custom_serializer():
    def wire_format_serializer(key: str, version: int) -> bytes:
        return b"\0" + version.to_bytes(4, byteorder="big") + key.encode()

    @dataclass
    class UserWithCustomId(AvroModel):
        _id: str

        class Meta:
            key = "_id"
            key_serializer = partial(wire_format_serializer, version=42)

    user = UserWithCustomId.fake()

    assert user.key == wire_format_serializer(user._id, 42)


def test_key__invalid():
    @dataclass
    class UserWithInvalidId(AvroModel):
        some_id: str

        class Meta:
            key = "invalid_id"

    with pytest.raises(RuntimeError) as exc_info:
        user = UserWithInvalidId.fake()
        user.key

    assert exc_info.value.args[0] == "There is no field with name invalid_id!"


def test_key__unknown_type():
    @dataclass
    class UserWithComplexIdType(AvroModel):
        complex_id: typing.List[int]

        class Meta:
            key = "complex_id"

    with pytest.raises(RuntimeError) as exc_info:
        user = UserWithComplexIdType.fake()
        user.key

    assert exc_info.value.args[0] == f"I don't know how to encode the key for complex_id of type <class 'list'>!"


def test_key__not_implemented():
    @dataclass
    class UserWithoutKey(AvroModel):
        some_id: str

    with pytest.raises(NotImplementedError) as exc_info:
        user = UserWithoutKey.fake()
        user.key

    assert exc_info.value.args[0] == "`key` attribute is not specified! You can declare it via a Meta class attribute"
