import inspect
import unittest
from typing import Optional

from graphql import GraphQLList, OperationDefinitionNode, build_ast_schema, parse

from gql_compiler import renderer
from gql_compiler.parser import ParsedQuery, Parser


def get_parsed_query(query_str: str, schema_str: Optional[str] = None) -> ParsedQuery:
    if schema_str is None:
        schema_str = """
        enum Episode {
            NEWHOPE
            EMPIRE
            JEDI
        }
        input SubInput {
            age: Int
        }
        input AddInput {
            name: String!
            sub: SubInput
        }
        type A {
            id: ID!
            name: String
            episode: Episode!
            llll: [[[[String]]]]
            r: SearchResult
        }
        union SearchResult = Human | Droid | Starship

        interface Character {
            id: ID!
            name: String!
            appearsIn: [Episode!]!
            bestFriend: Character
            friends: [Character]
        }
        type Human implements Character {
            id: ID!
            name: String!
            appearsIn: [Episode!]!
            bestFriend: Character
            friends: [Character]
            totalCredits: Int!
            starshipIds: [ID!]!
            starships: [Starship]
        }
        type Droid implements Character {
            id: ID!
            name: String!
            appearsIn: [Episode!]!
            bestFriend: Character
            friends: [Character]
            primaryFunction: String!
        }

        type Starship {
            id: ID!
            name: String!
        }

        type Query {
            hello: String!
            a(id: ID!): A
            a2(llll: [[[[String]]]]): A
            hero: Character
        }
        type Mutation {
            add(input: AddInput!): A
        }
        type Subscription {
            count(target: Int!): String
        }
        """

    schema = build_ast_schema(parse(schema_str))
    parsed_query = parse(query_str)
    query = parsed_query.definitions[0]
    assert isinstance(query, OperationDefinitionNode)
    parser = Parser(schema)
    return parser.parse(query)


