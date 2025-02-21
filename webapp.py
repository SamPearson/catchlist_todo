from flask import Flask, render_template, request, redirect, url_for
import os
import requests
from dotenv import load_dotenv

app = Flask(__name__)

# env files are specified in systemd service files on staging&prod
# we launch the app with gunicon on staging/prod, thus ( __name__ == main ) only on dev/local.
if __name__ == "__main__":
    load_dotenv('environments/.env.local')

API_URL = os.getenv('API_URL')
if not API_URL:
    print("API_URL is not set. Please check your environment files.")


@app.route('/')
def home():
    response = requests.get(f"{API_URL}/todos")
    if response.status_code == 200:
        todo_list = response.json()
    else:
        todo_list = []  # TODO make this return some kind of error
    return render_template("base.html", todo_list=todo_list)


@app.route("/add", methods=["POST"])
def add():
    title = request.form.get("title")
    response = requests.post(f"{API_URL}/todos", json={"title": title})
    if response.status_code == 201:
        return redirect(url_for("home"))
    else:
        return "Failed to add todo", 500


@app.route("/update/<int:todo_id>")
def update(todo_id):
    response = requests.get(f"{API_URL}/todos/{todo_id}")
    if response.status_code == 200:
        todo = response.json()
        todo["complete"] = not todo["complete"]
        response = requests.put(f"{API_URL}/todos/{todo_id}", json=todo)
        if response.status_code == 200:
            return redirect(url_for("home"))
    return "Failed to update todo", 500


@app.route("/delete/<int:todo_id>", methods=["DELETE"])
def delete(todo_id):
    response = requests.delete(f"{API_URL}/todos/{todo_id}")
    if response.status_code == 200:
        return "", 204  # No Content response (DELETE success), reloading happens in javascript
    return "Failed to delete todo", 500


# We have to have a second ( __name__ == main ) check here
# because app.run() needs to happen after all routes are defined,
# meanwhile API_URL must be set before routes are defined.
if __name__ == "__main__":
    load_dotenv('environments/.env.local')
    app.run(debug=True, port=5000)