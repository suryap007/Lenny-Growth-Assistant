.PHONY: backend frontend ingest test

backend:
	cd backend && uvicorn app.main:app --reload --port 8000

frontend:
	cd frontend && npm run dev

ingest:
	cd backend && python -m scripts.ingest_lenny

test:
	cd backend && pytest
