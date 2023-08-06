# querulous_quarrel

Named for a lovely groups of sparrows that happened to be flying by.  A library
that makes writing and executing queries a little easier for data scientists.

`quarrel` uses `concentric` and `waddle` and is proudly sponsored by the m&a
team at cscgh.

## installation

```
cd /path/to/repo
pip install quarrel
```

## usage

1. create a config file

        oracle:
          host: oracle.example.com
          user: scott
          password: tiger
          sid: xe

2. prepare a connection manager

        from concentric.managers import CachingConnectionManager as ccm

        ccm.get_instance('/path/to/oracle.yml')

3. query the database

        from quarrel.raw import query
        results = query('oracle', 'select sysdate from dual')
