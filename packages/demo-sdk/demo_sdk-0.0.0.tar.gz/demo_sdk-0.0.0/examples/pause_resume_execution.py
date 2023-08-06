import copy
import logging

import yaml
from libcloud.compute.providers import get_driver
from libcloud.compute.types import Provider

from src.client.ceph import Ceph
from src.controllers.install_prereq import install_prerequisites
from src.controllers.installers import deploy_ceph
from src.scripts.run_test_suite import RunTestSuite
from src.utilities.loader import LoaderMixin
from src.utilities.mail_sender import mail_sender
from src.utilities.metadata import Metadata

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(name)s:%(lineno)d - %(message)s"
)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
stream_handler.setLevel(logging.DEBUG)
logger.addHandler(stream_handler)


def get_libcloud_driver():
    cred_path = "credentials.yaml"
    cred = LoaderMixin().load_file(cred_path).get("openstack_credentials")
    openstack = get_driver(Provider.OPENSTACK)
    driver = openstack(
        cred.get("username"),
        cred.get("password"),
        ex_tenant_name=cred.get("tenant_name", "ceph-ci"),
        ex_force_auth_url=cred.get("auth-url"),
        ex_force_auth_version=cred.get("auth-version", "3.x_password"),
        ex_force_service_region=cred.get("service_region", "regionOne"),
        ex_domain_name=cred.get("domain", "redhat.com"),
        ex_tenant_domain_id=cred.get("tenant-domain-id"),
    )
    return driver


def create_vm_nodes(vm_nodes):
    clusters_dict = copy.deepcopy(vm_nodes)
    driver = get_libcloud_driver()
    for node_name, node_dict in clusters_dict.get("vm_nodes").items():
        uuid = node_dict.pop("uuid")
        node_dict["node_obj"] = driver.ex_get_node_details(uuid)
    return clusters_dict


if __name__ == "__main__":
    # place the dict printed in terminal from method print_vm_nodes_for_resuming
    input_file = open("src/models/outputs/clusters_dict.yaml", "r")
    vm_nodes = yaml.safe_load(input_file)
    vm_nodes = create_vm_nodes(vm_nodes)
    ceph = Ceph(vm_nodes)
    Metadata(ceph=ceph)
    infra_spec = "rbd/5node_rbd_mirror-conf.yaml"
    suite_config = "rbd/test_rbd_twoway_mirroring.yaml"
    prerequisite = "prerequisite.yaml"

    logger.info(f"Provisioned nodes are {vm_nodes}")

    ceph = install_prerequisites(vm_nodes, infra_spec, prerequisite)
    logger.info("Done with installing prerequisites")

    deploy_ceph()
    logger.info(f"Configured ceph clusters are {ceph}")

    run_test_suite_obj = RunTestSuite(suite_config, ceph)
    tests_output = run_test_suite_obj.run_tests()
    mail_sender(suite_config, tests_output)
