terraform {
  #required_version = ">= 1.6.0"

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
  sku_name = "F0" # Free - 20 calls a minute or 30k a month.

  custom_subdomain_name       = "${var.prefix}-faceid-checking"
  public_network_access_enabled = true # Accessible to the Internet...

  network_acls {
    default_action = "Allow"
  }

  tags = {
    Environment = "FaceID POC"
  }
}


resource "azurerm_service_plan" "faceid_plan" {
  name                = "${var.prefix}-plan"
  location            = azurerm_resource_group.faceid_resourcegroup.location
  resource_group_name = azurerm_resource_group.faceid_resourcegroup.name
  os_type             = "Linux"
  sku_name            = "B1"
}

resource "azurerm_linux_web_app" "faceid_webapp" {
  name                = "${var.prefix}-app"
  location            = azurerm_resource_group.faceid_resourcegroup.location
  resource_group_name = azurerm_resource_group.faceid_resourcegroup.name
  service_plan_id     = azurerm_service_plan.faceid_plan.id

  site_config {
    application_stack {
      python_version = "3.11"
    }
    always_on = true
    app_command_line = "python app.py"
  }

  app_settings = {
    "FACE_ENDPOINT"                  = azurerm_cognitive_account.faceid_cog_account.endpoint,
    "FACE_APIKEY"                    = azurerm_cognitive_account.faceid_cog_account.primary_access_key,
    "WEBSITES_PORT"                  = 8000,
    "SCM_DO_BUILD_DURING_DEPLOYMENT" = true
  }

  identity {
    type = "SystemAssigned"
  }
}

output "webapp_url" {
  value = azurerm_linux_web_app.faceid_webapp.default_hostname
}

output "webapp_name" {
  value = azurerm_linux_web_app.faceid_webapp.name
}  

output "webapp_resource_group" {
  value = azurerm_linux_web_app.faceid_webapp.resource_group_name
}


output "face_endpoint" {
  value = azurerm_cognitive_account.faceid_cog_account.endpoint
}

output "face_key_primary" {
  value     = azurerm_cognitive_account.faceid_cog_account.primary_access_key
  sensitive = true
}

