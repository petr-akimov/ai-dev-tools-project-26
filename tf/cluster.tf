resource "cloudru_evolution_iam_service_account" "cluster_sa" {
  name        = "k8s-cluster-sa"
  description = "Service account for managed k8s cluster"
  target = {
    project_id = var.project_id
  }
}

resource "cloudru_evolution_iam_permission" "k8s_admin_perm" {
  resource_id = var.project_id
  subject_id  = cloudru_evolution_iam_service_account.cluster_sa.id

  role_identifier = {
    role_name = "k8s.admin"
  }
}

resource "cloudru_evolution_iam_permission" "nlb_admin_perm" {
  resource_id = var.project_id
  subject_id  = cloudru_evolution_iam_service_account.cluster_sa.id

  role_identifier = {
    role_name = "nlb.admin"
  }
}

resource "cloudru_evolution_iam_permission" "vpc_admin_perm" {
  resource_id = var.project_id
  subject_id  = cloudru_evolution_iam_service_account.cluster_sa.id

  role_identifier = {
    role_name = "vpc.admin"
  }
}

resource "cloudru_evolution_compute_nat_gateway" "snat" {
  name       = "k8s-internet-snat"
  project_id = var.project_id
  vpc_id     = var.network_id
  zone = {
    name = "ru.AZ-2"
  }
}

resource "cloudru_evolution_mk8s_cluster" "resource_cluster" {
  name       = "cloudru-minimal-cluster"
  project_id = var.project_id

  control_plane = {
    count   = 1
    version = "v1.33.13"
    machine_configuration = {
      flavor = {
        flavor_id = "1f38e57c-0004-4f44-badf-1a0f3c09a128" # 2vCPU 4GB RAM 100% 
      }
    }
  }
  bootstrap_managed_addons = {
    persistent_disk_csi_driver = { enabled = true }
    horizontal_pod_autoscaling = { enabled = true }
    kube_proxy                 = { enabled = true }
    coredns                    = { enabled = true }
  }
  monitoring_service = { enabled = false }
  audit_service = { enabled = false }
  logging_service = { enabled = false }

  network_configuration = {
    private_vip_subnet_id = var.subnet_id
    kube_api_internet     = true
    network_plugin = {
      cilium = {
        enabled     = true
        version = "1.19.5-sbc.0"
      }
    }
    pods_subnet_cidr     = "10.10.0.0/16"
    services_subnet_cidr = "10.96.0.0/16"
  }

  identity_configuration = {
    cluster_sa_id = cloudru_evolution_iam_service_account.cluster_sa.id
  }

  depends_on = [cloudru_evolution_compute_nat_gateway.snat]
}

resource "cloudru_evolution_mk8s_node_pool" "resource_node_pool" {
  cluster_id = cloudru_evolution_mk8s_cluster.resource_cluster.id
  name       = "cloudru-minimal-nodepool"
  version    = "v1.33.13"
  machine_configuration = {
    flavor = {
      flavor_id = "c35c1ae7-55f4-40a8-98b4-4f3b570bf1e9" # 4vCPU 8GB RAM 100%
    }
    disk = {
      size = 40
    }
  }
  network_configuration = {
    nodes_subnet_id = var.subnet_id
  }
  update_configuration = {
    strategy = "NODE_POOL_UPDATE_STRATEGY_ROLLING_UPDATE"
    rolling_update_policy = {
      max_surge       = 1
      max_unavailable = 0
    }
  }
  scale_policy = {
    fixed_scale = {
      count = 1
    }
  }
}

resource "cloudru_evolution_mk8s_cluster_addon" "resource_cluster_addon" {
  cluster_id   = cloudru_evolution_mk8s_cluster.resource_cluster.id
  name         = "ingress-nginx" # Замените на точное имя аддона, если требуется
  app_version  = "1.14.0"     # Укажите актуальную версию
  resolve_mode = "RESOLVE_CONFLICTS_MODE_OVERWRITE"
  preserve     = true
  timeouts {
    create = "60m"
    update = "30m"
    delete = "20m"
  }
  lifecycle {
    ignore_changes = [timeouts]
  }
  depends_on = [cloudru_evolution_mk8s_node_pool.resource_node_pool]
}

output "cluster_cp_endpoint" {
  value = [
    for ep in cloudru_evolution_mk8s_cluster.resource_cluster.network_configuration.cp_endpoints :
    ep.address
    if ep.network == "NETWORK_TYPE_PUBLIC"
  ][0]
}

data "cloudru_evolution_mk8s_kube_config_collection" "datasource_kube_config" {
  cluster_id   = cloudru_evolution_mk8s_cluster.resource_cluster.id
}

output "kube_config_file" {
  value     = base64decode(data.cloudru_evolution_mk8s_kube_config_collection.datasource_kube_config.kube_config.config)
  sensitive = true
}

resource "null_resource" "kubeconfig" {
  triggers = {
    cluster_id   = cloudru_evolution_mk8s_cluster.resource_cluster.id
    auth_key_id  = var.auth_key_id
    auth_secret  = var.auth_secret
  }

  provisioner "local-exec" {
    interpreter = ["bash", "-c"]
    command     = <<-EOT
      set -e
      mkdir -p ~/.kube
      terraform output -raw kube_config_file \
        | sed -E \
            -e "/name: CLOUDRU_KEY_ID/{n;s|value:.*|value: \"${var.auth_key_id}\"|}" \
            -e "/name: CLOUDRU_SECRET_ID/{n;s|value:.*|value: \"${var.auth_secret}\"|}" \
        > ~/.kube/config
      chmod 600 ~/.kube/config
      echo "kubeconfig written to ~/.kube/config"
    EOT
  }

  depends_on = [cloudru_evolution_mk8s_cluster_addon.resource_cluster_addon]
}

data "external" "ingress_ip" {
  program = ["bash", "-c", <<-EOT
    set -e
    # Ждём, пока балансировщик получит IP (до 5 минут)
    for i in $(seq 1 30); do
      IP=$(kubectl get svc ingress-nginx-controller -n ingress \
        -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || true)
      if [ -n "$IP" ] && [ "$IP" != "<pending>" ]; then
        echo "{\"ip\":\"$IP\"}"
        exit 0
      fi
      sleep 10
    done
    echo "Timeout waiting for ingress IP (svc=$SVC ns=$NS)" >&2
    exit 1
  EOT
  ]

  depends_on = [null_resource.kubeconfig]
}

resource "cloudru_evolution_dns_public_zone" "pa99" {
  project_id  = var.project_id
  name        = "pa99.online."
  domain      = "pa99.online."
  description = "Public DNS zone for pa99.online"

  records = [
    {
      name   = "www"
      type   = "a"
      ttl    = 300
      values = [data.external.ingress_ip.result["ip"]]
    }
  ]

  depends_on = [data.external.ingress_ip]
}