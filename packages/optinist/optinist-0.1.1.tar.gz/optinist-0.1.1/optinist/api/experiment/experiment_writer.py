import os
from datetime import datetime
from dataclasses import asdict
from typing import Dict

from optinist.api.dir_path import DIRPATH
from optinist.api.experiment.experiment import ExptConfig, ExptFunction
from optinist.api.experiment.experiment_reader import ExptConfigReader
from optinist.api.utils.filepath_creater import join_filepath
from optinist.api.config.config_writer import ConfigWriter
from optinist.api.workflow.workflow import Edge, Node


class ExptConfigWriter:

    @classmethod
    def write(cls, unique_id: str, name: str, nodeDict: Dict[str, Node], edgeDict: Dict[str, Edge]) -> None:
        expt_filepath = join_filepath([
            DIRPATH.OUTPUT_DIR,
            unique_id,
            DIRPATH.EXPERIMENT_YML
        ])
        if os.path.exists(expt_filepath):
            expt_config = ExptConfigReader.read(expt_filepath)
            expt_config = cls.add_run_info(expt_config, nodeDict, edgeDict)
        else:
            expt_config = cls.create_config(unique_id, name, nodeDict, edgeDict)

        expt_config.function = cls.function_from_nodeDict(nodeDict)

        ConfigWriter.write(
            dirname=join_filepath([DIRPATH.OUTPUT_DIR, unique_id]),
            filename=DIRPATH.EXPERIMENT_YML,
            config=asdict(expt_config),
        )

    @classmethod
    def create_config(cls, unique_id: str, name: str, nodeDict: Dict[str, Node], edgeDict: Dict[str, Edge]) -> ExptConfig:
        return ExptConfig(
            unique_id=unique_id,
            name=name,
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            hasNWB=False,
            nodeDict=nodeDict,
            edgeDict=edgeDict,
            function={},
        )

    @classmethod
    def add_run_info(cls, expt_config: ExptConfig, nodeDict: Dict[str, Node], edgeDict: Dict[str, Edge]) -> ExptConfig:
        # 時間を更新
        expt_config.timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # # 関数を追加の可能性
        expt_config.nodeDict = nodeDict
        expt_config.edgeDict = edgeDict

        return expt_config

    @classmethod
    def function_from_nodeDict(cls, nodeDict: Dict[str, Node]) -> Dict[str, ExptFunction]:
        return {
            node.id: ExptFunction(
                unique_id=node.id,
                name=node.data.label,
                success="success" if node.data.type == "input" else "running",
                hasNWB=False,
            )
            for node in nodeDict.values()
        }
