from flask import Flask, request, Response
import google.cloud.logging
import handlers
import json
import multiprocessing

logClient = google.cloud.logging.Client()
logClient.setup_logging()

app = Flask(__name__)
app.config.from_object('config')
app.secret_key = app.config['SECRET_KEY']
context_root = app.config['PROJECT_ID']

def return_response(response_string, status):
    return Response(response=response_string, status=status, mimetype="application/json")

@app.get("/" + context_root, defaults={'item_id': None})
@app.get("/" + context_root + "/<path:item_id>")
def getItems(item_id):
    manager = multiprocessing.Manager()
    return_dict = manager.dict()
    p = multiprocessing.Process(target=handlers.handle_getItems, args=(item_id, return_dict))
    p.start()

    # Wait for 10 seconds or until process finishes
    p.join(30)

    # If thread is still active
    if p.is_alive():
        p.join()
        exit(1)
    else:
        return return_response(json.dumps(return_dict["results"]), return_dict["status"])
    
@app.post("/" + context_root)
def addItem():
    if request.json is None:
        return Response(response="JSON Object required required", status=400)
    
    manager = multiprocessing.Manager()
    return_dict = manager.dict()
    p = multiprocessing.Process(target=handlers.handle_addItem, args=(return_dict,))
    p.start()

    # Wait for 10 seconds or until process finishes
    p.join(30)
    if p.is_alive():
        p.join()
        exit(1)
    else:
        return return_response(json.dumps(return_dict["results"]), return_dict["status"])
        

@app.delete("/" + context_root + "/<path:item_id>")
def deleteItem(item_id):
    if item_id is None:
        return Response(response="Item ID required", status=400)
    
    manager = multiprocessing.Manager()
    return_dict = manager.dict()
    p = multiprocessing.Process(target=handlers.handle_deleteItem, args=(item_id, return_dict))
    p.start()

    # Wait for 10 seconds or until process finishes
    p.join(30)
    if p.is_alive():
        p.join()
        exit(1)
    else:
        return return_response(json.dumps(return_dict["results"]), return_dict["status"])

@app.put("/" + context_root + "/<path:item_id>")
def updateItem(item_id):
    if item_id is None:
        return Response(response="Item ID required", status=400)
    
    manager = multiprocessing.Manager()
    return_dict = manager.dict()
    p = multiprocessing.Process(target=handlers.handle_updateItem, args=(item_id, return_dict))
    p.start()

    # Wait for 10 seconds or until process finishes
    p.join(30)
    if p.is_alive():
        p.join()
        exit(1)
    else:
        return return_response(json.dumps(return_dict["results"]), return_dict["status"])
    
@app.get("/" + context_root + "/describe")
def describe():
    manager = multiprocessing.Manager()
    return_dict = manager.dict()
    p = multiprocessing.Process(target=handlers.handle_describe, args=(return_dict,))
    p.start()

    # Wait for 10 seconds or until process finishes
    p.join(30)
    if p.is_alive():
        p.join()
        exit(1)
    else:
        return return_response(json.dumps(return_dict["results"]), return_dict["status"])

if __name__ == "__main__":
    # Development only: run "python main.py" and open http://localhost:8080
    # When deploying to Cloud Run, a production-grade WSGI HTTP server,
    # such as Gunicorn, will serve the app.
    app.run(host="localhost", port=8080, debug=True)