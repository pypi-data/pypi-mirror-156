from typing import Any
from starlette.graphql import GraphQLApp
from fastapi import APIRouter, Depends
import graphene as gr
from graphql.execution.base import ResolveInfo
from starlette.requests import Request

from ert_shared.dark_storage.enkf import get_res, get_name
from ert_shared.dark_storage.graphql.ensembles import Ensemble, CreateEnsemble
from ert_shared.dark_storage.graphql.experiments import Experiment, CreateExperiment


class Query(gr.ObjectType):
    experiments = gr.List(Experiment)
    experiment = gr.Field(Experiment, id=gr.ID(required=True))
    ensemble = gr.Field(Ensemble, id=gr.ID(required=True))

    @staticmethod
    def resolve_experiments(root: Any, info: ResolveInfo) -> None:
        return ["default"]

    @staticmethod
    def resolve_experiment(root: Any, info: ResolveInfo, id: str) -> None:
        return "default"

    @staticmethod
    def resolve_ensemble(root: Any, info: ResolveInfo, id: str) -> None:
        return get_name("ensemble", id)


class Mutations(gr.ObjectType):
    create_experiment = CreateExperiment.Field()
    create_ensemble = gr.Field(
        CreateEnsemble,
        active_realizations=gr.List(gr.Int),
        parameter_names=gr.List(gr.String),
        size=gr.Int(),
        experiment_id=gr.ID(required=True),
    )


schema = gr.Schema(query=Query, mutation=Mutations)
graphql_app = GraphQLApp(schema=schema)
router = APIRouter(tags=["graphql"])


@router.post("/gql")
async def f(request: Request, res=Depends(get_res)):
    request.state.res = res
    return await graphql_app.handle_graphql(request=request)
