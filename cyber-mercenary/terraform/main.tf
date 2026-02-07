terraform {
  required_version = ">= 1.7.0"

  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.24"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.12"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
  }

  backend "azurerm" {
    resource_group_name  = "cyber-mercenary-tfstate"
    storage_account_name  = "cybermercenarytfstate"
    container_name        = "tfstate"
    key                   = "terraform.tfstate"
  }

  # Or use local backend for development
  # backend "local" {
  #   path = "terraform.tfstate"
  # }
}

provider "kubernetes" {
  config_path    = "~/.kube/config"
  config_context = var.kubernetes_cluster
}

provider "helm" {
  kubernetes {
    config_path    = "~/.kube/config"
    config_context = var.kubernetes_cluster
  }
}

provider "random" {}

variable "image_tag" {
  description = "Docker image tag"
  type        = string
  default     = "latest"
}

variable "registry" {
  description = "Container registry"
  type        = string
  default     = "ghcr.io"
}

variable "repository" {
  description = "Container repository"
  type        = string
  default     = "sketchbreezy/cyber-mercenary"
}

variable "kubernetes_cluster" {
  description = "Kubernetes cluster context"
  type        = string
  default     = "production"
}

variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "production"
}

variable "app_replica_count" {
  description = "Number of replicas"
  type        = number
  default     = 3
}

variable "app_cpu_limit" {
  description = "CPU limit per pod"
  type        = string
  default     = "2000m"
}

variable "app_memory_limit" {
  description = "Memory limit per pod"
  type        = string
  default     = "2Gi"
}

variable "app_cpu_request" {
  description = "CPU request per pod"
  type        = string
  default     = "500m"
}

variable "app_memory_request" {
  description = "Memory request per pod"
  type        = string
  default     = "512Mi"
}

variable "domain_name" {
  description = "Domain name for ingress"
  type        = string
  default     = "api.cyber-mercenary.io"
}

variable "enable_postgres" {
  description = "Enable PostgreSQL deployment"
  type        = bool
  default     = false
}

variable "enable_redis" {
  description = "Enable Redis deployment"
  type        = bool
  default     = false
}

variable "enable_monitoring" {
  description = "Enable monitoring stack"
  type        = bool
  default     = true
}

variable "enable_alerting" {
  description = "Enable alerting"
  type        = bool
  default     = true
}

locals {
  image_url = "${var.registry}/${var.repository}:${var.image_tag}"
}

resource "kubernetes_namespace" "production" {
  metadata {
    name = var.environment
    labels = {
      environment = var.environment
      managed_by  = "terraform"
    }
  }
}

resource "kubernetes_namespace" "monitoring" {
  count = var.enable_monitoring ? 1 : 0
  metadata {
    name = "monitoring"
    labels = {
      managed_by = "terraform"
    }
  }
}

resource "kubernetes_secret" "app_secrets" {
  metadata {
    name      = "cyber-mercenary-secrets"
    namespace = var.environment
  }

  data = {
    monad-rpc-url          = var.monad_rpc_url
    minimax-api-key         = var.minimax_api_key
    escrow-contract-address = var.escrow_contract_address
  }

  type = "Opaque"
}

resource "kubernetes_deployment" "app" {
  metadata {
    name      = "cyber-mercenary"
    namespace = var.environment
    labels = {
      app      = "cyber-mercenary"
      version  = var.image_tag
    }
  }

  spec {
    replicas = var.app_replica_count

    selector {
      match_labels = {
        app = "cyber-mercenary"
      }
    }

    template {
      metadata {
        labels = {
          app     = "cyber-mercenary"
          version = var.image_tag
        }
      }

      spec {
        container {
          image = local.image_url
          name  = "cyber-mercenary"

          port {
            container_port = 8000
            name           = "http"
          }

          resources {
            limits = {
              cpu    = var.app_cpu_limit
              memory = var.app_memory_limit
            }
            requests = {
              cpu    = var.app_cpu_request
              memory = var.app_memory_request
            }
          }

          env {
            name = "MONAD_RPC_URL"
            value_from {
              secret_key_ref {
                name = kubernetes_secret.app_secrets.metadata[0].name
                key  = "monad-rpc-url"
              }
            }
          }

          env {
            name = "MINIMAX_API_KEY"
            value_from {
              secret_key_ref {
                name = kubernetes_secret.app_secrets.metadata[0].name
                key  = "minimax-api-key"
              }
            }
          }

          liveness_probe {
            http_get {
              path = "/health"
              port = 8000
            }
            initial_delay_seconds = 30
            period_seconds        = 10
          }

          readiness_probe {
            http_get {
              path = "/health"
              port = 8000
            }
            initial_delay_seconds = 10
            period_seconds        = 5
          }
        }
      }
    }
  }
}

resource "kubernetes_service" "app" {
  metadata {
    name      = "cyber-mercenary"
    namespace = var.environment
  }

  spec {
    selector = {
      app = "cyber-mercenary"
    }

    port {
      port        = 80
      target_port = 8000
      protocol    = "TCP"
    }
  }
}

resource "kubernetes_ingress" "app" {
  metadata {
    name      = "cyber-mercenary"
    namespace = var.environment
    annotations = {
      "kubernetes.io/ingress.class" = "nginx"
    }
  }

  spec {
    rule {
      host = var.domain_name

      http {
        path {
          backend {
            service_name = kubernetes_service.app.metadata[0].name
            service_port = 80
          }
          path = "/"
        }
      }
    }
  }
}

output "deployment_url" {
  description = "Application URL"
  value       = "https://${var.domain_name}"
}

output "kubernetes_namespace" {
  description = "Kubernetes namespace"
  value       = var.environment
}
