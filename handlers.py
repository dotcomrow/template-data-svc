from flask import request, Response
from sqlalchemy.orm import Session
import config
import sqlalchemy as db
import logging
from sqlalchemy import select
import orm
import json
import datetime
from sqlalchemy.inspection import inspect

sequence_name = "lookup_code_seq"
connect_key="/secrets/google.key"
bigquery_url='bigquery://' + config.PROJECT_ID + '/' + config.DATASET_NAME

def buildResponse(result):
    out_results = []
    for r in result:
        o = r[0].to_dict()        
        o['last_update_datetime'] = str(o['last_update_datetime'])
        out_results.append(o)
    
    if len(out_results) == 1:
        return out_results[0]
    else:
        return out_results

def handle_getItems(item_id, return_dict):
    engine = db.create_engine(bigquery_url, 
                                credentials_path=connect_key,
                                echo=True,
                                echo_pool=True,
                                pool_size=5,
                                max_overflow=2,
                                pool_timeout=30,
                                pool_recycle=1800,
                                pool_pre_ping=True,
                                pool_use_lifo=True,
                              )
    my_session = Session(engine) 
    result = None
    if item_id is None:
        result = my_session.execute(
                select(orm.LookupCodes)
            ).all()
    else:
        result = my_session.execute(
            select(orm.LookupCodes)
                .where(orm.LookupCodes.code == item_id)                
            ).all()    
    out_results = buildResponse(result) 
    my_session.commit()
    my_session.flush()
    my_session.close()
    return_dict["results"]=out_results
    return_dict["status"]=200

def handle_addItem(return_dict):
    engine = db.create_engine(bigquery_url, 
                                credentials_path=connect_key,
                                echo=True,
                                echo_pool=True,
                                pool_size=5,
                                max_overflow=2,
                                pool_timeout=30,
                                pool_recycle=1800,
                                pool_pre_ping=True,
                                pool_use_lifo=True,
                              )
    connection = engine.connect()
    index = connection.execute(db.text('call ' + config.DATASET_NAME + '.get_row_id(\'' + sequence_name + '\')')).scalar()
    my_session = Session(engine)
    request_data = request.get_json()

    try:
        request_data['id'] = index
        request_data['last_update_datetime'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        newRec = orm.LookupCodes(**request_data)
        my_session.add(newRec)
        my_session.commit()
        my_session.flush()
    except Exception as e:
        logging.error(e)
    
    result = my_session.execute(select(orm.LookupCodes).where(orm.LookupCodes.id == index)).all()
    out_results = buildResponse(result) 
    
    my_session.commit()
    my_session.flush()
    my_session.close()
    
    return_dict["results"]=out_results
    return_dict["status"]=200

def handle_deleteItem(item_id, return_dict):
    engine = db.create_engine(bigquery_url, 
                                credentials_path=connect_key,
                                echo=True,
                                echo_pool=True,
                                pool_size=5,
                                max_overflow=2,
                                pool_timeout=30,
                                pool_recycle=1800,
                                pool_pre_ping=True,
                                pool_use_lifo=True,
                              )
    my_session = Session(engine) 
    result = my_session.execute(
        select(orm.LookupCodes)
            .where(orm.LookupCodes.id == int(item_id))
        ).all()
    
    if len(result) == 0:
        return_dict["results"]="Item does not exist"
        return_dict["status"]=404
        return
    
    my_session.delete(result[0][0])
    my_session.commit()
    my_session.flush()
    my_session.close()
    
    return_dict["results"]="Item deleted"
    return_dict["status"]=200

def handle_updateItem(item_id, return_dict):
    engine = db.create_engine(bigquery_url, 
                                credentials_path=connect_key,
                                echo=True,
                                echo_pool=True,
                                pool_size=5,
                                max_overflow=2,
                                pool_timeout=30,
                                pool_recycle=1800,
                                pool_pre_ping=True,
                                pool_use_lifo=True,
                              )
    my_session = Session(engine) 
    result = my_session.execute(
        select(orm.LookupCodes)
            .where(orm.LookupCodes.id == int(item_id))
        ).all()
    
    if len(result) == 0:
        return_dict["results"]="Item does not exist"
        return_dict["status"]=404
        return
     
    request_data = request.get_json()
    poi_data = result[0][0]
    poi_data.code = request_data['code']
    poi_data.value = request_data['value']
    poi_data.last_update_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    my_session.commit()
    my_session.flush()
    my_session.close()
    
    search_session = Session(engine) 
    search_res = search_session.execute(
        select(orm.LookupCodes)
            .where(orm.LookupCodes.code == item_id)
        ).all()
    
    out_results = buildResponse(search_res) 
    search_session.commit()
    search_session.flush()
    search_session.close()
    return_dict["results"]=out_results
    return_dict["status"]=200
    
def isGeneratedColumn(column_name):
    return True if column_name == "id" or column_name == "last_update_datetime" else  False

def isPrimaryKey(table, column):
    return True if column.name in [key.name for key in table.primary_key] else False;

def handle_describe(return_dict):
    return_dict["results"]=[{
        "name" : column.name,
        "type" : str(column.type),
        "generated": str(isGeneratedColumn(column.name)),
        "primary_key": str(isPrimaryKey(inspect(orm.LookupCodes), column))
    } for column in inspect(orm.LookupCodes).c]
    return_dict["status"]=200
    return