import alembic.config
import os

# Minimal script to run alembic if needed.
# Since the prompt requires alembic migrations to be provided, 
# I will create the basic structure. The actual running will be via `alembic upgrade head`.

# alembic.ini content
ALEMBIC_INI = """
[alembic]
script_location = alembic
sqlalchemy.url = postgresql+asyncpg://postgres:postgres@localhost:5432/postgres

[post_write_hooks]

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
"""

if not os.path.exists("alembic.ini"):
    with open("alembic.ini", "w") as f:
        f.write(ALEMBIC_INI)
