import json
from typing import cast, Dict, Optional
from dataclasses import asdict

from . import api
from .helpers import extract_typed_id, extract_arg_query


def facts_to_params(facts) -> api.Fact:
    return [
        api.Fact(predicate, list(map(extract_typed_id, args)))
        for [predicate, *args] in facts
    ]


class Oso:
    def __init__(self, url="https://cloud.osohq.com", api_key=None):
        self.api = api.API(url, api_key)

    def authorize(self, actor, action, resource, context_facts=[]):
        actor_typed_id = extract_typed_id(actor)
        resource_typed_id = extract_typed_id(resource)
        data = api.AuthorizeQuery(
            actor_typed_id["type"],
            actor_typed_id["id"],
            action,
            resource_typed_id["type"],
            resource_typed_id["id"],
            facts_to_params(context_facts),
        )
        result = self.api.post_authorize(data)
        return result.allowed

    def authorize_resources(self, actor, action, resources, context_facts=[]):
        def key(e: Dict) -> str:  # { "type": "type", "id": "id" }
            return f"{e['type']}:{e['id']}"

        if not resources or len(resources) == 0:
            return []

        resources_extracted = [extract_typed_id(r) for r in resources]
        actor_typed_id = extract_typed_id(actor)
        data = api.AuthorizeResourcesQuery(
            actor_typed_id["type"],
            actor_typed_id["id"],
            action,
            resources_extracted,
            facts_to_params(context_facts),
        )
        result = self.api.post_authorize_resources(data)
        if len(result.results) == 0:
            return []

        results_lookup = dict()
        for r in result.results:
            k = key(r)
            if not results_lookup.get(k, None):
                results_lookup[k] = True

        return list(
            filter(
                lambda r: results_lookup.get(key(extract_typed_id(r)), None),
                resources,
            )
        )

    def list(self, actor, action, resource_type, context_facts=[]):
        actor_typed_id = extract_typed_id(actor)
        data = api.ListQuery(
            actor_typed_id["type"],
            actor_typed_id["id"],
            action,
            resource_type,
            facts_to_params(context_facts),
        )
        result = self.api.post_list(data)
        return result.results

    def actions(self, actor, resource, context_facts=[]):
        actor_typed_id = extract_typed_id(actor)
        resource_typed_id = extract_typed_id(resource)
        data = api.ActionsQuery(
            actor_typed_id["type"],
            actor_typed_id["id"],
            resource_typed_id["type"],
            resource_typed_id["id"],
            facts_to_params(context_facts),
        )
        result = self.api.post_actions(data)
        return result.results

    def tell(self, predicate, *args):
        args = list(map(extract_typed_id, args))
        fact = api.Fact(predicate, args)
        result = self.api.post_facts(fact)
        return result

    def bulk_tell(self, facts):
        result = self.api.post_bulk_load(facts_to_params(facts))
        return result

    def delete(self, predicate, *args):
        args = list(map(extract_typed_id, args))
        fact = api.Fact(predicate, args)
        result = self.api.delete_facts(fact)
        return result

    def bulk_delete(self, facts):
        result = self.api.post_bulk_delete(facts_to_params(facts))
        return result

    # NOTE: the args stuff here doesn not show up in the openapi spec
    # so we don't codegen this correctly
    def get(self, predicate=None, *args):
        result = self.api.get_facts(predicate, *args)
        return list(map(asdict, result))

    # TODO: Fix nullable fields in codegen
    def policy(self, policy):
        policy = api.Policy("", policy)
        return self.api.post_policy(policy)
