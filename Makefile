UV := $(or \
	$(wildcard .venv/bin/uv), \
	$(shell which uv 2>/dev/null), \
	$(HOME)/.local/bin/uv \
)
ALEMBIC = $(UV) run alembic

migrations-init:
	$(ALEMBIC) init migrations

migrations-create:
	$(ALEMBIC) revision --autogenerate -m "$(message)"

migrations-upgrade:
	$(ALEMBIC) upgrade head

migrations-downgrade:
	$(ALEMBIC) downgrade -1