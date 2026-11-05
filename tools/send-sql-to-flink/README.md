# Send SQL to Flink

Python tool to submit all SQL statements contained in files to Flink SQL gateway.

**Setup & Install**<br>
```sh
uv sync
```

**Run like**<br>
```
uv run send-sql-to-flink  --filepath myscript.sql
```

**Command details**<br>
```sh
usage: send-sql-to-flink [-h] --filepath PATH [--host HOST] [--port PORT] [--log-file PATH] [--log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}]

Submit a SQL script to a remote Flink SQL Gateway.

options:
  -h, --help            show this help message and exit
  --filepath PATH       Path to the SQL file to submit.

gateway:
  --host HOST           Flink SQL Gateway host. (default: localhost)
  --port PORT           Flink SQL Gateway port. (default: 8083)

logging:
  --log-file PATH       Append logs to this file. (default: .logs)
  --log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        Minimum log level to emit. (default: INFO)
```