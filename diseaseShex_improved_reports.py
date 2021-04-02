import requests
import pyshex
from pyshex.utils.schema_loader import SchemaLoader
from pprint import pprint
import copy
from wikidataintegrator import wdi_core
from ShExJSG import Schema, ShExC
from pyjsg.jsglib.loader import is_valid
from pyshex import ShExEvaluator
from rdflib import Graph
rdfdata = Graph()
import json
shex = requests.get("https://genewikibots.semscape.org/wiki/Special:EntitySchemaText/E3").text
shex_results = dict()

schema = SchemaLoader().loads(shex)
not_evaluated = dict()
try:
    query = "SELECT * WHERE {?item wdt:P699 ?doid .}"
    query_results = wdi_core.WDFunctionsEngine.execute_sparql_query(query=query, as_dataframe=True)
    for index, row in query_results.iterrows():
        qid=row["item"].replace("http://www.wikidata.org/entity/", "")
        print(qid)
        rdfdata.parse("http://www.wikidata.org/entity/{}.ttl".format(qid))
        result = ShExEvaluator(rdf=rdfdata, schema=schema, focus="http://www.wikidata.org/entity/{}".format(qid)).evaluate()
        for i in range(len(schema.shapes[0].expression.expressions)):  
            schema2 = SchemaLoader().loads(shex)
            for j in range(len(schema2.shapes[0].expression.expressions), -1, -1):
                keep = schema.shapes[0].expression.expressions[i]        
                if schema2.shapes[0].expression.expressions[j-1] != keep:
                        schema2.shapes[0].expression.expressions.pop(j-1)
            result = ShExEvaluator(rdf=rdfdata, schema=schema2, focus="http://www.wikidata.org/entity/{}".format(qid)).evaluate()
            if not result[0].result:
                if qid not in shex_results.keys():
                    shex_results[qid]=[]
                reason = result[0].reason.split("\n")[len(result[0].reason.split("\n"))-1]
                temp = dict()
                temp["property"] = schema2.shapes[0].expression.expressions[0].predicate
                temp["reason"] = reason.strip()
                temp["verbose_reason"] = result[0].reason
                shex_results[qid].append(temp)
except Exception as e:
        not_evaluated[row["item"]] = str(e)

with open('disease_shex.json', 'w', encoding='utf-8') as f:
    json.dump(shex_results, f, ensure_ascii=False, indent=4)

with open('disease_shex_errors.json', 'w', encoding='utf-8') as f:
    json.dump(not_evaluated, f, ensure_ascii=False, indent=4)
