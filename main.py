from flask import Flask, request, Response
import google.cloud.logging
import handlers
import json

logClient = google.cloud.logging.Client()
logClient.setup_logging()

app = Flask(__name__)
app.config.from_object('config')
app.secret_key = app.config['SECRET_KEY']
context_root = app.config['PROJECT_ID']
connection_options = json.loads(app.config['CONNECTION_OPTIONS'])

@app.get("/" + context_root, defaults={'item_id': None})
@app.get("/" + context_root + "/<path:item_id>")
def getItems(item_id):
    try:
        return handlers.handle_getItems(item_id, connection_options)
    except Exception as e:
        exit(1)
    
@app.post("/" + context_root)
def addItem():
    if request.json is None:
        return Response(response="JSON Object required required", status=400)
    try:
        return handlers.handle_addItem(connection_options)
    except Exception as e:
        exit(1)

@app.delete("/" + context_root + "/<path:item_id>")
def deleteItem(item_id):
    if item_id is None:
        return Response(response="Item ID required", status=400)
    try:
        return handlers.handle_deleteItem(item_id, connection_options)
    except Exception as e:
        exit(1)

@app.put("/" + context_root + "/<path:item_id>")
def updateItem(item_id):
    if item_id is None:
        return Response(response="Item ID required", status=400)
    try:
        return handlers.handle_updateItem(item_id, connection_options)
    except Exception as e:
        exit(1)

if __name__ == "__main__":
    # Development only: run "python main.py" and open http://localhost:8080
    # When deploying to Cloud Run, a production-grade WSGI HTTP server,
    # such as Gunicorn, will serve the app.
    app.run(host="localhost", port=8080, debug=True)