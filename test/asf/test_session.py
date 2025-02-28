#!/usr/bin/env python3

import unittest

from asfframework import tag_fixme_vpp_workers
from asfframework import VppTestCase, VppTestRunner
from asfframework import tag_run_solo
from vpp_ip_route import VppIpTable, VppIpRoute, VppRoutePath


@tag_fixme_vpp_workers
class TestSession(VppTestCase):
    """Session Test Case"""

    @classmethod
    def setUpClass(cls):
        super(TestSession, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        super(TestSession, cls).tearDownClass()

    def setUp(self):
        super(TestSession, self).setUp()

        self.vapi.session_enable_disable(is_enable=1)
        self.create_loopback_interfaces(2)

        table_id = 0

        for i in self.lo_interfaces:
            i.admin_up()

            if table_id != 0:
                tbl = VppIpTable(self, table_id)
                tbl.add_vpp_config()

            i.set_table_ip4(table_id)
            i.config_ip4()
            table_id += 1

        # Configure namespaces
        self.vapi.app_namespace_add_del(
            namespace_id="0", sw_if_index=self.loop0.sw_if_index
        )
        self.vapi.app_namespace_add_del(
            namespace_id="1", sw_if_index=self.loop1.sw_if_index
        )

    def tearDown(self):
        for i in self.lo_interfaces:
            i.unconfig_ip4()
            i.set_table_ip4(0)
            i.admin_down()

        super(TestSession, self).tearDown()
        self.vapi.session_enable_disable(is_enable=1)

    def test_segment_manager_alloc(self):
        """Session Segment Manager Multiple Segment Allocation"""

        # Add inter-table routes
        ip_t01 = VppIpRoute(
            self,
            self.loop1.local_ip4,
            32,
            [VppRoutePath("0.0.0.0", 0xFFFFFFFF, nh_table_id=1)],
        )
        ip_t10 = VppIpRoute(
            self,
            self.loop0.local_ip4,
            32,
            [VppRoutePath("0.0.0.0", 0xFFFFFFFF, nh_table_id=0)],
            table_id=1,
        )
        ip_t01.add_vpp_config()
        ip_t10.add_vpp_config()

        # Start builtin server and client with small private segments
        uri = "tcp://" + self.loop0.local_ip4 + "/1234"
        error = self.vapi.cli(
            "test echo server appns 0 fifo-size 64 "
            + "private-segment-size 1m uri "
            + uri
        )
        if error:
            self.logger.critical(error)
            self.assertNotIn("failed", error)

        error = self.vapi.cli(
            "test echo client nclients 100 appns 1 "
            + "no-output fifo-size 64 syn-timeout 2 "
            + "private-segment-size 1m uri "
            + uri
        )
        if error:
            self.logger.critical(error)
            self.assertNotIn("failed", error)

        if self.vpp_dead:
            self.assert_equal(0)

        # Delete inter-table routes
        ip_t01.remove_vpp_config()
        ip_t10.remove_vpp_config()


@tag_fixme_vpp_workers
class TestSessionUnitTests(VppTestCase):
    """Session Unit Tests Case"""

    @classmethod
    def setUpClass(cls):
        super(TestSessionUnitTests, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        super(TestSessionUnitTests, cls).tearDownClass()

    def setUp(self):
        super(TestSessionUnitTests, self).setUp()
        self.vapi.session_enable_disable(is_enable=1)

    def test_session(self):
        """Session Unit Tests"""
        error = self.vapi.cli("test session all")

        if error:
            self.logger.critical(error)
        self.assertNotIn("failed", error)

    def tearDown(self):
        super(TestSessionUnitTests, self).tearDown()
        self.vapi.session_enable_disable(is_enable=0)


@tag_run_solo
class TestSegmentManagerTests(VppTestCase):
    """SVM Fifo Unit Tests Case"""

    @classmethod
    def setUpClass(cls):
        super(TestSegmentManagerTests, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        super(TestSegmentManagerTests, cls).tearDownClass()

    def setUp(self):
        super(TestSegmentManagerTests, self).setUp()

    def test_segment_manager(self):
        """Segment manager Tests"""
        error = self.vapi.cli("test segment-manager all")

        if error:
            self.logger.critical(error)
        self.assertNotIn("failed", error)

    def tearDown(self):
        super(TestSegmentManagerTests, self).tearDown()


@tag_run_solo
class TestSvmFifoUnitTests(VppTestCase):
    """SVM Fifo Unit Tests Case"""

    @classmethod
    def setUpClass(cls):
        super(TestSvmFifoUnitTests, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        super(TestSvmFifoUnitTests, cls).tearDownClass()

    def setUp(self):
        super(TestSvmFifoUnitTests, self).setUp()

    def test_svm_fifo(self):
        """SVM Fifo Unit Tests"""
        error = self.vapi.cli("test svm fifo all")

        if error:
            self.logger.critical(error)
        self.assertNotIn("failed", error)

    def tearDown(self):
        super(TestSvmFifoUnitTests, self).tearDown()


if __name__ == "__main__":
    unittest.main(testRunner=VppTestRunner)
