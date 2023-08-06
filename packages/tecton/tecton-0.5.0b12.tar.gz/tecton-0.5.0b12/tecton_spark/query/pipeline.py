from tecton_core.query.nodes import FeatureViewPipelineNode
from tecton_spark.pipeline_helper import _PipelineBuilder
from tecton_spark.query import translate
from tecton_spark.query.node import SparkExecNode


class PipelineEvalSparkNode(SparkExecNode):
    def __init__(self, node: FeatureViewPipelineNode):
        self.inputs_map = {key: translate.spark_convert(node.inputs_map[key]) for key in node.inputs_map}
        self.feature_definition_wrapper = node.feature_definition_wrapper
        # Needed for correct behavior on MaterializationContextNode in the pipeline
        self.feature_time_limits = node.feature_time_limits

    def to_dataframe(self, spark):
        return _PipelineBuilder(
            spark,
            self.feature_definition_wrapper.pipeline,
            consume_streaming_data_sources=False,
            data_sources=self.feature_definition_wrapper.data_sources,
            transformations=self.feature_definition_wrapper.transformations,
            feature_time_limits=self.feature_time_limits,
            schedule_interval=None,
            passed_in_inputs={k: self.inputs_map[k].to_dataframe(spark) for k in self.inputs_map},
        ).get_dataframe()
