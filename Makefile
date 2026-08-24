.PHONY: run audit test dev-backend dev-frontend down

run:
	docker compose up --build

audit:
	cd backend && python3 cli.py

test:
	cd backend && python3 -m pytest tests/ -q

dev-backend:
	cd backend && uvicorn app.main:app --reload --port 8000

dev-frontend:
	cd frontend && npm run dev

down:
	docker compose down
