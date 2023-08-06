import functools
from typing import Dict, List

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal  # type: ignore

import pandas as pd

from gantry.query.core.dataframe import GantrySeries
from gantry.query.core.utils import check_response


def categorical(func):
    @functools.wraps(func)
    def categorical_dec(self, outputs: GantrySeries, feedback: GantrySeries, *args, **kwargs):
        if outputs.datatype != "float":
            return func(self, outputs, feedback, *args, **kwargs)
        else:
            raise NotImplementedError()

    return categorical_dec


def regression(func):
    @functools.wraps(func)
    def regression_dec(self, outputs: GantrySeries, feedback: GantrySeries, *args, **kwargs):
        if outputs.datatype == "float":
            return func(self, outputs, feedback, *args, **kwargs)
        else:
            raise NotImplementedError()

    return regression_dec


def score(func):
    @functools.wraps(func)
    def score_dec(self, outputs: GantrySeries, feedback: GantrySeries, *args, **kwargs):
        if outputs.datatype == "float" and feedback.datatype != "float":
            return func(self, outputs, feedback, *args, **kwargs)
        else:
            raise NotImplementedError(
                "Outputs and feedback do not have the appropriate types to calculate score metrics"
            )

    return score_dec


def check_comparable(series_a, series_b):
    if not all(
        [filter_a == filter_b for filter_a, filter_b in zip(series_a.filters, series_b.filters)]
    ):
        raise ValueError(
            "Series A and series B do not have the same filters. "
            "Series A filters: {}\nSeries B filters: {}".format(series_a.filters, series_b.filters)
        )


