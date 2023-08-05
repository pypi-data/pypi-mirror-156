import requests
import pandas as pd
import json

def ctdbase_fetch(cas_num, api, endpoint):
    """
    | Returns CTDBase data for a given API and cas number
    |
    | Endpoint variables:
    | "cgixns" = Gene interactions
    | "diseases" = Associated diseases
    """
    try:
        url = f"https://ctdbase.org/tools/batchQuery.go?inputType=chem&inputTerms={cas_num}&report={endpoint}&format=json"
        response = requests.get(url).json()
        response_pd = pd.DataFrame(response)
        return response_pd
    except NameError:
        print("Not data available")
    finally:
        url = f"https://ctdbase.org/tools/batchQuery.go?inputType=chem&inputTerms={api}&report={endpoint}&format=json"
        response = requests.get(url).json()
        response_pd = pd.DataFrame(response)
        return response_pd


def ot_gene_pathways(ensemblId):
    query_string = """
      query target($ensemblId: String!){
        target(ensemblId: $ensemblId){
          id
          approvedSymbol
          pathways{
              pathway
              pathwayId
              topLevelTerm
            }
        }
      }
    """

    # Set variables object of arguments to be passed to endpoint
    variables = {"ensemblId": ensemblId}

    # Set base URL of GraphQL API endpoint
    base_url = "https://api.platform.opentargets.org/api/v4/graphql"

    # Perform POST request and check status code of response
    r = requests.post(base_url, json={"query": query_string, "variables": variables})
    print(r.status_code)

    # Transform API response from JSON into Python dictionary and print in console
    api_response = json.loads(r.text)
    print(api_response)
    pathways = api_response["data"]["target"]["pathways"]
    pathway_list = []

    for pathway in pathways:
        single_pathway_dict = {
            "pathway_id": pathway["pathwayId"],
            "pathway": pathway["pathway"],
            "pathway_group": pathway["topLevelTerm"]
        }
        pathway_list.append(single_pathway_dict)
    return pathway_list


def ot_disease_phenotypes(disease_id):
    query_string = """
      query disease($efoId: String!){
        disease(efoId: $efoId){
            id
            name
            phenotypes{
              rows {
                phenotypeHPO {
                  id
                  name
                  namespace
                }
              }
            }
          }

          }
    """

    # Set variables object of arguments to be passed to endpoint
    variables = {"efoId": disease_id}

    # Set base URL of GraphQL API endpoint
    base_url = "https://api.platform.opentargets.org/api/v4/graphql"

    # Perform POST request and check status code of response
    r = requests.post(base_url, json={"query": query_string, "variables": variables})
    print(r.status_code)

    # Transform API response from JSON into Python dictionary and print in console
    api_response = json.loads(r.text)
    print(api_response)
    phenotypes = api_response["data"]["disease"]["phenotypes"]["rows"]
    phenotype_list = []
    for phenotype in phenotypes:
        phenotype_nested = phenotype["phenotypeHPO"]
        single_phenotype_dict = {
            "phenotype_id": phenotype_nested["id"],
            "phenotype": phenotype_nested["name"],
            "phenotype_space": phenotype_nested["namespace"][0]
        }
        phenotype_list.append(single_phenotype_dict)

    return phenotype_list
