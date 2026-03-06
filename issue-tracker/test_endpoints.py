import urllib.request
import urllib.error
import json

base_url = "http://127.0.0.1:8000"
results = {}

def req(method, path, data=None, token=None):
    request = urllib.request.Request(base_url + path, method=method)
    if data:
        request.add_header("Content-Type", "application/json")
        request.data = json.dumps(data).encode("utf-8")
    if token:
        request.add_header("Authorization", f"Bearer {token}")
    try:
        resp = urllib.request.urlopen(request)
        return resp.getcode(), resp.read(), resp.headers
    except urllib.error.HTTPError as e:
        return e.code, e.read(), e.headers
    except Exception as e:
        return 0, str(e), {}

results["GET /"] = req("GET", "/")[0]
results["GET /health"] = req("GET", "/health")[0]
results["GET /users"] = req("GET", "/users")[0]
results["GET /projects"] = req("GET", "/projects")[0]
results["GET /projects/1/tickets"] = req("GET", "/projects/1/tickets")[0]

results["POST /auth/register"] = req("POST", "/auth/register", {"name":"Deploy Test Admin","email":"deployadmin@test.com","password":"deploypass1"})[0]
code, body, hdrs = req("POST", "/auth/login", {"email":"deployadmin@test.com","password":"deploypass1"})
results["POST /auth/login"] = code
token = json.loads(body).get("access_token") if code == 200 else ""

results["GET /auth/me"] = req("GET", "/auth/me", token=token)[0]

results["POST /projects (auth)"] = req("POST", "/projects", {"name":"Deploy Test Project","description":"Created during pre-deploy"}, token=token)[0]
results["POST /tickets (auth)"] = req("POST", "/projects/1/tickets", {"title":"Deploy Test Ticket","priority":"HIGH","type":"BUG"}, token=token)[0]
results["PATCH /tickets (auth)"] = req("PATCH", "/tickets/1", {"status":"IN_PROGRESS"}, token=token)[0]
results["DELETE /tickets (auth)"] = req("DELETE", "/tickets/1", token=token)[0]

results["POST /projects (no auth)"] = req("POST", "/projects", {"name":"Should Fail"})[0]
results["Wrong password -> 401"] = req("POST", "/auth/login", {"email":"deployadmin@test.com","password":"wrongpassword"})[0]

results["Short password -> 422"] = req("POST", "/auth/register", {"name":"Bad User","email":"bad@test.com","password":"short"})[0]
results["Pagination limit=500 -> 422"] = req("GET", "/users?limit=500")[0]

_, _, headers = req("GET", "/")
sec_headers = [h.lower() for h in headers.keys()]
# wait, .keys() gives title-cased keys in http.client.HTTPMessage, let's just make it lower.
results["headers_found"] = ", ".join([h for h in ["x-frame-options", "x-content-type-options", "cache-control"] if h in sec_headers])

print(json.dumps(results))
