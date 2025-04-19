variable "prefix" {
  description = "Short prefix used in resource names (e.g. 'face-ai-poc')."
  type        = string
}

variable "resource_group_name" {
  description = "Name of the new resource group."
  type        = string
}

variable "location" {
  description = "Azure region where resources will be created."
  type        = string
  default     = "eastus"
}

