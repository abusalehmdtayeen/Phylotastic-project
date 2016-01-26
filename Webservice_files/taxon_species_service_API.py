from flask import Flask, jsonify, request
import json
import requests

app = Flask(__name__)

api_url = "http://api.gbif.org/v1/species/"

def get_children(taxonKey):
    resource_url = api_url + str(taxonKey) + "/children"    
    payload = {
        'limit': 1000,   
    }
    children_result = requests.get(resource_url, params=payload)
    res_json = json.loads(children_result.text)
        
    children_list = []
    for child in res_json['results']:
        childAtt = {}         
        childAtt['canonicalName'] = child['canonicalName']
        childAtt['key'] = child['key']
        children_list.append(childAtt)
        
    return children_list

def get_species_from_order(orderKey):
    species_list = [] 
    #get all genus of a family    
    family_list = get_children(orderKey)
    for family in family_list: 
        children_lst = get_species_from_family(family['key'])
        for child in children_lst:         
            species_list.append(child)            
        
    return species_list

def get_species_from_family(familyKey):
    species_list = [] 
    #get all genus of a family    
    genus_list = get_children(familyKey)
    for genus in genus_list: 
        children_lst = get_species_from_genus(genus['key'])
        for child in children_lst:         
            species_list.append(child)            
        
    return species_list

def get_species_from_genus(genusKey):
    species_list = []
    #get all species of a genus 
    children_lst = get_children(genusKey)
    for child in children_lst: 
        species_list.append(child['canonicalName'])            
        
    return species_list
                
def match_taxon(taxonName):
    resource_url = api_url + "match"    
    payload = {
        'name': taxonName,
        'verbose': 'true',
        'strict': 'true'
    }    
    
    matched_result = requests.get(resource_url, params=payload)
    res_json = json.loads(matched_result.text) 
    
    taxonAtt = {}
    taxonAtt['matchType'] = res_json['matchType']
    if res_json['matchType'] == 'NONE':
        for s in res_json['alternatives']:
            if s['matchType'] == 'EXACT':
                taxonAtt['matchType'] = s['matchType']                
                taxonAtt['rank'] = s['rank']
                taxonAtt['canonicalName'] = s['canonicalName']
                taxonAtt['usageKey'] = s['usageKey']                
                break;
    else:
        taxonAtt['matchType'] = res_json['matchType']
        taxonAtt['rank'] = res_json['rank']
        taxonAtt['canonicalName'] = res_json['canonicalName']
        taxonAtt['usageKey'] = res_json['usageKey']
    
    return taxonAtt

@app.route('/phylo/api/v1.0/species', methods = ['GET'])
def get_species():
    #inputTaxon = 'Vulpes'
    inputTaxon = request.args['taxon']
    #inputTaxon = request.args.get('taxon')    
    result = match_taxon(inputTaxon)
    if result['rank'] == 'GENUS':
        species_list = get_species_from_genus(result['usageKey'])
    elif result['rank'] == 'FAMILY':
        species_list = get_species_from_family(result['usageKey'])        
    elif result['rank'] == 'ORDER':
        species_list = get_species_from_order(result['usageKey'])   
        
    species_list.sort()    
        
    return jsonify( {'species': species_list} )


def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

@app.route('/phylo/api/v1.0/shutdown', methods=['POST'])
def shutdown():
    shutdown_server()
    return 'Server shutting down...'


if __name__ == '__main__':
    app.run()