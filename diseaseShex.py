from rdflib import Graph
from wikidataintegrator import wdi_core
from pprint import pprint

query = "SELECT * WHERE {?item wdt:P699 ?doid .} LIMIT 10"
results = wdi_core.WDFunctionsEngine.execute_sparql_query(query=query, as_dataframe=True)

report = []
not_evaluated = dict()
for index, row in results.iterrows():
    try:
        shex = wdi_core.WDFunctionsEngine.check_shex_conformance(qid=row["item"].replace("http://www.wikidata.org/entity/", ""), eid="E3", entity_schema_repo="https://genewikibots.semscape.org/wiki/Special:EntitySchemaText/", output="conform")
        print(row["item"], shex["result"])
        report.append(shex)
    except Exception as e:
        not_evaluated[row["item"]] = str(e)

pprint(report)

import json
with open('disease_shex.json', 'w', encoding='utf-8') as f:
    json.dump(report, f, ensure_ascii=False, indent=4)

with open('disease_shex_errors.json', 'w', encoding='utf-8') as f:
    json.dump(report, f, ensure_ascii=False, indent=4)
# print(wdi_core.WDFunctionsEngine.check_shex_conformance(qid="Q35869", eid="E113", output="conform"))


