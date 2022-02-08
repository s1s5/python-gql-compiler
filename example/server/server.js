var express = require('express');
var { graphqlHTTP } = require('express-graphql');
var { buildSchema } = require('graphql');

// Construct a schema, using GraphQL schema language
var schema = buildSchema(`
scalar Date

  type Author {
  id: Int!
  firstName: String!
  lastName: String!
  posts(findTitle: String): [Post]
}

type Post {
  id: Int!
  title: String!
  author: Author
f: Float
d: Date
}

enum SpanKind {
  DAILY
  MONTHLY
}

type Query {
  hello: String
  posts(slugList: [ID!], kind: SpanKind): [Post]
}
`);

// The root provides a resolver function for each API endpoint
var root = {
    hello: () => {
        return 'Hello world!';
    },
    posts: (args) => {
        console.log(args.slugList);
        return [{
            id: 9, title: "post-title", f: 0.9, d: '2022-01-01',
        }];
    }
};

var app = express();
app.use('/graphql', graphqlHTTP({
    schema: schema,
    rootValue: root,
    graphiql: true,
}));
app.listen(4000);
console.log('Running a GraphQL API server at http://localhost:4000/graphql');
