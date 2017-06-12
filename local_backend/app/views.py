from flask import render_template, request, jsonify, abort
from . import app
from .models import Reputation
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
from datetime import datetime, timedelta
from pprint import pprint
import json
#@app.before_first_request
def update_domain_list():
    #print (app.config['LATEST_DOMAIN_ID'])
    pass

@app.route('/')
def index():
    domains = Reputation.query.all()
    return render_template('app/index.html',domains=domains )

@app.route('/ttp')
def ttp_feed():
    index='netmode-aggrevents-2017.06.11' 
    es_client = Elasticsearch(hosts=app.config['TTP_HOST'], port=app.config['TTP_PORT'])
    # TODO: let user define the doc_type he wants to see
    # Or operate on all doc_types at once on post-processing!
    # Also, iterate over all districts' indices
    s = Search(using=es_client, index=index, doc_type='auth') \
        .query('match', aggregation_type='attacker') \
        .sort('-@timestamp') \
        .extra(size=1)
    collaborator_aggregation = s.execute()[0]
    with open(app.config['LOCAL_LATEST_AGGR']) as f:
        local_aggr_event = json.load(f)

    results = []
    for cidr in local_aggr_event['cidrs']: 
        for col_cidr in collaborator_aggregation['cidrs']:
            if col_cidr['network'] == cidr['network']:
               #print(col_cidr['network'], ': ', col_cidr['total_attempts'], ' | ', cidr['total_attempts'])
               results.append((col_cidr['network'], col_cidr['total_attempts'], cidr['total_attempts']))
               break
    local_distr = app.config['LOCAL_DISTRICT']
    return render_template(
        'app/ttp.html', 
        aggr_event=collaborator_aggregation, 
        results=results, 
        local_distr=local_distr,
    )


@app.route('/api/get_latest', methods=['GET'])
def get_latest():
    with open(app.config['LOCAL_LATEST_AGGR']) as f:
        local_aggr_event = json.load(f)
    return jsonify(local_aggr_event)