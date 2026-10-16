data "terraform_remote_state" "infra" {
  backend = "local"
  config = {
    path = "../tf1/terraform.tfstate"
  }
}

provider "kubernetes" {
  host = data.terraform_remote_state.infra.outputs.cluster_cp_endpoint
  cluster_ca_certificate = ""
  insecure = true
  exec {
    api_version = "client.authentication.k8s.io/v1"
    command     = "cloudlogin"
    args        = ["get-token", "--iam-url=https://id.cloud.ru/auth/system/openid/token"]
    env = {
      CLOUDRU_KEY_ID    = var.auth_key_id
      CLOUDRU_SECRET_ID = var.auth_secret
    }
  }
}

data "kubernetes_service_v1" "ingress_nginx" {
  metadata {
    name      = "ingress-nginx-controller"
    namespace = "ingress"
  }
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
      values = [data.kubernetes_service_v1.ingress_nginx.status[0].load_balancer[0].ingress[0].ip]
    }
  ]
}
