import mock
import pandas as pd
import pytest

from gantry.query.core.metric import GantryMetric


@pytest.fixture
def gantry_metric_obj(api_client_obj):
    return GantryMetric(api_client_obj)


@pytest.mark.parametrize("num_points", [-2, -1, 0])
def test_metric_query_invalid_num_points(num_points, gantry_metric_obj, series_obj_factory):
    series_obj_1 = series_obj_factory("str")
    series_obj_2 = series_obj_factory("str")
    with pytest.raises(ValueError):
        gantry_metric_obj._metric_query(
            outputs=series_obj_1,
            feedback=series_obj_2,
            stat="this-is-not-used",
            num_points=num_points,
        )


def test_check_comparable_invalid_series_filters(
    gantry_metric_obj, series_obj_factory, api_client_obj, query_info_obj
):
    parent_dataframe_1 = mock.Mock(api_client=api_client_obj, query_info=query_info_obj)
    parent_dataframe_2 = mock.Mock(api_client=api_client_obj, query_info=query_info_obj)
    parent_dataframe_1.filters = ["some-filter"]
    parent_dataframe_2.filters = ["some-other-filter"]

    series_obj_1 = series_obj_factory("str", parent_dataframe=parent_dataframe_1)
    series_obj_2 = series_obj_factory("str", parent_dataframe=parent_dataframe_2)

    with pytest.raises(ValueError):
        gantry_metric_obj._metric_query(
            outputs=series_obj_1,
            feedback=series_obj_2,
            stat="this-is-not-used",
        )


@pytest.mark.parametrize("dropna", [True, False])
def test_empty_results_returns_empty_df(dropna, gantry_metric_obj):
    df = gantry_metric_obj._prepare_pandas_dataframe(stat="not-used", results=[], dropna=dropna)
    assert isinstance(df, pd.DataFrame)
    assert df.empty


@pytest.mark.parametrize("dropna", [False, True])
@pytest.mark.parametrize("num_points", [1, 2, 10])
@mock.patch("gantry.query.core.metric.GantryMetric._metric_query")
def test_accuracy_score(mock_query, num_points, dropna, gantry_metric_obj, series_obj_factory):
    stat = "accuracy_score"
    series_obj_1 = series_obj_factory("str")
    series_obj_2 = series_obj_factory("str")
    timestamp = "2022-03-20T00:00:00"
    mock_query.return_value = [{"time_stamp": timestamp, "value": 0.5}]
    result = gantry_metric_obj.accuracy_score(
        series_obj_1, series_obj_2, num_points=num_points, dropna=dropna
    )
    assert isinstance(result, pd.DataFrame)
    assert result.shape == (1, 1)
    assert result.columns.tolist() == [stat]
    assert result.index.name == "timestamp"
    result_score = result.loc[result.index == timestamp, stat].values[0]
    assert result_score == 0.5
    mock_query.assert_called_once_with(
        series_obj_1,
        series_obj_2,
        stat,
        num_points=num_points,
    )


@pytest.mark.parametrize("dropna", [False, True])
@pytest.mark.parametrize("num_points", [1, 2, 10])
@pytest.mark.parametrize("multioutput", ["uniform_average", "raw_values", None])
@pytest.mark.parametrize("squared", [False, True])
@mock.patch("gantry.query.core.metric.GantryMetric._metric_query")
def test_mean_squared_error(
    mock_query, squared, multioutput, num_points, dropna, gantry_metric_obj, series_obj_factory
):

    stat = "mean_squared_error"
    series_obj_1 = series_obj_factory("float")
    series_obj_2 = series_obj_factory("float")
    timestamp = "2022-03-20T00:00:00"
    mock_query.return_value = [{"time_stamp": timestamp, "value": 0.99}]
    result = gantry_metric_obj.mean_squared_error(
        series_obj_1,
        series_obj_2,
        multioutput=multioutput,
        squared=squared,
        num_points=num_points,
        dropna=dropna,
    )
    assert isinstance(result, pd.DataFrame)
    assert result.columns.tolist() == [stat]
    result_score = result.loc[result.index == timestamp, stat].values[0]
    assert result_score == 0.99
    mock_query.assert_called_once_with(
        series_obj_1,
        series_obj_2,
        stat,
        num_points=num_points,
        stat_kwargs={"multioutput": multioutput, "squared": squared},
    )


