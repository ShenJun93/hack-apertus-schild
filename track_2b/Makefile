.PHONY: run local test bench

# Starts Schild on http://localhost:8080 using the hosted Apertus endpoint from
# LLM_BASE_URL / LLM_API_KEY / LLM_NAME (exported in the shell or set in .env).
run:
	docker compose up --build

# Air-gapped setup: Apertus 1.5 8B runs in a local llama.cpp container.
# Needs models/apertus-v1.5-8b-text-q4_k_m.gguf (see docs/local-model.md).
local:
	docker compose -f docker-compose.yml -f docker-compose.local.yml up --build

test:
	docker compose run --rm --build app sh -c "pip install -q pytest && python -m pytest -q -p no:cacheprovider"

bench:
	docker compose run --rm --build app python -m bench.run
