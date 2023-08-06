from django.http import HttpResponse, JsonResponse, FileResponse
from torque import models as torque_models
from django.db.models import Q
from enhanced_curation import models
import random
import json


def ranked_proposals(request):
    group = request.GET["group"]
    q = request.GET["q"]
    global_wiki_key = request.GET["wiki_key"]
    global_collection_name = request.GET["collection_name"]
    wiki_keys = request.GET["wiki_keys"].split(",")
    collection_names = request.GET["collection_names"].split(",")
    org_sizes = request.GET["org_sizes"].split(",") if request.GET["org_sizes"] else []
    selections = json.loads(request.GET["selections"])
    org_budgets = (
        request.GET["org_budgets"].split(",") if request.GET["org_budgets"] else []
    )
    global_config = torque_models.WikiConfig.objects.get(
        collection__name=global_collection_name,
        wiki__wiki_key=global_wiki_key,
        group=group,
    )
    configs = torque_models.WikiConfig.objects.filter(
        collection__name__in=collection_names, wiki__wiki_key__in=wiki_keys, group=group
    ).all()

    filters = [Q(collection_cache__collection__name__in=collection_names)]
    if len(org_sizes) > 0:
        filters.append(Q(org_size__in=org_sizes))

    if len(org_budgets) > 0:
        filters.append(Q(org_budget__in=org_budgets))

    if q:
        search_results = (
            torque_models.SearchCacheDocument.objects.filter(
                collection__name__in=collection_names,
                wiki__wiki_key__in=configs.values_list("wiki__wiki_key", flat=True),
                group__in=configs.values_list("group", flat=True),
                wiki_config__in=configs,
                data_vector=q,
            )
            .select_related("document")
        )

        searched_documents = [ result.document for result in search_results ]

        filters.append(Q(document__in=searched_documents))

    proposals = list(models.DocumentCache.objects.filter(*filters))

    for proposal in proposals:
        proposal.score(selections)

    proposals.sort()

    resp = []
    for proposal in proposals[0:20]:
        for config in configs:
            if config.collection == proposal.document.collection:
                resp.append(proposal.document.to_dict(config))

    return JsonResponse({"result": resp})