@pytest.mark.parametrize("dropna", [False, True])
@pytest.mark.parametrize("num_points", [1, 2, 10])
@mock.patch("gantry.query.core.metric.GantryMetric._metric_query")
def test_confusion_matrix(mock_query, num_points, dropna, gantry_metric_obj, series_obj_factory):
    stat = "confusion_matrix"
    series_obj_1 = series_obj_factory("int")
    series_obj_2 = series_obj_factory("int")
    timestamp = "2022-03-20T00:00:00"
    mock_query.return_value = [{"time_stamp": timestamp, "value": [[1, 2], [3, 4]]}]
    result = gantry_metric_obj.confusion_matrix(
        series_obj_1, series_obj_2, num_points=num_points, dropna=dropna
    )
    assert isinstance(result, pd.DataFrame)
    assert result.columns.tolist() == [stat]
    result_score = result.loc[result.index == timestamp, stat].values[0]
    assert result_score == [[1, 2], [3, 4]]
    mock_query.assert_called_once_with(
        series_obj_1,
        series_obj_2,
        stat,
        num_points=num_points,
    )


@pytest.mark.parametrize("method", ["precision_score", "recall_score", "f1_score"])
@pytest.mark.parametrize("dropna", [False, True])
@pytest.mark.parametrize("num_points", [1, 2, 10])
@mock.patch("gantry.query.core.metric.GantryMetric._metric_query")
def test_f1_score_precision_score_recall_score(
    mock_query, num_points, dropna, method, gantry_metric_obj, series_obj_factory
):
    stat = method
    average = "micro"
    series_obj_1 = series_obj_factory("int")
    series_obj_2 = series_obj_factory("int")
    timestamp = "2022-03-20T00:00:00"
    mock_query.return_value = [{"time_stamp": timestamp, "value": 0.5}]
    result = getattr(gantry_metric_obj, method)(
        series_obj_1, series_obj_2, average=average, num_points=num_points, dropna=dropna
    )
    assert isinstance(result, pd.DataFrame)
    assert result.shape == (1, 1)
    assert result.columns.tolist() == [stat]
    assert result.index.name == "timestamp"
    result_score = result.loc[result.index == timestamp, stat].values[0]
    assert result_score == 0.5
    mock_query.assert_called_once_with(
        series_obj_1,
        series_obj_2,
        stat,
        num_points=num_points,
        stat_kwargs={"average": average},
    )


@pytest.mark.parametrize("dropna", [False, True])
@pytest.mark.parametrize("num_points", [1, 2, 10])
@pytest.mark.parametrize("multioutput", ["uniform_average", "raw_values", None])
@mock.patch("gantry.query.core.metric.GantryMetric._metric_query")
def test_r2_score(
    mock_query, multioutput, num_points, dropna, gantry_metric_obj, series_obj_factory
):

    stat = "r2_score"
    series_obj_1 = series_obj_factory("float")
    series_obj_2 = series_obj_factory("float")
    timestamp = "2022-03-20T00:00:00"
    mock_query.return_value = [{"time_stamp": timestamp, "value": 0.99}]
    result = gantry_metric_obj.r2_score(
        series_obj_1,
        series_obj_2,
        multioutput=multioutput,
        num_points=num_points,
        dropna=dropna,
    )
    assert isinstance(result, pd.DataFrame)
    assert result.columns.tolist() == [stat]
    result_score = result.loc[result.index == timestamp, stat].values[0]
    assert result_score == 0.99
    mock_query.assert_called_once_with(
        series_obj_1,
        series_obj_2,
        stat,
        num_points=num_points,
        stat_kwargs={"multioutput": multioutput},
    )


@pytest.mark.parametrize("dropna", [False, True])
@pytest.mark.parametrize("num_points", [1, 2, 10])
@mock.patch("gantry.query.core.metric.GantryMetric._metric_query")
def test_roc_auc_score(mock_query, num_points, dropna, gantry_metric_obj, series_obj_factory):
    stat = "roc_auc_score"
    series_obj_1 = series_obj_factory("float")
    series_obj_2 = series_obj_factory("bool")
    timestamp = "2022-03-20T00:00:00"
    mock_query.return_value = [{"time_stamp": timestamp, "value": 0.68}]
    result = gantry_metric_obj.roc_auc_score(
        series_obj_1, series_obj_2, num_points=num_points, dropna=dropna
    )
    assert isinstance(result, pd.DataFrame)
    assert result.columns.tolist() == [stat]
    result_score = result.loc[result.index == timestamp, stat].values[0]
    assert result_score == 0.68
    mock_query.assert_called_once_with(
        series_obj_1,
        series_obj_2,
        stat,
        num_points=num_points,
    )
