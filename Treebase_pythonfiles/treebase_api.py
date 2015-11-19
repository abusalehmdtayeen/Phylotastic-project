import requests
import urllib
import xml.etree.ElementTree as ET
import dendropy

url = "http://purl.org/phylo/treebase/phylows/taxon/find?"
headers = {'user-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:42.0) Gecko/20100101 Firefox/42.0'}


def create_payload(taxon):
    querystr = 'tb.title.taxon='
    query = querystr + taxon  

    payload = {
      'query': query, 
      'format': 'rss1',
      'recordSchema':  'tree' 
    }
    
    encoded_payload = urllib.urlencode(payload)
    #print encoded_payload    
    return encoded_payload


#----------------------------------------
def get_tree(species):
    
    #need to quote the species name
    dqote = '"'    
    species = dqote + species + dqote
    
    payload = create_payload(species)
    page = requests.get(url, params=payload, headers=headers)
    #print page.url

    NSMap = {
         'dcterms': 'http://purl.org/rss/1.0/',
         'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
         'dc' :'http://purl.org/dc/elements/1.1/', 
         'ns' : 'http://purl.org/rss/1.0/'
        }

    tree_root = ET.fromstring(page.content)

    if tree_root.find('ns:item', NSMap) is None:
        return "No Tree found"
    else:    
        for child in tree_root.findall('ns:item', NSMap):
            item_link = child.get('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about', NSMap)
            tree = dendropy.Tree.get(url=item_link+'?format=nexus', schema="nexus")        
            return tree.as_string(schema="newick")
        
#-------------------------------------------
if __name__ == '__main__':
    
    #taxon = 'Atta laevigata'    
    taxon = 'Camponotus sericeus'
    treebase_result = get_tree(taxon)    
    print "Final Result:"    
    print treebase_result