class GantryMetric(object):
    """
    Gantry metric computations.

    Inspired by and references sklearn metrics:
    https://scikit-learn.org/stable/modules/classes.html#module-sklearn.metrics

    For all queries, we use the first available GantrySeries's QueryInfo to obtain
    the relevant query metadata window.
    """

    def __init__(self, api_client) -> None:
        self._api_client = api_client

    def _metric_query(
        self,
        outputs: GantrySeries,
        feedback: GantrySeries,
        stat: str,
        num_points: int = None,
        stat_kwargs: dict = None,
    ) -> List[Dict]:
        if (num_points is not None) and (num_points < 1):
            raise ValueError(
                "num_points must be greater than 0 if passed. Got {}.".format(num_points)
            )

        # TODO if outputs and feedback don't have the same parent dataframe
        # or have different query_info, we should raise an error. Can check filters.
        check_comparable(outputs, feedback)

        data = {
            "start_time": outputs.query_info.start_time,
            "end_time": outputs.query_info.end_time,
            "num_points": num_points,
            "queries": {
                "query_label": {
                    "query_type": "data_node_ids",
                    "func_name": outputs.query_info.application,
                    "version": outputs.query_info.version,
                    "stat": stat,
                    "stat_kwargs": stat_kwargs or {},
                    "filters": outputs.filters,
                    "start_time": outputs.query_info.start_time,
                    "end_time": outputs.query_info.end_time,
                    "data_node_ids": [
                        outputs.id,
                        feedback.id,
                    ],
                },
            },
        }

        response = self._api_client.request("POST", "/api/v1/time_series/query", json=data)
        check_response(response)
        return response["data"]["query_label"].get("points", [])

    def _prepare_pandas_dataframe(self, stat, results, dropna) -> pd.DataFrame:
        df = pd.DataFrame.from_records(results)
        if df.empty:
            return df

        # note that if num_points is 1, the timestamp is start_time
        # this is probably better than using end_time because
        # end_time is possibly in the future
        df.time_stamp = pd.to_datetime(df.time_stamp)
        df.rename(columns={"value": stat, "time_stamp": "timestamp"}, inplace=True)

        if dropna:
            df = df.dropna()

        return df.set_index("timestamp")

    @categorical
    def accuracy_score(
        self,
        outputs: GantrySeries,
        feedback: GantrySeries,
        dropna: bool = False,
        num_points: int = 1,
    ) -> pd.DataFrame:
        """
        Categorical metric - accuracy

        In multilabel classification, this computes the set of |outputs| which exactly match
        the available |feedback|.

        Args:
            outputs: predictions as a GantrySeries
            feedback: labels to compare against as a GantrySeries
            dropna: if True, drop rows with NaN values in result
            num_points: number of points to divide the time window of the GantrySeries into
        Returns: pd.DataFrame of shape (num_points, 1) accuracy score
        """
        stat = "accuracy_score"
        results = self._metric_query(
            outputs,
            feedback,
            stat,
            num_points=num_points,
        )
        return self._prepare_pandas_dataframe(stat, results, dropna=dropna)

    @regression
    def mean_squared_error(
        self,
        outputs: GantrySeries,
        feedback: GantrySeries,
        dropna: bool = False,
        num_points: int = 1,
        multioutput: Literal["uniform_average", "raw_values"] = "uniform_average",
        squared: bool = True,
    ) -> pd.DataFrame:
        """
        Regression metric- mean squared error
        Args:
            outputs: predictions as a GantrySeries
            feedback: labels to compare against as a GantrySeries
            dropna: if True, drop rows with NaN values in result
            num_points: number of points to divide the time window of the GantrySeries into
            multioutput: type of averaging to use when computing the metric
                Can be one of "uniform_average", "raw_values"
            squared: if True, return the squared error
        Returns: pd.DataFrame of shape (num_points, 1) mean_squared_error
        """
        stat = "mean_squared_error"
        results = self._metric_query(
            outputs,
            feedback,
            stat,
            num_points=num_points,
            stat_kwargs={"multioutput": multioutput, "squared": squared},
        )
        return self._prepare_pandas_dataframe(stat, results, dropna=dropna)

    @categorical
    def confusion_matrix(
        self,
        outputs: GantrySeries,
        feedback: GantrySeries,
        dropna: bool = False,
        num_points: int = 1,
    ) -> pd.DataFrame:
        """
        Categorical metric - confusion matrix
        The confusion matrix is a matrix :math:`C` where :math:`C_{i, j}`
        represents the number of times a data point from the class :math:`i`
        was predicted to be in class :math:`j`.
        Args:
            outputs: predictions as a GantrySeries
            feedback: labels to compare against as a GantrySeries
            dropna: if True, drop rows with NaN values in result
            num_points: number of points to divide the time window of the GantrySeries into
        Returns: pd.DataFrame of shape (num_points, 1) confusion_matrix
        """
        stat = "confusion_matrix"
        results = self._metric_query(
            outputs,
            feedback,
            stat,
            num_points=num_points,
        )
        return self._prepare_pandas_dataframe(stat, results, dropna=dropna)

    @categorical
    def f1_score(
        self,
        outputs: GantrySeries,
        feedback: GantrySeries,
        dropna: bool = False,
        num_points: int = 1,
        average: Literal["micro"] = "micro",
    ) -> pd.DataFrame:
        """
        Categorical metric - F1 score

        It is computed as the harmonic mean of precision and recall:
        F1 = 2 * (precision * recall) / (precision + recall)
        In multiclass classification, this is the average of the F1 score for all available classes.

        Args:
            outputs: predictions as a GantrySeries
            feedback: labels to compare against as a GantrySeries
            dropna: if True, drop rows with NaN values in result
            num_points: number of points to divide the time window of the GantrySeries into
            average: type of averaging to use when computing the metric
        Returns: pd.DataFrame of shape (num_points, 1) f1_score
        """
        stat = "f1_score"
        results = self._metric_query(
            outputs,
            feedback,
            stat,
            num_points=num_points,
            stat_kwargs={"average": average},
        )
        return self._prepare_pandas_dataframe(stat, results, dropna=dropna)

    @regression
    def r2_score(
        self,
        outputs: GantrySeries,
        feedback: GantrySeries,
        dropna: bool = False,
        num_points: int = 1,
        multioutput: Literal[
            "uniform_average", "raw_values", "variance_weighted"
        ] = "uniform_average",
    ) -> float:
        """
        Regression metric- R^2 coefficient of determination
        Args:
            outputs: predictions as a GantrySeries
            feedback: labels to compare against as a GantrySeries
            dropna: if True, drop rows with NaN values in result
            num_points: number of points to divide the time window of the GantrySeries into
            multioutput: type of averaging to use when computing the metric
        Returns:
            float R^2 score.
        """
        stat = "r2_score"
        results = self._metric_query(
            outputs,
            feedback,
            stat,
            num_points=num_points,
            stat_kwargs={"multioutput": multioutput},
        )
        return self._prepare_pandas_dataframe(stat, results, dropna=dropna)

    @categorical
    def precision_score(
        self,
        outputs: GantrySeries,
        feedback: GantrySeries,
        dropna: bool = False,
        num_points: int = 1,
        average: Literal["micro"] = "micro",
    ) -> pd.DataFrame:
        """
        Categorical metric - precision score
        precision =
        (number of true positives) / ((number of true positives) + (number of false positives))
        Args:
            outputs: predictions as a GantrySeries
            feedback: labels to compare against as a GantrySeries
            dropna: if True, drop rows with NaN values in result
            num_points: number of points to divide the time window of the GantrySeries into
            average: type of averaging to use when computing the metric
        Returns: pd.DataFrame of shape (num_points, 1) precision_score
        """
        stat = "precision_score"
        results = self._metric_query(
            outputs,
            feedback,
            stat,
            num_points=num_points,
            stat_kwargs={"average": average},
        )
        return self._prepare_pandas_dataframe(stat, results, dropna=dropna)

    @categorical
    def recall_score(
        self,
        outputs: GantrySeries,
        feedback: GantrySeries,
        dropna: bool = False,
        num_points: int = 1,
        average: Literal["micro"] = "micro",
    ) -> pd.DataFrame:
        """
        Categorical metric - recall score
        recall =
        (number of true positives) / ((number of true positives) + (number of false negatives))
        Args:
            outputs: predictions as a GantrySeries
            feedback: labels to compare against as a GantrySeries
            dropna: if True, drop rows with NaN values in result
            num_points: number of points to divide the time window of the GantrySeries into
            average: type of averaging to use when computing the metric
        Returns: pd.DataFrame of shape (num_points, 1) recall_score
        """
        stat = "recall_score"
        results = self._metric_query(
            outputs,
            feedback,
            stat,
            num_points=num_points,
            stat_kwargs={"average": average},
        )
        return self._prepare_pandas_dataframe(stat, results, dropna=dropna)

    @score
    def roc_auc_score(
        self,
        outputs: GantrySeries,
        feedback: GantrySeries,
        dropna: bool = False,
        num_points: int = 1,
    ) -> pd.DataFrame:
        """
        Classification score metric - the area under the ROC curve
        Args:
            outputs: predictions as GantrySeries
            feedback: labels to compare against as a GantrySerires
            dropna: if True, drop rows with NaN values in result
            num_points: number of points to divide the time window of the GantrySeries into
        Returns: pd.DataFrame of shape (num_points, 1) roc_auc_score
        """
        stat = "roc_auc_score"
        results = self._metric_query(
            outputs,
            feedback,
            stat,
            num_points=num_points,
        )
        return self._prepare_pandas_dataframe(stat, results, dropna=dropna)
