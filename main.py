from fastapi import FastAPI, Security, Request
from fastapi.responses import JSONResponse
from starlette.middleware.sessions import SessionMiddleware
from utils import VerifyToken
from authlib.integrations.starlette_client import OAuth, OAuthError
from dotenv import find_dotenv, load_dotenv
from os import environ as env

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="secret-string")
app.secret_key = env.get("APP_SECRET_KEY")

oauth = OAuth()
oauth.register(
    name = "auth0",
    client_id=env.get("AUTH0_CLIENT_ID"),
    client_secret=env.get("AUTH0_CLIENT_SECRET"),
    client_kwargs={
        "scope": "openid profile email",
    },
    authorize_params={'audience': env.get("AUTH0_AUDIENCE")},
    server_metadata_url=f'https://{env.get("AUTH0_DOMAIN")}/.well-known/openid-configuration',
)

verify_auth = VerifyToken()

@app.get("/login")
async def login(request:Request):
    redirect_uri = request.url_for('auth')
    return await oauth.auth0.authorize_redirect(request, redirect_uri)

@app.get('/auth')
async def auth(request: Request):
    try:        
        access_token = await oauth.auth0.authorize_access_token(request)
    except OAuthError as error:
        return JSONResponse(status_code=403, content={"message": "Forbidden"})
    
    try:
        access_token = access_token['access_token']
        return JSONResponse(status_code=200, content=access_token)
    except KeyError:
        return JSONResponse(status_code=403, content={"message": "Forbidden"})

@app.get("/api/public")
def public():
    """No access token required to access this route"""

    result = {
        "status": "success",
        "msg": ("Hello from a public endpoint! You don't need to be "
                "authenticated to see this.")
    }
    return result

@app.get("/api/private")
def private(auth_result: str = Security(verify_auth.verify)):
    """A valid access token is required to access this route"""
    return auth_result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000)