from fastapi import FastAPI
import api
from crud import create_db

# command to start the API server
# uvicorn main:app --workers 4
# SWAGGER DOCS: http://127.0.0.1:8004/docs


app = FastAPI()

create_db()

# include routes from api
app.include_router(api.app)
