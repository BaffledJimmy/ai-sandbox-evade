variable "prefix" {
  description = "Short prefix used in resource names (e.g. 'face-ai-poc')."
  type        = string
  default     = "face-ai-poc"
}

variable "resource_group_name" {
  description = "Name of the new resource group."
  type        = string
  default     = "face-ai-sandbox-poc"
}

variable "location" {
  description = "Azure region where resources will be created."
  type        = string
  default     = "ukwest"
}

