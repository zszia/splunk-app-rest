# Persistent REST handler examples

The persistent rest driver script distributed as part of the Splunk internal SDK simplifies marshaling of arguments. 
The handler receives all its arguments as a JSON string, which is convertible to a Python dictionary or a comparable 
map structure in other programming languages.

Depending on the restmap.conf parameters for the rest handler, however, certain attributes may be missing from the 
dictionary. The user and app context used to invoke the handler will also affect the available attributes.

## Contents
- [Basic usage](#basic)
- [Using data payloads](#payload)
- [Using query parameters](#query)
- [Using namespace context](#namespace)
- [Using user and namespace context](#user)
- [Invalid context errors](#invalid)
- [Persistent request payload format](#persistentrequest)
- [Persistent reply payload format](#persistentreply)

### <a name="basic"></a>Basic usage

Note that the "cookies" and "headers" attributes are enabled via the use of the "passCookies" and passHttpHeaders" 
restmap.conf parameters, respectively.

```
$ curl -s -k -u admin:changeme https://localhost:8089/services/echo_persistent | python -m json.tool
{
    "connection": {
        "listening_port": 8089,
        "src_ip": "127.0.0.1",
        "ssl": true
    },
    "cookies": [],
    "headers": [
        [
            "Authorization",
            "Basic NOTAREALTOKEN"
        ],
        [
            "User-Agent",
            "curl/7.29.0"
        ],
        [
            "Host",
            "localhost:8089"
        ],
        [
            "Accept",
            "*/*"
        ]
    ],
    "method": "GET",
    "output_mode": "xml",
    "output_mode_explicit": false,
    "query": [],
    "rest_path": "/echo_persistent",
    "restmap": {
        "conf": {
            "handler": "echo_persistent_handler.EchoHandler",
            "match": "/echo_persistent",
            "output_modes": "json",
            "passHttpCookies": "true",
            "passHttpHeaders": "true",
            "passPayload": "true",
            "requireAuthentication": "true",
            "script": "echo_persistent_handler.py",
            "scripttype": "persist"
        },
        "name": "script:echo"
    },
    "server": {
        "guid": "1B43291B-02C8-45C3-A9BD-72A9C9130EDD",
        "hostname": "host.domain.com",
        "rest_uri": "https://127.0.0.1:8089",
        "servername": "host.domain.com"
    },
    "session": {
        "authtoken": "NOTAREALTOKEN",
        "user": "admin"
    }
}
```

### <a name="payload"></a>Using data payloads

Passing a data argument converts the method to a HTTP POST, and adds the "form" attribute. Since we are also specifying 
"passPayload=true" in restmap.conf, the payload is also included in raw form in the "payload" attribute. Note that the 
contents of the "form" argument are passed as a list of pairs, and thus can be repeated, so it is important to account 
for repeated keys when converting the form arguments to a map or dictionary data structure.

```
$ curl -s -k -u admin:changeme https://localhost:8089/services/echo_persistent -d "abcd=EFGH" -d "ijkl=MNOP" | python -m json.tool
{
    "connection": {
        "listening_port": 8089,
        "src_ip": "127.0.0.1",
        "ssl": true
    },
    "cookies": [],
    "form": [
        [
            "abcd",
            "EFGH"
        ],
        [
            "ijkl",
            "MNOP"
        ]
    ],
    "headers": [
        [
            "Authorization",
            "Basic NOTAREALTOKEN"
        ],
        [
            "User-Agent",
            "curl/7.29.0"
        ],
        [
            "Host",
            "localhost:8089"
        ],
        [
            "Accept",
            "*/*"
        ],
        [
            "Content-Length",
            "19"
        ],
        [
            "Content-Type",
            "application/x-www-form-urlencoded"
        ]
    ],
    "method": "POST",
    "output_mode": "xml",
    "output_mode_explicit": false,
    "payload": "abcd=EFGH&ijkl=MNOP",
    "query": [],
    "rest_path": "/echo_persistent",
    "restmap": {
        "conf": {
            "handler": "echo_persistent_handler.EchoHandler",
            "match": "/echo_persistent",
            "output_modes": "json",
            "passHttpCookies": "true",
            "passHttpHeaders": "true",
            "passPayload": "true",
            "requireAuthentication": "true",
            "script": "echo_persistent_handler.py",
            "scripttype": "persist"
        },
        "name": "script:echo"
    },
    "server": {
        "guid": "1B43291B-02C8-45C3-A9BD-72A9C9130EDD",
        "hostname": "host.domain.com",
        "rest_uri": "https://127.0.0.1:8089",
        "servername": "host.domain.com"
    },
    "session": {
        "authtoken": "NOTAREALTOKEN",
        "user": "admin"
    }
}
```

### <a name="query"></a>Using query parameters
Key-value arguments in the HTTP query string will be passed as part of the "query" attribute. Like the "form" attribute,
"query" information is passed to the handler as a list of pairs. Thus it is possible for arguments to be repeated. 
This must be taken into account when crafting your REST handler: do  you prefer to receive multi-valued arguments in a 
special form such as comma-separated strings, or do you wish to allow the user to simply specify repeated arguments?

```
$ curl -s -k -u admin:changeme 'https://localhost:8089/services/echo_persistent?arg1=value1&arg2=value2&arg1=value1' | python -m json.tool
{
    "connection": {
        "listening_port": 8089,
        "src_ip": "127.0.0.1",
        "ssl": true
    },
    "cookies": [],
    "headers": [
        [
            "Authorization",
            "Basic NOTAREALTOKEN"
        ],
        [
            "User-Agent",
            "curl/7.29.0"
        ],
        [
            "Host",
            "localhost:8089"
        ],
        [
            "Accept",
            "*/*"
        ]
    ],
    "method": "GET",
    "output_mode": "xml",
    "output_mode_explicit": false,
    "query": [
        [
            "arg1",
            "value1"
        ],
        [
            "arg2",
            "value2"
        ],
        [
            "arg1",
            "value1"
        ]
    ],
    "rest_path": "/echo_persistent",
    "restmap": {
        "conf": {
            "handler": "echo_persistent_handler.EchoHandler",
            "match": "/echo_persistent",
            "output_modes": "json",
            "passHttpCookies": "true",
            "passHttpHeaders": "true",
            "passPayload": "true",
            "requireAuthentication": "true",
            "script": "echo_persistent_handler.py",
            "scripttype": "persist"
        },
        "name": "script:echo"
    },
    "server": {
        "guid": "1B43291B-02C8-45C3-A9BD-72A9C9130EDD",
        "hostname": "host.domain.com",
        "rest_uri": "https://127.0.0.1:8089",
        "servername": "host.domain.com"
    },
    "session": {
        "authtoken": "NOTAREALTOKEN",
        "user": "admin"
    }
}
```

### <a name="namespace"></a>Using namespace context

Making a request to the handler under a specific namespace context will result in the addition of the "ns" key to 
the argument dictionary. Note that the "user" is "-", which indicates the "wildcard" or "all apps" context.

```
$ curl -s -k -u admin:changeme https://localhost:8089/servicesNS/-/splunk-rest-examples/echo_persistent | python -m json.tool
{
    "connection": {
        "listening_port": 8089,
        "src_ip": "127.0.0.1",
        "ssl": true
    },
    "cookies": [],
    "headers": [
        [
            "Authorization",
            "Basic NOTAREALTOKEN"
        ],
        [
            "User-Agent",
            "curl/7.29.0"
        ],
        [
            "Host",
            "localhost:8089"
        ],
        [
            "Accept",
            "*/*"
        ]
    ],
    "method": "GET",
    "ns": {
        "app": "splunk-rest-examples"
    },
    "output_mode": "xml",
    "output_mode_explicit": false,
    "query": [],
    "rest_path": "/echo_persistent",
    "restmap": {
        "conf": {
            "handler": "echo_persistent_handler.EchoHandler",
            "match": "/echo_persistent",
            "output_modes": "json",
            "passHttpCookies": "true",
            "passHttpHeaders": "true",
            "passPayload": "true",
            "requireAuthentication": "true",
            "script": "echo_persistent_handler.py",
            "scripttype": "persist"
        },
        "name": "script:echo"
    },
    "server": {
        "guid": "1B43291B-02C8-45C3-A9BD-72A9C9130EDD",
        "hostname": "host.domain.com",
        "rest_uri": "https://127.0.0.1:8089",
        "servername": "host.domain.com"
    },
    "session": {
        "authtoken": "NOTAREALTOKEN",
        "user": "admin"
    }
}
```

### <a name="user"></a>Using user and namespace context

Adding a specific user to the context will result in the addition of the "user" to the ns" attribute of the argument 
dictionary.

```
$ curl -s -k -u admin:changeme https://localhost:8089/servicesNS/admin/splunk-rest-examples/echo_persistent | python -m json.tool
{
    "connection": {
        "listening_port": 8089,
        "src_ip": "127.0.0.1",
        "ssl": true
    },
    "cookies": [],
    "headers": [
        [
            "Authorization",
            "Basic NOTAREALTOKEN"
        ],
        [
            "User-Agent",
            "curl/7.29.0"
        ],
        [
            "Host",
            "localhost:8089"
        ],
        [
            "Accept",
            "*/*"
        ]
    ],
    "method": "GET",
    "ns": {
        "app": "splunk-rest-examples",
        "user": "admin"
    },
    "output_mode": "xml",
    "output_mode_explicit": false,
    "query": [],
    "rest_path": "/echo_persistent",
    "restmap": {
        "conf": {
            "handler": "echo_persistent_handler.EchoHandler",
            "match": "/echo_persistent",
            "output_modes": "json",
            "passHttpCookies": "true",
            "passHttpHeaders": "true",
            "passPayload": "true",
            "requireAuthentication": "true",
            "script": "echo_persistent_handler.py",
            "scripttype": "persist"
        },
        "name": "script:echo"
    },
    "server": {
        "guid": "1B43291B-02C8-45C3-A9BD-72A9C9130EDD",
        "hostname": "host.domain.com",
        "rest_uri": "https://127.0.0.1:8089",
        "servername": "host.domain.com"
    },
    "session": {
        "authtoken": "NOTAREALTOKEN",
        "user": "admin"
    }
}
```

### <a name="invalid"></a>Invalid context errors

However, trying to view objects in a nonexistent context will result in an error. Note that the error messages are NOT
JSON-formatted.

```
$ curl -s -k -u admin:changeme https://localhost:8089/servicesNS/NOSUCHUSER/splunk-rest-examples/echo_persistent
<?xml version="1.0" encoding="UTF-8"?>
<response>
  <messages>
    <msg type="ERROR">User does not exist: nosuchuser</msg>
  </messages>
</response>
```

HTTP status code should be used to determine whether or not a request succeeded:

```
$ curl -s -k -u admin:changeme -o /dev/null -w "%{http_code}\n" https://localhost:8089/servicesNS/NOSUCHUSER/splunk-rest-examples/echo_persistent
404
```


### <a name="persistentrequest"></a>Persistent Request Payload Format

The new-style persistent REST request format is documented below. This will be passed in to the handle() method's in_string 
parameter.

```
     {
       "output_mode" = "xml"|"json"|etc,
       "output_mode_explicit" = True/False,
       "server" = {
         "rest_uri" = "https://127.0.0.1:8089",
         "hostname" = "string",
         "servername" = "string",
         "guid" = "0000-...",
         "site" = "0"                 # only for multisite clustering
       },
       "system_authtoken" = "authtoken"       # missing if passSystemAuth=false
       "restmap" = { "name" = "...",  # missing if passConf=false
         "conf" = { "key": "value", ... }
       },
       "path_info": "part/after/match",       # Missing if there isn't any URL after restmap "match"
       "query" = [ [ "key", "value" ], ... ]  # "GET" args passed on the URL
       "connection" = {
         "src_ip" = "..."
         "ssl" = True/False
         "listening_port" = port#
         "listening_ip" = "..."     # missing if listening to all
       },
       "session" = {                  # missing if an un-authed call
         "user": "name",              # missing if no user context
         "authtoken": "token",        # missing if not logged in
         "tz": "US/Pacific",          # missing if user is in the system's default timezone
         "search_id": "search",       # present only if REST call from search process
         "embed": { "app": "X", "user": "Y", "object": "Z" }, # present only for anonymous embed requests
       },
       "rest_path" = "/...",          # part of the URI after the /services...
       "lang" = "en-US",              # for requests originating in the UI, the language from the URL
       "api_version" = "1.2.3",       # only present for REST requests that send an explicit version on URL
       "method" = "GET/etc",
       "ns" = {                       # missing if not namespaced (i.e. "/services" instead of "/servicesNS")
         "app": "search",             # missing if wildcarded app
         "user": "admin"              # missing if wildcarded user
       },
       "form" = [ [ "key", "value" ], ... ]   # POST args passed in the body (only if a POST/PUT)
       "headers" = [ [ "name", "value" ], ...]        # missing if passHttpHeaders=false
       "cookies" = [ [ "name", "value" ], ...]        # missing if passHttpCookies=false
       "payload" = "..."              # missing unless POST/PUT and non-empty
       "payload_base64" = "..."               # ...or if requested in restmap.conf we can send base64-encoded
     }
```

## <a name="persistentreply"></a>Persistent Request Reply Format

The new-style persistent REST reply format is documented below.

```
   {
      "status" = 200,         # Optional (200 is the default)
      "status" = [ 200, "Foo" ],      # ...or you can pass a status code and the explaination string
      "headers" = [           # Optional (add headers to result)
        [ "Name", "value" ]
      ],
      "headers" = { "Name": "value" } # ... or 'headers' can be an object
      "headers" = { "Name": [ "value1", "value2" ] } # ... and a single header can be set multiple times
      "cookies" = [           # Optional (send Add-Cookie headers)
        {
           "name": "foo",
           "value": "bar",
           "domain": domain,          # optional
           "path": path,              # optional
           "httponly": True/False,    # optional (defaults to true)
           "secure": True/False,      # optional (defaults to true if servicing an https request)
           "maxage": seconds,         # optional
        },
      ],
      "cookies" = { "foo": { ... } }  # ... or 'cookies' can be an object
      "cookies" = { "foo": "bar" }    # ... using a string instead of an object accepts all of the defaults
      "filename" = "foo.txt",         # Optional (send a Content-Disposition header to suggest browser should download)
      "log" = True/False,             # Optional (false will prevent transaction from going in splunkd_access.log)
      "payload" = "",                 # send the reply payload as a raw string
      "payload_base64" = "",          # ...or it's provided as a base64-encoded one
      "payload" = {obj} / [array],    # ...or it can be a JSON object (which implies that we should return a JSON content type)
      "payload" = Null,               # ...or we want to explicitly send nothing (implies status 204)
   }
```
