# python type file generator for graphql-python/gql

# Features
- scalar/custom scalar
- enum
- union
- inline fragment
- fragment not supported yet

# Command

``` shell
usage: main.py [-h] [-s SCHEMA [SCHEMA ...]] [-q QUERY [QUERY ...]] [--config CONFIG]

options:
  -h, --help            show this help message and exit
  -s SCHEMA [SCHEMA ...], --schema SCHEMA [SCHEMA ...]
                        the graphql schemas storage path or url
  -q QUERY [QUERY ...], --query QUERY [QUERY ...]
                        path where query file or directory all queries files are stored
  --config CONFIG       path where config yaml file
```

## config-file
``` yaml
output_path: "{dirname}/__generated__/{basename_without_ext}.py"
scalar_map:
  ID:
    import: ""
    value: "str"
query_ext: "gql"
```

### output_path
determine output file depends on source query file

### scalar_map
custom scalar type mapping

``` yaml
"<Custom Scalar name>":
  import: "import <import path>"  # import file when use this type
  value: "<scalar type in python code>"
```

### query_ext
searched by this extension name

# Usage
## create query graphql file

``` graphql
# schema.graphql
type Query {
  hello: String!
}
```

``` graphql
# example.graphql
query Hello {
  hello
}
```
## run generate command
``` shell
python main.py -s schema.graphql -q example.graphql
```

## check generated file
``` python
# example.py
# @generated AUTOGENERATED file. Do not Change!

import typing
from gql import gql, Client

GetScalarInput__required = typing.TypedDict("GetScalarInput__required", {})
GetScalarInput__not_required = typing.TypedDict("GetScalarInput__not_required", {}, total=False)


class GetScalarInput(GetScalarInput__required, GetScalarInput__not_required):
    pass


class GetScalar:
    _query = gql('''
        query GetScalar {
          hello
        }
    ''')
    @classmethod
    def execute(cls, client: Client, variable_values: GetScalarInput = {}) -> GetScalarResponse:
        return client.execute(  # type: ignore
            cls._query, variable_values=variable_values
        )
    @classmethod
    def execute_async(cls, client: Client, variable_values: GetScalarInput = {}) -> GetScalarResponse:
        return client.execute_async(  # type: ignore
            cls._query, variable_values=variable_values
        )

```
## run query

``` python
from gql import Client
from gql.transport.aiohttp import AIOHTTPTransport

transport = AIOHTTPTransport(url="http://localhost:8000")
client = Client(transport=transport, fetch_schema_from_transport=True, parse_results=True)

result0 = client_queries.GetScalar.execute(client)
assert result0 == {"hello": "hello world"}
```

## mutation

``` graphql
mutation AddStarship($input: AddStarshipInput!) {
  addStarship(input: $input) {
    id name
  }
}

```

``` python
client_queries.AddStarship.execute(client, {'input': {'name': 'HOGE'}})
```

## subscription
``` graphql
subscription AllHuman {
  allHuman {
    id name
  }
}

```

``` python
# ----- sync call -----
transport = WebsocketsTransport(url='ws://localhost:8000')
client = Client(transport=transport, schema=schema)  # fetch_schema_from_transportには対応していない
result8 = [x for x in client_queries.AllHuman.subscribe(client)]
assert result8 == [{'allHuman': {'id': 'h-1', 'name': 'luke'}}, {'allHuman': {'id': 'h-2', 'name': 'obi'}}]

# ----- async call -----
async def async_subscription_test():
    transport = WebsocketsTransport(url='ws://localhost:8000')
    client = Client(transport=transport, schema=schema)
    result8 = [x async for x in client_queries.AllHuman.subscribe_async(client)]
    assert result8 == (
        [{'allHuman': {'id': 'h-1', 'name': 'luke'}}, {'allHuman': {'id': 'h-2', 'name': 'obi'}}])

asyncio.run(async_subscription_test())

```



# Example
## generate type file
``` shell
# install required packages
poetry install

# run example server
python -m strawberry server example.server:schema

# @another shell
python main.py -s http://localhost:8000 -q ./example/client_queries.graphql
```
This command generates `example/client_queries.py`.

``` shell
python example/run_client.py 
```

## run with docker

``` shell
docker run --rm -t -i --user=`id -u`:`id -g` -v `pwd`:/app --network=host s1s5/python-gql-compiler -s http://localhost:8000 -q ./example/client_queries.graphql
```


## License

[MIT License](https://github.com/s1s5/python-gql-compiler/blob/master/LICENSE)
