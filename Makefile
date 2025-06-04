# export all variables defined as environment variables
.EXPORT_ALL_VARIABLES:

.PHONY: default
default: all

.PHONY: dev
dev: start-cluster start-juju juju-deploy

.PHONY: nuke
nuke: delete-cluster delete-juju

.PHONY: juju-deploy
juju-deploy:
	juju bootstrap kind-language-tool-dev-cluster language-tool-controller
	juju add-model language-tool-model
	juju deploy ./language-tool-k8s-charm_ubuntu-22.04-amd64.charm --resource language-tool-image=ghcr.io/canonical/api_demo_server:1.0.1

# ====================================================================
# Local dev cluster utility targets. (k8s, kustomize, kind, skaffold)

KIND_CLUSTER := language-tool-dev-cluster

.PHONY: start-cluster
start-cluster:
	@if ! kind get clusters | grep -q "$(KIND_CLUSTER)"; then \
		echo "Cluster '$(KIND_CLUSTER)' does not exist. Creating..."; \
		kind create cluster \
			--image kindest/node:v1.31.0 \
			--name $(KIND_CLUSTER) \
			--config kind.yaml; \
		kubectl config set-context --current --namespace=default; \
	else \
		echo "Cluster '$(KIND_CLUSTER)' already exists."; \
	fi

.PHONY: delete-cluster
delete-cluster:
	kind delete cluster --name $(KIND_CLUSTER)

# ====================================================================
# juju setup utilities

# development juju setup
.PHONY: start-juju
start-juju:
	@echo "Setting up Juju controller for development..."
	@if ! juju clouds --client --all | grep language-tool; then \
		juju add-k8s --context-name kind-dev-cluster language-tool; \
	else \
		echo "Juju controller already exists."; \
	fi

.PHONY: delete-juju
delete-juju:
	juju unregister language-tool-controller --no-prompt
	juju remove-cloud kind-language-tool-dev-cluster
