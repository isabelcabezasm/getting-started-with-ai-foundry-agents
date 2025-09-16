SHELL := /bin/bash

export PATH := $(HOME)/.local/bin:$(PATH)

.PHONY: help setup install clean lint clear-cache test format fmt chatbot dataset-create
.DEFAULT_GOAL := help
.ONESHELL: # Applies to every target in the file https://www.gnu.org/software/make/manual/html_node/One-Shell.html
MAKEFLAGS += --silent # https://www.gnu.org/software/make/manual/html_node/Silent.html

# Load environment file if exists
ENV_FILE := .env
ifeq ($(filter $(MAKECMDGOALS),config clean),)
	ifneq ($(strip $(wildcard $(ENV_FILE))),)
		ifneq ($(MAKECMDGOALS),config)
			include $(ENV_FILE)
			export
		endif
	endif
endif

help: ## 💬 This help message :)
	grep -E '[a-zA-Z_-]+:.*?## .*$$' $(firstword $(MAKEFILE_LIST)) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n\n", $$1, $$2}'

setup: ## 🎭 init environment 
	@echo "🎭 Setting up environment..."
	@pip install --upgrade pip
	@pip install -U pip setuptools
	@pip install uv
	@make install

install: ## 📦 Install python packages
	@echo "📦 Installing python packages..."
	@uv sync --all-groups

clean: ## 🧹 Clean python packages
	@echo "🧹 Cleaning python packages..."
	@uv clean
	@make clear-cache

clear-cache: ## 🧹 Clean python cache
	@echo "🧹 Cleaning python cache..."
	@find . -type d -name __pycache__ -exec rm -r {} \+