class Test(unittest.TestCase):
    def test_code_chunk(self):
        cc = renderer.CodeChunk()
        cc.write("a")
        line_index = cc.tell()
        with cc.write_block("b"):
            cc.write_lines(["c"])
        cc.insert(line_index, ["d"])
        self.assertEqual(
            str(cc),
            inspect.cleandoc(
                """
                a
                d
                b
                    c
                """
            ),
        )

    def test_render(self):
        parsed_query = get_parsed_query(
            """
            query Q {
                hero {
                    __typename
                    name
                    appearsIn
                    bestFriend {
                        name
                    }
                    friends {
                        __typename
                        ... on Human {
                            name
                        }
                        ... on Droid {
                            primaryFunction
                        }
                    }
                }
            }
            """
        )

        r = renderer.Renderer()
        r.render([parsed_query])

        r = renderer.Renderer(render_as_typed_dict=True)
        r.render([parsed_query])

    def test_get_query_body(self):
        parsed_query = get_parsed_query(
            """
            # comment
            query Q {
                hello
            }
            # other-comment
            """
        )

        r = renderer.Renderer()
        body = r.get_query_body(parsed_query)
        self.assertEqual(
            body,
            """query Q {
                hello
            }""",
        )

    def test_render_enum(self):
        parsed_query = get_parsed_query(
            """
            query Q($id: ID!) {
                a(id: $id) {
                    episode
                }
            }
            """
        )

        b = renderer.CodeChunk()
        r = renderer.Renderer()
        r.render_enum(b, "Episode", parsed_query.used_enums["Episode"])
        self.assertEqual(str(b), 'Episode = typing.Literal["NEWHOPE", "EMPIRE", "JEDI"]')

    def test_render_input(self):
        parsed_query = get_parsed_query(
            """
            mutation M($input: AddInput!) {
                add(input: $input) {
                    name
                }
            }
            """
        )
        b = renderer.CodeChunk()
        r = renderer.Renderer()
        r.render_input(b, "SubInput", parsed_query.used_input_types["SubInput"])
        r.render_input(b, "AddInput", parsed_query.used_input_types["AddInput"])

        self.assertEqual(
            str(b).strip(),
            inspect.cleandoc(
                """
                SubInput__required = typing.TypedDict("SubInput__required", {})
                SubInput__not_required = typing.TypedDict("SubInput__not_required", {"age": typing.Optional[int]}, total=False)


                class SubInput(SubInput__required, SubInput__not_required):
                    pass


                AddInput__required = typing.TypedDict("AddInput__required", {"name": str})
                AddInput__not_required = typing.TypedDict("AddInput__not_required", {"sub": typing.Optional[SubInput]}, total=False)


                class AddInput(AddInput__required, AddInput__not_required):
                    pass
                """  # noqa
            ),
        )

    def test_get_field_type_mapping(self):
        parsed_query = get_parsed_query(
            """
            query Q {
                hero {
                    __typename
                    ... on Human {
                        friends {
                            __typename
                            ... on Human {
                                name
                            }
                            ... on Droid {
                                primaryFunction
                            }
                        }
                    }
                }
            }
            """
        )

        r = renderer.Renderer()
        m = r.get_field_type_mapping(parsed_query.fields["hero"], parsed_query)
        # {'__typename': (
        #     <GraphQLNonNull <GraphQLScalarType 'String'>>, 'typing.Literal["Character", "Droid"]')}
        self.assertEqual(m["__typename"][1], 'typing.Literal["Character", "Droid"]')

        m = r.get_field_type_mapping(parsed_query.fields["hero"].inline_fragments["Human"], parsed_query)
        # {'__typename': (<GraphQLNonNull <GraphQLScalarType 'String'>>, 'typing.Literal["Human"]'),
        #  'friends': (<GraphQLList <GraphQLInterfaceType 'Q__hero__Human__friends'>>,
        #              'typing.List[typing.Optional[Q__hero__Human__friends]]')}
        self.assertEqual(m["__typename"][1], 'typing.Literal["Human"]')
        self.assertEqual(m["friends"][1], "typing.List[typing.Optional[Q__hero__Human__friends]]")
        self.assertTrue(isinstance(m["friends"][0], GraphQLList))

    def test_is_scalar_type(self):
        parsed_query = get_parsed_query(
            """
            query Q {
                hero {
                    name
                    appearsIn
                }
            }
            """
        )

        r = renderer.Renderer()
        self.assertFalse(r.is_scalar_type(parsed_query.fields["hero"].type))
        self.assertTrue(r.is_scalar_type(parsed_query.fields["hero"].fields["name"].type))
        self.assertTrue(r.is_scalar_type(parsed_query.fields["hero"].fields["appearsIn"].type))

    def test_get_assign_field_str(self):
        parsed_query = get_parsed_query(
            """
            query Q {
                hero {
                    name
                    friends {
                        name
                    }
                }
            }
            """
        )

        converter = renderer.DefaultAssignConverter()
        r = renderer.Renderer()
        b = renderer.CodeChunk()
        assign = r.get_assign_field_str(b, "name", parsed_query.fields["hero"].fields["name"].type, converter)
        self.assertEqual(assign, "name")

        converter = renderer.ObjectAssignConverter(field_type_str="Friend")
        assign = r.get_assign_field_str(
            b, "friends", parsed_query.fields["hero"].fields["friends"].type, converter
        )
        self.assertEqual(
            assign,
            "[Friend(**rewrite_typename(friends__iter))"
            " if friends__iter else None for friends__iter in friends]",
        )

    def test_render_class(self):
        parsed_query = get_parsed_query(
            """
            query Q {
                hero {
                    __typename
                    name
                    bestFriend {
                        name
                    }
                    friends {
                        __typename
                        ... on Human {
                            name
                        }
                        ... on Droid {
                            primaryFunction
                        }
                    }
                }
            }
            """
        )

        r = renderer.Renderer()
        b = renderer.CodeChunk()
        r.render_class(b, "Hero", parsed_query.fields["hero"], parsed_query)

        self.assertEqual(
            str(b).strip(),
            inspect.cleandoc(
                """
                @dataclass
                class Hero:
                    name: str
                    bestFriend: typing.Optional[Q__hero__bestFriend]
                    friends: typing.List[typing.Optional[Q__hero__friends]]
                    _typename: typing.Literal["Character", "Droid", "Human"]
                    def __init__(self, name, bestFriend, friends, _typename):
                        self.name = name
                        self.bestFriend = Q__hero__bestFriend(**rewrite_typename(bestFriend)) if bestFriend else None
                        __friends_map = {
                            "Human": Q__hero__friends__Human,
                            "Droid": Q__hero__friends__Droid,
                        }
                        self.friends = [__friends_map.get(friends__iter["__typename"], Q__hero__friends)(**rewrite_typename(friends__iter)) if friends__iter else None for friends__iter in friends]
                        self._typename = _typename
                """  # noqa
            ),
        )

    def test_render_typed_dict(self):
        parsed_query = get_parsed_query(
            """
            query Q {
                hero {
                    __typename
                    name
                    bestFriend {
                        name
                    }
                    friends {
                        __typename
                        ... on Human {
                            name
                        }
                        ... on Droid {
                            primaryFunction
                        }
                    }
                }
            }
            """
        )

        r = renderer.Renderer(render_as_typed_dict=True)
        b = renderer.CodeChunk()
        r.render_typed_dict(b, "Hero", parsed_query.fields["hero"], parsed_query)
        self.assertEqual(
            str(b).strip(),
            'Hero = typing.TypedDict("Hero", {"__typename": typing.Literal["Character", "Droid", "Human"], '
            '"name": str, "bestFriend": typing.Optional[Q__hero__bestFriend], '
            '"friends": typing.List[typing.Optional[Q__hero__friends]]})',
        )

        b = renderer.CodeChunk()
        r.render_typed_dict(
            b, "Q__hero__friends", parsed_query.fields["hero"].fields["friends"], parsed_query
        )
        self.assertEqual(
            str(b).strip(),
            inspect.cleandoc(
                """
                __Q__hero__friends = typing.TypedDict("__Q__hero__friends", {"__typename": typing.Literal["Character"]})
                Q__hero__friends = typing.Union[__Q__hero__friends, Q__hero__friends__Human, Q__hero__friends__Droid]
                """  # noqa
            ),
        )

    def test_type_to_string(self):
        parsed_query = get_parsed_query(
            """
            query Q {
                a(id: "id") {
                    id llll r
                }
            }
            """
        )

        r = renderer.Renderer()
        self.assertEqual(r.type_to_string(parsed_query.fields["a"].fields["id"].type), "str")
        self.assertEqual(
            r.type_to_string(parsed_query.fields["a"].fields["llll"].type),
            "typing.List[typing.List[typing.List[typing.List[typing.Optional[str]]]]]",
        )
        self.assertEqual(
            r.type_to_string(parsed_query.fields["a"].fields["r"].type), "typing.Optional[Q__a__r]"
        )

    def test_node_type_to_string(self):
        parsed_query = get_parsed_query(
            """
            query Q($id: ID!, $llll: [[[[String]]]]) {
                a(id: $id) {
                    id name
                }
                a2(llll: $llll) {
                    id name
                }
            }
            """
        )

        r = renderer.Renderer()
        self.assertEqual(r.node_type_to_string(parsed_query.variable_map["id"].type_node), "str")
        self.assertEqual(
            r.node_type_to_string(parsed_query.variable_map["llll"].type_node),
            "typing.List[typing.List[typing.List[typing.List[typing.Optional[str]]]]]",
        )

    def test_render_variable_type(self):
        parsed_query = get_parsed_query(
            """
            query Q($id: ID!, $llll: [[[[String]]]]) {
                a(id: $id) {
                    id name
                }
                a2(llll: $llll) {
                    id name
                }
            }
            """
        )

        r = renderer.Renderer()
        b = renderer.CodeChunk()
        r.render_variable_type(b, "V", parsed_query.variable_map)

        self.assertEqual(
            str(b).strip(),
            inspect.cleandoc(
                """
                V__required = typing.TypedDict("V__required", {"id": str})
                V__not_required = typing.TypedDict("V__not_required", {"llll": typing.List[typing.List[typing.List[typing.List[typing.Optional[str]]]]]}, total=False)


                class V(V__required, V__not_required):
                    pass
                """  # noqa
            ),
        )

    def test_write_execute_method(self):
        parsed_query = get_parsed_query(
            """
            query Q($id: ID!) {
                a(id: $id) {
                    id name
                }
            }
            """
        )

        r = renderer.Renderer()
        b = renderer.CodeChunk()
        r.write_execute_method(b, parsed_query, False)
        self.assertEqual(
            str(b),
            inspect.cleandoc(
                """
                @classmethod
                def execute(cls, client: Client, variable_values: _QInput) -> QResponse:
                    return cls.Response(**rewrite_typename(client.execute(  # type: ignore
                        cls._query, variable_values=variable_values
                    )))
                """
            ),
        )

        b = renderer.CodeChunk()
        r.write_execute_method(b, parsed_query, True)
        self.assertEqual(
            str(b),
            inspect.cleandoc(
                """
                @classmethod
                async def execute_async(cls, client: Client, variable_values: _QInput) -> QResponse:
                    return cls.Response(**rewrite_typename(await client.execute_async(  # type: ignore
                        cls._query, variable_values=variable_values
                    )))
                """
            ),
        )

    def test_write_subscribe_method(self):
        parsed_query = get_parsed_query(
            """
            subscription ($t: Int!) {
                count(target: $t)
            }
            """
        )

        r = renderer.Renderer()
        b = renderer.CodeChunk()
        r.write_subscribe_method(b, parsed_query, False)
        self.assertEqual(
            str(b),
            inspect.cleandoc(
                """
                @classmethod
                def subscribe(cls, client: Client, variable_values: _Input) -> typing.Iterable[Response]:
                    for r in client.subscribe(cls._query, variable_values=variable_values):
                        yield cls.Response(**rewrite_typename(r))  # type: ignore
                """
            ),
        )

        b = renderer.CodeChunk()
        r.write_subscribe_method(b, parsed_query, True)
        self.assertEqual(
            str(b),
            inspect.cleandoc(
                """
                @classmethod
                async def subscribe_async(cls, client: Client, variable_values: _Input) -> typing.AsyncIterable[Response]:
                    async for r in client.subscribe_async(cls._query, variable_values=variable_values):
                        yield cls.Response(**rewrite_typename(r))  # type: ignore
                """  # noqa
            ),
        )

    def test_write_file_header(self):
        b = renderer.CodeChunk()
        r = renderer.Renderer()
        r.write_file_header(b)
