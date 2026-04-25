---

---
# GraphQL Overview

## Example Queries

- Example query

```javascript
    query {
        products {
            id
            name
            listed
        }
    }
```

- Example query through get request

```javascript
    /graphql?query=mutation+%7B%0A%09deleteOrganizationUser%28input%3A%7Bid%3A+3%7D%29+%7B%0A%09%09user+%7B%0A%09%09%09id%0A%09%09%7D%0A%09%7D%0A%7D
```

- Example query with a variable

```javascript
    query {
        product(id: 3) {
            id
            name
            listed
        }
    }
```

- Probing for introspection

```javascript
    {
        "query": "{__schema{queryType{name}}}"
    }
```

## **Bypassing GraphQL introspection defenses
**

> [!note]+ Use characters like spaces, new lines and commas ignored by the GraphQL but not by the flawed regex


```javascript
    GET /graphql?query=query%7B__schema%0A%7BqueryType%7Bname%7D%7D%7D
```
