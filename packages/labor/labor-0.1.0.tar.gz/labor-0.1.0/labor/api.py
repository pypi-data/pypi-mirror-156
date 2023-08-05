import httpx
import json
import config
from date_utils import get_last_day_of_month

BASE_URL = "https://api.getlabor.com.br/"

def update_header_interceptor(logged_user, headers):
    if not headers['access-token']: return
    logged_user["saved_headers"] = {
        'access-token': headers['access-token'],
        'client': headers['client'],
        'expiry': headers['expiry'],
        'uid': headers['uid'],
        'token-type': headers['token-type']
    }
    config.write(logged_user)

def _request(url, logged_user):
    headers = logged_user["saved_headers"]
    res = httpx.get(url, headers=headers)
    update_header_interceptor(logged_user, res.headers)
    return res

def sign_in(email, password):
    url = BASE_URL + "auth/sign_in"
    res = httpx.post(url, json={"email": email, "password": password})
    return json.loads(res.text)['data'], res.status_code, res.headers

def sign_out(headers):
    url = BASE_URL + "auth/sign_out"
    res = httpx.delete(url, headers=headers)
    return res.status_code

def tasks(logged_user, month, year):
    user_id = logged_user["data"]["id"]
    last_day = get_last_day_of_month(month, year)
    url = f"https://api.getlabor.com.br/tasks?cost=true&ending={year}-{month}-{last_day}T23:59:59.543Z&includes%5B%5D=planned_task&starting={year}-{month}-01T00:00:00.000Z&user_id%5B%5D={user_id}"
    projects = _request(BASE_URL + 'projects', logged_user)
    res = _request(url, logged_user)
    return json.loads(res.text), res.status_code, json.loads(projects.text)

def reports(logged_user, year):
    res = _request(BASE_URL + f'reports?&year={year}', logged_user)
    return json.loads(res.text), res.status_code