terraform providers mirror  -platform=windows_amd64 -platform=linux_amd64 -platform=darwin_amd64 C:\tf-providers-mirror

mkdir C:\temp\tf-mirror-seed
notepad C:\temp\tf-mirror-seed\versions.tf
terraform {
  required_version = ">= 1.3.0"

  required_providers {
    databricks = {
      source  = "databricks/databricks"
      version = "1.106.0"
    }
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.0"
    }
    tls = {
      source  = "hashicorp/tls"
      version = "~> 4.0"
    }
  }
}
