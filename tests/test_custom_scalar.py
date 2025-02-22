import base64
from typing import NewType

import strawberry
from graphql import graphql_sync


Base64Encoded = strawberry.scalar(
    NewType("Base64Encoded", bytes),
    serialize=base64.b64encode,
    parse_value=base64.b64decode,
)


@strawberry.scalar(serialize=lambda x: 42, parse_value=lambda x: Always42())
class Always42:
    pass


MyStr = strawberry.scalar(NewType("MyStr", str))


def test_custom_scalar_serialization():
    @strawberry.type
    class Query:
        @strawberry.field
        def custom_scalar_field(self, info) -> Base64Encoded:
            return Base64Encoded(b"decoded value")

    schema = strawberry.Schema(Query)

    result = graphql_sync(schema, "{ customScalarField }")

    assert not result.errors
    assert base64.b64decode(result.data["customScalarField"]) == b"decoded value"


def test_custom_scalar_deserialization():
    @strawberry.type
    class Query:
        @strawberry.field
        def decode_base64(self, info, encoded: Base64Encoded) -> str:
            return bytes(encoded).decode("ascii")

    schema = strawberry.Schema(Query)

    encoded = Base64Encoded(base64.b64encode(b"decoded"))
    query = """query decode($encoded: Base64Encoded!) {
        decodeBase64(encoded: $encoded)
    }"""
    result = graphql_sync(schema, query, variable_values={"encoded": encoded})

    assert not result.errors
    assert result.data["decodeBase64"] == "decoded"


def test_custom_scalar_decorated_class():
    @strawberry.type
    class Query:
        @strawberry.field
        def answer(self, info) -> Always42:
            return Always42()

    schema = strawberry.Schema(Query)

    result = graphql_sync(schema, "{ answer }")

    assert not result.errors
    assert result.data["answer"] == 42


def test_custom_scalar_default_serialization():
    @strawberry.type
    class Query:
        @strawberry.field
        def my_str(self, info, arg: MyStr) -> MyStr:
            return MyStr(str(arg) + "Suffix")

    schema = strawberry.Schema(Query)

    result = graphql_sync(schema, '{ myStr(arg: "value") }')

    assert not result.errors
    assert result.data["myStr"] == "valueSuffix"
