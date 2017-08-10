from flask import render_template, request, jsonify, abort, url_for, redirect
from . import app, db
from .models import Reputation
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
from datetime import datetime, timedelta
from pprint import pprint
import json

#######################################################
####################### Views #########################
#######################################################

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.form:
        # Request district from database
        district_name = request.form.get('topup')
        district = db.session.query(Reputation).filter_by(district=district_name).first()

        # TODO: Define reputation formula
        rep_formula = district.rep + 10
        district.rep = min(rep_formula, 100)
        db.session.commit()
        
        # Push new reputation to TTP
        push_to_ttp(app.config, district)

        # Redirect to index to avoid resubmitting the reputation increase form
        return redirect(url_for('index'))
    districts = Reputation.query.all()
    return render_template('app/index.html',districts=districts )

@app.route('/ttp')
def ttp_feed():
    data= {}
    collaborator = request.args.get('coll')
    
    # Load district's latest per attacker aggregation 
    with open(app.config['LOCAL_LATEST_AGGR']) as f:
        local_aggr_event = json.load(f)
    
    if collaborator:
        results = []
        index = collaborator + '-aggrevents-*' 
        es_client = Elasticsearch(hosts=app.config['TTP_HOST'], port=app.config['TTP_PORT'])
        
        # TODO: let user define the doc_type he wants to see
        # Or operate on all doc_types at once on post-processing!
        # Also, iterate over all districts' indices
        s = Search(using=es_client, index=index, doc_type='auth') \
            .query('match', aggregation_type='attacker') \
            .sort('-@timestamp') \
            .extra(size=1)          # Query remote district's latest aggregation from TTP
        remote_aggr = s.execute()[0]
        
        indexable_aggr = ldict_to_ddict(remote_aggr) # Improves performance greatly, read definition
        num_matching_events = 0
        num_total_events = 0
        for cidr in local_aggr_event['cidrs']:
            num_total_events += 1
            if cidr['network'] in indexable_aggr:
                results.append((
                    cidr['network'],
                    cidr['total_attempts'],
                    indexable_aggr[cidr['network']]
                ))
                num_matching_events += 1
        
        # Enrich document
        remote_district = Reputation.query.filter_by(name=collaborator).first()
        data['remote_district'] = remote_district
        data['aggr_event'] = remote_aggr
        data['percentage'] = float(format((num_matching_events / num_total_events) * 100, '.2f')) 
        data['results'] = sorted(results, key=lambda tup: tup[1], reverse=True) 
    else:  # If we are not comparing against any other district, show our local latest aggregation
        data['aggr_event'] = local_aggr_event  

    data['local_distr'] = app.config['LOCAL_DISTRICT']
    data['districts'] = Reputation.query.all()
    return render_template('app/ttp.html', **data)

@app.route('/decay_rep')
def decay_reputation():
    """Decreases every district's reputation at regular intervals"""
    
    # Decay all reputations
    update_body = {
            'doc' :{}
        }
    try:
        for district in Reputation.query.all():
            district.rep = max(district.rep - app.config['AGING_DECAY'], app.config['MIN_REP_VALUE'])
            db.session.add(district)
            db.session.commit()
            update_body['doc'][district.name] = district.rep
    except Exception as e:
        print(e)
        abort(500)

    # Push new reputations to TTP
    es = Elasticsearch(hosts=app.config['TTP_HOST'], port=app.config['TTP_PORT'])
    rep_index = app.config['TTP_REP_INDEX']        
    rep_doc_type = app.config['LOCAL_DISTRICT']
    es.update(index=rep_index, doc_type=rep_doc_type, id=1, body=update_body)
    return 'Update Complete'

@app.route('/ttp_all')
def ttp_all_list():
    """Gets the latest aggregation for all districts from TTP and serves it"""
    
    es = Elasticsearch(hosts=app.config['TTP_HOST'], port=app.config['TTP_PORT'])
    aggr_index = app.config['TTP_AGGR_INDEX_PREFIX'] + '*'        
    doc_type = 'all_raw'
    s = Search(using=es, index=aggr_index, doc_type=doc_type) \
        .sort('-@timestamp') \
        .extra(size=1)
    all_raw_event = s.execute()[0]
    attackers = sorted(all_raw_event['attackers'], key=lambda k: k['attempts'], reverse=True) 
    cidrs = sorted(all_raw_event['cidrs'], key=lambda k: k['total_attempts'], reverse=True)
    return render_template('app/ttp_all.html', event=all_raw_event,cidrs=cidrs, attackers=attackers)

#######################################################
################## Private Functions ##################
#######################################################

def push_to_ttp(config, district):
    es = Elasticsearch(hosts=config['TTP_HOST'], port=config['TTP_PORT'])
    rep_index = config['TTP_REP_INDEX']        
    rep_doc_type = config['LOCAL_DISTRICT']
    insert_body = { 
        district.name: district.rep
    }
    update_body = {
        'doc' :{
                district.name: district.rep,
        }
    }
    if not es.indices.exists(index=rep_index):
        es.indices.create(rep_index)
    if not es.exists(index=rep_index, doc_type=rep_doc_type, id=1):
        es.index(index=rep_index, doc_type=rep_doc_type, id=1, body=insert_body)
    else:
        es.update(index=rep_index, doc_type=rep_doc_type, id=1, body=update_body)
        

def ldict_to_ddict(aggregations):
    """
    Converts a list of dictionaries to a dictionary of dictionaries.
    
    Note: We use this as an optimization since we want to cross check all the subnets found
    in our local aggregations against the collaraborator's aggregations. Therefore, 
    if we use a listwe need O(n) time to find an item in the list, 
    instead we convert it to a dictionary that requires O(1) in the general case.
    
    Also, we cannot have a dictionary in the first place because of Elasticsearch limitations.
    For more information and a deeper understanding check out ESclient's Wiki 
    on "Implementation Concerns"
    """
    d = {}
    for cidr in aggregations['cidrs']:
        d[cidr['network']] = cidr['total_attempts']
    return d