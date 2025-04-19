terraform {
  required_version = ">= 1.6.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }
}

provider "azurerm" {
  features {}
}

resource "azurerm_resource_group" "faceid_resourcegroup" {
  name     = var.resource_group_name
  location = var.location
}


resource "azurerm_cognitive_account" "faceid_cog_account" {
  name                = "${var.prefix}-face"
  location            = azurerm_resource_group.faceid_resourcegroup.location
  resource_group_name = azurerm_resource_group.faceid_resourcegroup.name

  kind     = "Face"
  sku_name = "F0" # Free - 20 calls a minute 30k a month.

  custom_subdomain_name       = "${var.prefix}-faceid-checking"
  public_network_access_enabled = true # Accessible to the Internet...

  network_acls {
    default_action = "Allow"
  }

  tags = {
    Environment = "FaceID POC"
  }
}

# -------------------------------------------------------------------
#  Useful outputs
# -------------------------------------------------------------------
output "face_endpoint" {
  value = azurerm_cognitive_account.face.endpoint
}

output "face_key_primary" {
  value     = azurerm_cognitive_account.face.primary_access_key
  sensitive = true
}

