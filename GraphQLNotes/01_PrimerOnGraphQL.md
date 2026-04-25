GraphQL allows an API consumer to request certain resources from the server without also receiving unnecessary data. This also reduces the change of unnecessary information disclosure unlike in badly designed REST applications.

Unlike in many REST applications where usually read operations happens through `GET`, creation happens with `POST`, update with `PUT` and deletion through `DELETE` in GraphQL -usually but not necessarily- all of these functionalities will happen through a `POST` request to a certain endpoint.

### GraphQL Schemas
A GraphQL schema represents the structure of the data that is being requested. An example GraphQL schema defining an `User` object can be written as following:
```
type User {
    id: Int
    username: String
    email: String
}
```

However GraphQL allows developers to link different types of objects with each other. LLets say we also have another object called `PaymentInfo` as following
```
type PaymentInfo {
   id: Int
   card_no: String
}
```

One can easily link both nodes by nesting one an another.

```
type User {
    id: Int
    username: String
    email: String
    payment_info: PaymentInfo
}
```

This means when requesting for an `User` object one can also query the associated payment information related to that specific user. This is known as an *one-way link relationship*. However reverse is in this case not necessarily true meaning one can not request the correlated `User` object just by querying a `PaymentInfo` object.

> There can be occurences of two-way link relationships if the developers specificaally also insert the `User` object into the `PaymentInfo` type schema. This often leads to Denial of Service (DoS) situations. More on that on later chapters.

Once the schema is defined the API consumer can interact with the entries in the database using **Queries**. There are 3 possible operations for interacting with the data

- `Queries` used for read only operations and do not modify the data.
- `Mutations` are used for data manipulation like create, update or delete.
- `Subscriptions` being an interesting one allowing real time communication with the application. They allow GraphQL to push data to the client when different events occur.

Before using the queries the developer must implement the schema. As an example
```
type Query {
  users: [User]
}

schema {
  query: Query
}

query {
   users {
        username
        email
   }
}
```

The `users` query will allow the consumer to receive all of the usernames and emails of the application.

An advantage of using GraphQL is performance. GraphQL improves the speed of client-server interactions by saving the client from having to make multiple requests in order to retrieve the complete set of data it needs from an application.

# Authentication and Authorization Flaws
One of the most common vulnerabilities that occur in the field of GraphQL is broken authentication and authorization. Authentication and authorization are complex security controls in any API technology. 


