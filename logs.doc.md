Logs management
===============

* Stored in ~/.intuition/logs/<session_id>.log
* Level is set with the `$LOG` environment variable (default: warning)
* Logs are structured in json events, with at least "event", "id" and
  "timestamp" fields. Others are optional and used by the application.
  Thoses events are indexed with recoreded time, source and debug level
