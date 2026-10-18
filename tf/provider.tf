terraform {
  required_providers {
    cloudru = {
      source  = "cloudru/cloud"
      version = "2.1.4"
    }
  }
}

variable "project_id" {
  type        = string
  description = "Идентификатор проекта"
}

variable "auth_key_id" {
  type        = string
  description = "Идентификатор ключа доступа"
  sensitive   = true
}

variable "auth_secret" {
  type        = string
  description = "Секрет ключа доступа"
  sensitive   = true
}

variable "subnet_id" {
  type        = string
  description = "Идентификатор subnet"
}

variable "network_id" {
  type        = string
  description = "Идентификатор net"
}

# --- Провайдер ---
provider "cloudru" {
  project_id  = var.project_id
  auth_key_id = var.auth_key_id
  auth_secret = var.auth_secret

  endpoints = {
    iam_endpoint     = "iam.api.cloud.ru:443"
    compute_endpoint = "compute.api.cloud.ru:443"
    mk8s_endpoint    = "mk8s.api.cloud.ru:443"
  }
}
