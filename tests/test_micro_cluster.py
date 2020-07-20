from cdesf2.data_structures import MicroCluster
from cdesf2.data_structures import Case
from cdesf2.utils import initialize_graph, extract_case_distances
from datetime import datetime
from math import sqrt
import networkx as nx
import numpy as np
import pytest


def test_initial_value():
    micro_cluster = MicroCluster(0, 2, 0, 0.15)
    assert type(micro_cluster.CF) is np.ndarray
    assert type(micro_cluster.CF2) is np.ndarray
    assert np.all(micro_cluster.CF == [0, 0])
    assert np.all(micro_cluster.CF2 == [0, 0])
    assert micro_cluster.weight == 0
    assert type(micro_cluster.creation_time) is int
    assert micro_cluster.creation_time == 0
    assert type(micro_cluster.lambda_) is float
    assert micro_cluster.lambda_ == 0.15


def test_no_value():
    with pytest.raises(Exception):
        assert MicroCluster()


def test_centroid():
    micro_cluster = MicroCluster(0, 2, 0, 0.15)
    micro_cluster.weight = 1
    assert type(micro_cluster.centroid) is np.ndarray
    assert np.all(micro_cluster.centroid == 0)
    micro_cluster.CF = np.array([0, 1])
    assert np.all(micro_cluster.centroid == [0, 1])
    micro_cluster.weight = 2
    assert np.all(micro_cluster.centroid == [0, 0.5])


def test_radius():
    micro_cluster = MicroCluster(0, 2, 0, 0.15)
    micro_cluster.weight = 1
    micro_cluster.CF = np.array([0, 0])
    micro_cluster.CF2 = np.array([0, 1])

    assert type(micro_cluster.radius) is np.float64
    assert micro_cluster.radius == 1.0

    micro_cluster.CF = np.array([0, 0])
    micro_cluster.CF2 = np.array([0, 2])
    assert micro_cluster.radius == sqrt(2)

    micro_cluster.CF = np.array([0, 1])
    micro_cluster.CF2 = np.array([0, 2])
    assert micro_cluster.radius == 1

    micro_cluster.CF = np.array([0, 2])
    micro_cluster.CF2 = np.array([0, 2])
    assert micro_cluster.radius == 0

    micro_cluster.CF = np.array([1, 2])
    micro_cluster.CF2 = np.array([0, 0])
    assert micro_cluster.radius == 0


def test_radius_with_new_point():
    micro_cluster = MicroCluster(0, 2, 0, 0.15)
    point1 = np.array([0, 1])
    radius = micro_cluster.radius_with_new_point(point1)
    assert type(radius) is np.float64
    assert radius == 0

    micro_cluster.CF = np.array([0, 0])
    micro_cluster.CF2 = np.array([0, 1])
    point1 = np.array([0, 1])
    radius = micro_cluster.radius_with_new_point(point1)
    assert radius == 1

    micro_cluster.CF = np.array([0, 0])
    micro_cluster.CF2 = np.array([1, 1])
    point1 = np.array([0, 1])
    radius = micro_cluster.radius_with_new_point(point1)
    micro_cluster.CF = np.array([0, 1])
    micro_cluster.CF2 = np.array([1, 2])
    micro_cluster.weight = 1
    assert radius == micro_cluster.radius

    micro_cluster.CF = np.array([1, 1])
    micro_cluster.CF2 = np.array([0, 0])
    point1 = np.array([1, 1])
    radius = micro_cluster.radius_with_new_point(point1)
    micro_cluster.CF = np.array([2, 2])
    micro_cluster.CF2 = np.array([1, 1])
    micro_cluster.weight = 1
    assert radius == 0
    assert radius == micro_cluster.radius


def test_update():
    case_list = []
    micro_cluster = MicroCluster(0, 2, 0, 0.15)

    case = Case('1')
    case.set_activity('activityA', datetime(2015, 5, 10, 8, 00, 00))
    case.set_activity('activityD', datetime(2015, 5, 10, 8, 33, 20))
    case.set_activity('activityE', datetime(2015, 5, 10, 14, 6, 40))
    case_list.append(case)

    case = Case('2')
    case.set_activity('activityA', datetime(2015, 5, 10, 1, 00, 00))
    case.set_activity('activityB', datetime(2015, 5, 10, 14, 40, 00))
    case.set_activity('activityD', datetime(2015, 5, 10, 15, 5, 00))
    case_list.append(case)

    graph = nx.DiGraph()
    graph = initialize_graph(graph, case_list)

    case = Case('3')
    case.set_activity('activityA', datetime(2015, 5, 10, 8, 00, 00))
    case.set_activity('activityB', datetime(2015, 5, 10, 8, 13, 00))
    case.set_activity('activityC', datetime(2015, 5, 10, 8, 13, 00))
    case.graph_distance, case.time_distance = extract_case_distances(graph, case)

    cf = micro_cluster.CF.copy()
    cf2 = micro_cluster.CF2.copy()
    weight = micro_cluster.weight
    micro_cluster.update(case)

    assert np.all(micro_cluster.CF == cf + case.point)
    assert np.all(micro_cluster.CF2 == cf2 + case.point*case.point)
    assert micro_cluster.weight == weight + 1

    case = case_list[0]
    case.graph_distance, case.time_distance = extract_case_distances(graph, case)
    cf = micro_cluster.CF.copy()
    cf2 = micro_cluster.CF2.copy()
    weight = micro_cluster.weight
    micro_cluster.update(case)

    assert np.all(micro_cluster.CF == cf + case.point)
    assert np.all(micro_cluster.CF2 == cf2 + case.point * case.point)
    assert micro_cluster.weight == weight + 1


def test_decay():
    micro_cluster = MicroCluster(0, 2, 0, 0.15)
    micro_cluster.weight = 1
    micro_cluster.CF = np.array([0.5, 0.7])
    micro_cluster.CF2 = np.array([0.0, 1.0])

    cf = micro_cluster.CF.copy()
    cf2 = micro_cluster.CF2.copy()
    weight = micro_cluster.weight
    micro_cluster.decay()

    assert np.all(micro_cluster.CF == cf * (2**(-0.15)))
    assert np.all(micro_cluster.CF2 == cf2 * (2**(-0.15)))
    assert micro_cluster.weight == weight * (2**(-0.15))
