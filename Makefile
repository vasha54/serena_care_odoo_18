SHELL := /bin/bash
CURRENT_DIR := $(shell pwd)

RUNDOCKER_COMAND ?= docker-compose up
STOPDOCKER_COMAND ?= docker-compose down

RUNSERVER_DEVELOP ?=  DEV_MODE=true
RUNSERVER_INIT_DATABSE ?= INIT_DATABASE=true 
RUNSERVER_DEPLOY ?= $(RUNDOCKER_COMAND)

run-develop:
	@RUNSERVER_EXEC= $(RUNSERVER_DEVELOP) $(RUNDOCKER_COMAND)
.PHONY: run-develop

run-deploy:
	@RUNSERVER_EXEC= $(RUNSERVER_DEPLOY)
.PHONY: run-deploy

init-database:
	@RUNSERVER_EXEC= $(RUNSERVER_INIT_DATABSE) $(RUNDOCKER_COMAND)
.PHONY: init-database

docker-down:
	@RUNSERVER_EXEC= $(STOPDOCKER_COMAND)
.PHONY: docker-down

create-addons:
ifndef name_module
	@echo "Run with 'make create-addons name_module=..."
else
	@RUNSERVER_EXEC= docker-compose up -d && \
                     sleep 5 && \
                     docker-compose exec odoo odoo scaffold $(name_module) /mnt/extra-addons && \
                     docker-compose exec --user root odoo chmod -R 777 "/mnt/extra-addons/$(name_module)" && \
                     docker-compose down
endif
.PHONY: create-addon
