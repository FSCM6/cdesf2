from cdesf2.clustering import DenStream, NoMicroClusterException
from cdesf2.data_structures import MicroCluster
from cdesf2.data_structures import Case
from cdesf2.utils import extract_case_distances, initialize_graph
import networkx as nx
from datetime import datetime
import numpy as np
import pytest


class TestDenstream:
    @pytest.fixture
    def denstream(self):
        denstream = DenStream(2, 0.15, 0.3, 0.1, 4, 1000)
        return denstream

    @pytest.fixture
    def cases_list(self):
        case_list = []
        case = Case('1')
        case.set_activity('activityA', datetime(2015, 5, 10, 8, 00, 00))
        case.set_activity('activityB', datetime(2015, 5, 10, 8, 00, 10))
        case.set_activity('activityC', datetime(2015, 5, 10, 8, 00, 20))
        case_list.append(case)

        case = Case('2')
        case.set_activity('activityA', datetime(2015, 5, 10, 8, 00, 00))
        case.set_activity('activityB', datetime(2015, 5, 10, 8, 00, 10))
        case_list.append(case)

        case = Case('3')
        case.set_activity('activityA', datetime(2015, 5, 10, 8, 00, 00))
        case.set_activity('activityB', datetime(2015, 5, 10, 8, 00, 10))
        case.set_activity('activityC', datetime(2015, 5, 10, 8, 00, 20))
        case.set_activity('activityD', datetime(2015, 5, 10, 8, 00, 30))
        case_list.append(case)

        case = Case('4')
        case.set_activity('activityA', datetime(2015, 5, 10, 8, 00, 00))
        case.set_activity('activityB', datetime(2015, 5, 10, 8, 00, 10))
        case.set_activity('activityC', datetime(2015, 5, 10, 8, 00, 20))
        case_list.append(case)

        return case_list

    def test_initial_value_den(self, denstream):
        assert denstream.n_features == 2
        assert denstream.lambda_ == 0.15
        assert denstream.beta == 0.3
        assert denstream.epsilon == 0.1
        assert denstream.mu == 4
        assert denstream.p_micro_clusters == []
        assert denstream.o_micro_clusters == []
        assert denstream.time == 0
        assert denstream.all_cases == {}
        assert denstream.stream_speed == 1000

    def test_no_value_den(self):
        with pytest.raises(Exception):
            assert DenStream()

    def test_euclidean_distance(self):
        point_1 = np.array([0, 0])
        point_2 = np.array([0, 1])
        euc_dist = DenStream.euclidean_distance(point_1, point_2)
        assert type(euc_dist) is np.float64
        assert euc_dist == 1

    def test_find_closest_mc(self, denstream):
        point = np.array([0, 0])

        with pytest.raises(NoMicroClusterException):
            assert denstream.find_closest_mc(point, denstream.p_micro_clusters)
        with pytest.raises(NoMicroClusterException):
            assert denstream.find_closest_mc(point, denstream.o_micro_clusters)

        micro_cluster = MicroCluster(0, 2, 0, 0.15)
        micro_cluster.CF = np.array([0, 1])
        micro_cluster.weight = 2
        denstream.p_micro_clusters.append(micro_cluster)

        micro_cluster = MicroCluster(1, 2, 0, 0.15)
        micro_cluster.CF = np.array([0, 1])
        micro_cluster.weight = 1
        denstream.p_micro_clusters.append(micro_cluster)

        i, mc, dist = denstream.find_closest_mc(point, denstream.p_micro_clusters)
        assert i == 0
        assert np.all(mc.CF == [0, 1])
        assert mc.weight == 2
        assert dist == 0.5

        point = np.array([0, 2])
        micro_cluster = MicroCluster(2, 2, 1, 0.15)
        micro_cluster.CF = np.array([0, 1])
        micro_cluster.weight = 2
        denstream.p_micro_clusters = []
        denstream.p_micro_clusters.append(micro_cluster)

        micro_cluster = MicroCluster(3, 2, 1, 0.15)
        micro_cluster.CF = np.array([0, 1])
        micro_cluster.weight = 1
        denstream.p_micro_clusters.append(micro_cluster)

        i, mc, dist = denstream.find_closest_mc(point, denstream.p_micro_clusters)
        assert i == 1
        assert np.all(mc.CF == [0, 1])
        assert mc.weight == 1
        assert dist == 1

        micro_cluster = MicroCluster(4, 2, 1, 0.15)
        micro_cluster.CF = np.array([0, 3])
        micro_cluster.weight = 2
        denstream.o_micro_clusters = []
        denstream.o_micro_clusters.append(micro_cluster)

        micro_cluster = MicroCluster(5, 2, 1, 0.15)
        micro_cluster.CF = np.array([0, 1])
        micro_cluster.weight = 3
        denstream.o_micro_clusters.append(micro_cluster)

        micro_cluster = MicroCluster(6, 2, 1, 0.15)
        micro_cluster.CF = np.array([0, 2])
        micro_cluster.weight = 1
        denstream.o_micro_clusters.append(micro_cluster)

        point = np.array([0, 3])
        i, mc, dist = denstream.find_closest_mc(point, denstream.o_micro_clusters)
        assert i == 2
        assert np.all(mc.CF == [0, 2])
        assert mc.weight == 1

    def test_add_point(self, denstream):
        case_list = []
        case_1 = Case('1')
        case_1.set_activity('activityA', datetime(2015, 5, 10, 8, 00, 00))
        case_1.set_activity('activityB', datetime(2015, 5, 10, 8, 00, 10))
        case_1.set_activity('activityC', datetime(2015, 5, 10, 8, 00, 20))
        case_list.append(case_1)

        case_2 = Case('2')
        case_2.set_activity('activityA', datetime(2015, 5, 10, 8, 00, 00))
        case_2.set_activity('activityB', datetime(2015, 5, 10, 8, 00, 10))
        case_list.append(case_2)

        graph = nx.DiGraph()
        graph = initialize_graph(graph, case_list)

        case_3 = Case('3')
        case_3.set_activity('activityA', datetime(2015, 5, 10, 8, 00, 00))
        case_3.set_activity('activityB', datetime(2015, 5, 10, 8, 00, 10))
        case_3.set_activity('activityC', datetime(2015, 5, 10, 8, 00, 20))
        case_3.set_activity('activityD', datetime(2015, 5, 10, 8, 00, 30))

        trace_distance, time_distance = extract_case_distances(graph, case_3)
        case_3.graph_distance = trace_distance
        case_3.time_distance = time_distance

        micro_cluster = MicroCluster(10, 2, 0, 0.15)
        micro_cluster.CF = np.array([0.5, -0.5])
        micro_cluster.CF2 = np.array([0.5, -0.1])
        micro_cluster.weight = 10
        denstream.p_micro_clusters.append(micro_cluster)

        micro_cluster = MicroCluster(11, 2, 0, 0.15)
        micro_cluster.CF = np.array([0.0, 0.0])
        micro_cluster.CF2 = np.array([0.0, 0.0])
        micro_cluster.weight = 5
        denstream.o_micro_clusters.append(micro_cluster)
        denstream.mc_id = 2

        mc_id = denstream.add_point(case_3)
        assert mc_id == 2
        assert len(denstream.o_micro_clusters) == 2
        assert denstream.o_micro_clusters[1].radius == 0
        assert denstream.o_micro_clusters[1].weight == 1
        assert np.all(denstream.o_micro_clusters[1].CF == case_3.point)
        assert np.all(denstream.o_micro_clusters[1].CF2 == case_3.point * case_3.point)

        cf = denstream.o_micro_clusters[1].CF.copy()
        cf2 = denstream.o_micro_clusters[1].CF2.copy()
        mc_id = denstream.add_point(case_3)
        assert mc_id == 2
        assert len(denstream.o_micro_clusters) == 1
        assert len(denstream.p_micro_clusters) == 2
        assert denstream.p_micro_clusters[1].weight == 2
        assert np.all(denstream.p_micro_clusters[1].CF == cf + case_3.point)
        assert np.all(denstream.p_micro_clusters[1].CF2 == cf2 + case_3.point * case_3.point)

    def test_decay_micro_clusters(self, denstream):
        micro_cluster = MicroCluster(0, 2, 0, 0.15)
        micro_cluster.CF = np.array([5.0, 5.0])
        micro_cluster.CF2 = np.array([1.0, 1.0])
        micro_cluster.weight = 5
        denstream.p_micro_clusters.append(micro_cluster)

        micro_cluster = MicroCluster(1, 2, 0, 0.15)
        micro_cluster.CF = np.array([1.0, 5.0])
        micro_cluster.CF2 = np.array([3.0, 0.0])
        micro_cluster.weight = 10
        denstream.p_micro_clusters.append(micro_cluster)

        micro_cluster = MicroCluster(2, 2, 0, 0.15)
        micro_cluster.CF = np.array([0.0, 0.0])
        micro_cluster.CF2 = np.array([10.0, 2.0])
        micro_cluster.weight = 3
        denstream.p_micro_clusters.append(micro_cluster)

        denstream.decay_micro_clusters(0)
        assert np.all(denstream.p_micro_clusters[0].CF == np.array([5, 5]))
        assert np.all(denstream.p_micro_clusters[0].CF2 == np.array([1, 1]))
        assert np.all(denstream.p_micro_clusters[0].weight == 5)

        assert np.all(denstream.p_micro_clusters[1].CF == np.array([1, 5]) * 2 ** (-0.15))
        assert np.all(denstream.p_micro_clusters[1].CF2 == np.array([3, 0]) * 2 ** (-0.15))
        assert np.all(denstream.p_micro_clusters[1].weight == 10 * 2 ** (-0.15))

        assert np.all(denstream.p_micro_clusters[2].CF == np.array([0, 0]) * 2 ** (-0.15))
        assert np.all(denstream.p_micro_clusters[2].CF2 == np.array([10, 2]) * 2 ** (-0.15))
        assert np.all(denstream.p_micro_clusters[2].weight == 3 * 2 ** (-0.15))

    def test_dbscan(self, denstream, cases_list):
        graph = nx.DiGraph()
        graph = initialize_graph(graph, cases_list)
        for case in cases_list:
            trace_distance, time_distance = extract_case_distances(graph, case)
            case.graph_distance = trace_distance
            case.time_distance = time_distance

        denstream.dbscan(cases_list)
        assert len(denstream.p_micro_clusters) == 1
        assert denstream.all_cases.keys() == {'1', '4'}
        new_p_mc = denstream.p_micro_clusters[0]
        assert new_p_mc.weight == 2
        assert new_p_mc.creation_time == 0
        assert new_p_mc.lambda_ == 0.15

    # def test_train(self, denstream, cases_list):
    #     case_1 = cases_list[0]
    #     with pytest.raises(Exception):
    #         assert denstream.train(case_1)
    #     assert denstream.all_cases == {'1'}
    #     assert denstream.time == 1
    #     denstream.initiated = True
    #
    #     micro_cluster = MicroCluster(2, 0, 0.15, 1000)
    #     micro_cluster.case_ids.add('1')
    #     micro_cluster.case_ids.add('2')
    #     micro_cluster.weight = 1
    #     denstream.p_micro_clusters[1] = micro_cluster
    #
    #     micro_cluster = MicroCluster(2, 0, 0.15, 1000)
    #     micro_cluster.case_ids.add('1')
    #     micro_cluster.case_ids.add('3')
    #     micro_cluster.weight = 1
    #     denstream.p_micro_clusters[2] = micro_cluster
    #
    #     denstream.train(case_1)
    #     assert denstream.all_cases == {'1'}
    #     p_mc = denstream.p_micro_clusters[1]
    #     assert p_mc.case_ids == {'2'}
    #     p_mc = denstream.p_micro_clusters[2]
    #     assert p_mc.case_ids == {'3', '1'}
    #
    #     denstream.train(case_1)
    #     assert p_mc.case_ids == {'3'}
    #
    # def test_generate_clusters(self, denstream):

    # def test_generate_outlier_clusters(self, denstream):
    #     assert denstream.generate_outlier_clusters() == []
    #
    #     micro_cluster = MicroCluster(2, 0, 0.15, 1000)
    #     micro_cluster.weight = 3
    #     micro_cluster.case_ids = {'1', '2', '3'}
    #     denstream.o_micro_clusters[0] = micro_cluster
    #
    #     micro_cluster = MicroCluster(2, 0, 0.15, 1000)
    #     micro_cluster.weight = 4
    #     micro_cluster.case_ids = {'1', '2', '3', '4'}
    #     denstream.o_micro_clusters[1] = micro_cluster
    #
    #     cluster_list = denstream.generate_outlier_clusters()
    #
    #     cluster = cluster_list[0]
    #     assert cluster.id == 0
    #     assert np.all(cluster.centroid == [0, 0])
    #     assert cluster.weight == 3
    #     assert cluster.case_ids == {'1', '2', '3'}
    #
    #     cluster = cluster_list[1]
    #     assert cluster.id == 1
    #     assert np.all(cluster.centroid == [0, 0])
    #     assert cluster.weight == 4
    #     assert cluster.case_ids == {'1', '2', '3', '4'}