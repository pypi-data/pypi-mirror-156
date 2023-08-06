from typing import Dict

from optinist.api.dataclass.dataclass import *
from optinist.api.snakemake.smk import Rule
from optinist.api.workflow.workflow import Edge, Node, NodeType
from optinist.api.workflow.workflow_params import get_typecheck_params
from optinist.api.utils.filepath_creater import get_pickle_file


class SmkSetfile:
    @classmethod
    def image(cls, unique_id: str, node: Node, edgeDict: Dict[str, Edge], nwbfile):
        return_name = cls.get_return_name(node, edgeDict)

        output_file = get_pickle_file(
            unique_id,
            node.id,
            node.data.label.split(".")[0]
        )

        return Rule(
            input=node.data.path,
            return_arg=return_name,
            params=node.data.param,
            output=output_file,
            type="image",
            nwbfile=nwbfile,
        )

    @classmethod
    def csv(cls, unique_id, node: Node, edgeDict: Dict[str, Edge], nwbfile, nodeType="csv"):
        return_name = cls.get_return_name(node, edgeDict)

        output_file = get_pickle_file(
            unique_id,
            node.id,
            node.data.label.split(".")[0]
        )

        return Rule(
            input=node.data.path,
            return_arg=return_name,
            params=node.data.param,
            output=output_file,
            type=nodeType,
            nwbfile=nwbfile,
        )

    @classmethod
    def hdf5(cls, unique_id, node: Node, edgeDict: Dict[str, Edge], nwbfile):
        return_name = cls.get_return_name(node, edgeDict)

        output_file = get_pickle_file(
            unique_id,
            node.id,
            node.data.label.split(".")[0]
        )

        return Rule(
            input=node.data.path,
            return_arg=return_name,
            params=node.data.param,
            output=output_file,
            type="hdf5",
            nwbfile=nwbfile,
            hdf5Path=node.data.hdf5Path,
        )

    @classmethod
    def algo(cls, unique_id, node: Node, edgeDict: Dict[str, Edge], nodeDict: Dict[str, Node]):
        algo_input = []
        return_arg_names = {}
        for edge in edgeDict.values():
            if node.id == edge.target:
                arg_name = edge.targetHandle.split("--")[1]

                sourceNode = nodeDict[edge.source]
                if sourceNode.type == NodeType.ALGO:
                    return_name = edge.sourceHandle.split("--")[1]
                    algo_input.append(get_pickle_file(
                        unique_id,
                        sourceNode.id,
                        sourceNode.data.label
                    ))
                else:
                    return_name = edge.sourceHandle.split("--")[0]
                    algo_input.append(get_pickle_file(
                        unique_id,
                        sourceNode.id,
                        sourceNode.data.label.split(".")[0]
                    ))

                return_arg_names[return_name] = arg_name

        params = get_typecheck_params(node.data.param, node.data.label)
        algo_output = get_pickle_file(unique_id, node.id, node.data.label)

        return Rule(
            input=algo_input,
            return_arg=return_arg_names,
            params=params,
            output=algo_output,
            path=node.data.path,
            type=node.data.label,
        )

    @classmethod
    def get_return_name(cls, node: Node, edgeDict: Dict[str, Edge]):
        for edge in edgeDict.values():
            if node.id == edge.source:
                return_name = edge.sourceHandle.split("--")[0]
        return return_name
