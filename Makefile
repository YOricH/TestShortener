ifneq (,$(wildcard ./.env.compose))
    include .env.compose
    export
endif

compose.run:
	docker-compose --project-directory . -f .deployment/docker-compose.yml -p shortener up --build

compose.stop:
	docker-compose --project-directory . -f .deployment/docker-compose.yml -p shortener stop

compose.clear:
	docker-compose --project-directory . -f .deployment/docker-compose.yml -p shortener down -v

# Assembling for Kubernetes configured for Minikube on VirtualBox.
kube.run:
	-pkill -f "port-forward"  # Release port 8000 if occupied. For production k8s use ingresses.
	envsubst < .env.compose > .env.temp
	@if [ -z "$$(kubectl get ns $$K8S_NAMESPACE)" ]; then \
        echo "Not found $$K8S_NAMESPACE namespace"; \
        kubectl create namespace $$K8S_NAMESPACE; \
    else \
        echo "$$K8S_NAMESPACE namespace already created"; \
    fi
	@for service in "postgres" "redis" ; do \
  		echo "Checking $$service volume"; \
	if [ -z "$$(kubectl -n $$K8S_NAMESPACE get pvc $$service-pvc)" ]; then \
        echo "Not found $$service volume"; \
        export SERVICE_NAME="$$service" && envsubst < .deployment/volumes.yaml | kubectl -n $$K8S_NAMESPACE apply -f -; \
    else \
        echo "$$service volume already created"; \
    fi \
    done
	kubectl -n $$K8S_NAMESPACE create configmap test-config --from-env-file=.env.temp -o yaml --dry-run=client | kubectl apply -f -
	kubectl -n $$K8S_NAMESPACE apply -f .deployment/deployment.yaml -f .deployment/service.yaml
	rm -f .env.temp
	kubectl -n $$K8S_NAMESPACE wait --for=condition=available --timeout=120s --all deployments
	kubectl -n $$K8S_NAMESPACE port-forward svc/shortener 8000:8000 > /dev/null 2>&1 &  # For production k8s use ingresses.
	@echo "TestShortener is started! Open http://localhost:8000"

kube.clear:
	-pkill -f "port-forward"
	kubectl delete ns --ignore-not-found=true $$K8S_NAMESPACE
	minikube ssh "sudo rm -rf /tmp/postgres && sudo rm -rf /tmp/redis"  # Deleting DBs data from minikube.