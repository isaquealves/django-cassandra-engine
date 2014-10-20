from cassandra.cluster import Cluster
from djangotoolbox.db.base import FakeCursor
from mock import patch

from django.db import connections
from django.test import TestCase

from django_cassandra_engine.connection import CassandraConnection


class CassandraConnectionTestCase(TestCase):

    def setUp(self):
        connection = connections['cassandra']
        self.connection = CassandraConnection(**connection.settings_dict)

    def test_cursor(self):

        self.assertIsInstance(self.connection.cursor(), FakeCursor)

    def test_connected_to_db(self):

        from cqlengine import connection as cql_connection

        self.assertIsInstance(cql_connection.cluster, Cluster)
        self.assertIsNotNone(cql_connection.session)

    def test_session_property(self):

        from cqlengine import connection as cql_connection

        self.assertEqual(self.connection.session, cql_connection.session)

    def test_cluster_property(self):

        from cqlengine import connection as cql_connection

        self.assertEqual(self.connection.cluster, cql_connection.cluster)

    def test_connection_options(self):
        connection = connections['cassandra']
        connection_options = connection.settings_dict['OPTIONS']['connection']
        self.assertEqual(
            self.connection.connection_options, connection_options)

    @patch("django_cassandra_engine.connection.connection")
    def test_connection_setup_called_first_time_with_proper_options(
            self, connection_mock):

        settings = connections['cassandra'].settings_dict
        connection_mock.cluster = None
        connection = CassandraConnection(**settings)

        connection_mock.setup.assert_called_once_with(
            connection.hosts, connection.keyspace,
            **settings['OPTIONS']['connection'])

    @patch("django_cassandra_engine.connection.connection")
    def test_connection_setup_called_second_time(
            self, connection_mock):

        settings = connections['cassandra'].settings_dict
        connection_mock.cluster = Cluster()
        CassandraConnection(**settings)

        self.assertFalse(connection_mock.setup.called)