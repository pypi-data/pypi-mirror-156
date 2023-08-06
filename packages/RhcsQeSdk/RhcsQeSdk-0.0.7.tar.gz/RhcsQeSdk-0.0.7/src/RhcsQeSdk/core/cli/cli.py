from src.RhcsQeSdk.core.cli.ceph.ceph import Ceph
from src.RhcsQeSdk.core.cli.cephadm.cephadm import CephAdm
from src.RhcsQeSdk.core.cli.rados.rados import Rados
from src.RhcsQeSdk.core.cli.radosgw_admin.radosgw_admin import Radosgw_admin
from src.RhcsQeSdk.core.cli.rbd.rbd import Rbd


class CLI:
    def __init__(self, base_cmd=""):
        """
        Module for initiaizing root modules for SDK layer.
        """
        self.ceph = Ceph(base_cmd)
        self.rados = Rados(base_cmd)
        self.radosgw_admin = Radosgw_admin(base_cmd)
        self.rbd = Rbd(base_cmd)
        self.cephadm = CephAdm(base_cmd)
        self.rbd_mirror = self.rbd.mirror
