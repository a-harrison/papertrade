### PaperTrade

This is a personal learning project created using FastAPI.

Final vision is a web app that allows for tracking stock trading with friends.
A user can invite friends, create contests of a certain dollar amount (not real
money) with a time length, and a dashboard to allow users to see how well they
perform against one another.

This repository is the server side API. Final vision would be a front-end made in
React or other framework.

##### Current status:
* Very early on.
* Basic users endpoint created.
* Dummy JSON Web Token authentication implemented referencing a dummy DB object
* Basic testing implemented for endpoints that exist.
* More robust authentication incoming. 

#### Install

```
pip install -r requirements.txt
```

#### Start

```
uvicorn api.main:app --reload
```

#### Run Tests

```
pytest
```
