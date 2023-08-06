class RedefineArgs:
    def __init__(self):
        pass

    def get_args(self, **kw):
        kw = kw.get("kw")
        step = kw.get("step")
        cls = step.get("class")
        method = step.get("method")
        component = step.get("component")
        redefine_method_name = f"{component}_{cls}_{method}"
        args = step.get("args")
        redefine_method = getattr(self, redefine_method_name)
        if redefine_method:
            args = redefine_method(kw=kw)
        return args

    def cephadm_cephadm_bootstrap(self, **kw):
        kw = kw.get("kw")
        step = kw.get("step")
        cluster_name = kw.get("cluster_name")
        ceph_cluster_dict = kw.get("ceph_cluster_dict")
        args = step.get("args")
        role = step.get("role")
        if len(role.split(":")) == 2:
            cluster_and_role = role.split(":")
            cluster_name = cluster_and_role[0]
            role = cluster_and_role[1]
        if args.get("registry-url"):
            args["registry-username"] = "cephuser"
            args["registry-password"] = "cephuser"
        if args.get("mon-ip"):
            ips = [
                ceph_cluster_dict[cluster_name]
                .get_node_by_hostname(args.get("mon-ip"))
                .ip_address
            ]
        else:
            ips = []
            nodes = ceph_cluster_dict[cluster_name].get_nodes("mon")
            for node in nodes:
                ips.append(node.ip_address)
        args["mon-ip"] = " ".join(ips)
        return args

    def ceph_orch_apply(self, **kw):
        kw = kw.get("kw")
        step = kw.get("step")
        args = step.get("args")
        role = step.get("role")
        service_name = args.get("service_name")
        if len(role.split(":")) == 2:
            cluster_and_role = role.split(":")
            # cluster_name = cluster_and_role[0]
            role = cluster_and_role[1]
        placement = args.get("placement", {})
        if placement:
            if "label" in placement:
                args["label"] = placement["label"]
            if "nodes" in placement:
                sep = placement.get("sep", " ")
                nodes = placement.get("nodes", "")
                nodes_str = f"{sep}".join(nodes)
                count = placement.get("count", "")
                if service_name == "rgw" and placement.get("count-per-host", ""):
                    count = placement.get("count-per-host", None)
                nodes_str = f"{count}{sep}{nodes_str}"
                args["nodes_str"] = nodes_str
        return args
