run-front: create-env-file-if-not-exists
	uv run --env-file .env streamlit run app.py

create-env-file-if-not-exists:
	@if [ ! -f .env ]; then \
		echo "API_URL=http://localhost:8000" > .env; \
	fi
