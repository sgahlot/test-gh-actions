#!/bin/bash

# RBAC Testing Cleanup Script
# Removes all GitHub Actions RBAC resources for clean testing

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🧹 Cleaning up GitHub Actions RBAC resources for testing${NC}"
echo "=================================================================="

# Function to safely delete if exists
safe_delete() {
    local resource_type=$1
    local resource_name=$2
    local namespace=$3
    
    if [ -n "$namespace" ]; then
        if oc get $resource_type $resource_name -n $namespace &>/dev/null; then
            echo -e "${YELLOW}   Deleting $resource_type/$resource_name in namespace $namespace${NC}"
            oc delete $resource_type $resource_name -n $namespace
        fi
    else
        if oc get $resource_type $resource_name &>/dev/null; then
            echo -e "${YELLOW}   Deleting cluster $resource_type/$resource_name${NC}"
            oc delete $resource_type $resource_name
        fi
    fi
}

# Get all test namespaces
TEST_NAMESPACES=("test-cluster-admin" "test-namespace-scoped" "test-hybrid" "sgahlot-test" "sgahlot-testi")

echo -e "${BLUE}🗑️  Removing cluster-level RBAC resources...${NC}"
# Remove cluster-level resources
safe_delete "clusterrolebinding" "github-actions-rbac-manager"
safe_delete "clusterrolebinding" "github-actions-cluster-admin"
safe_delete "clusterrolebinding" "github-actions-monitoring"
safe_delete "clusterrole" "github-actions-rbac-manager"
safe_delete "clusterrole" "github-actions-monitoring"

echo -e "${BLUE}🗑️  Removing namespace-level RBAC resources...${NC}"
for namespace in "${TEST_NAMESPACES[@]}"; do
    if oc get namespace $namespace &>/dev/null; then
        echo -e "${BLUE}   Cleaning namespace: $namespace${NC}"
        safe_delete "rolebinding" "github-actions-deployer" "$namespace"
        safe_delete "role" "github-actions-deployer" "$namespace"
        safe_delete "secret" "github-actions-token" "$namespace"
        safe_delete "serviceaccount" "github-actions" "$namespace"
    fi
done

echo -e "${BLUE}🗑️  Removing test namespaces (optional)...${NC}"
for namespace in "${TEST_NAMESPACES[@]}"; do
    if oc get namespace $namespace &>/dev/null; then
        echo -e "${YELLOW}   Found test namespace: $namespace${NC}"
        read -p "Delete namespace $namespace? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo -e "${YELLOW}   Deleting namespace: $namespace${NC}"
            oc delete namespace $namespace
        else
            echo -e "${GREEN}   Keeping namespace: $namespace${NC}"
        fi
    fi
done

echo -e "${GREEN}✅ RBAC cleanup completed!${NC}"
echo -e "${BLUE}📋 You can now run clean RBAC tests:${NC}"
echo "   ./scripts/ocp-setup.sh -s -t -n test-cluster-admin"
echo "   RBAC_CONFIG=github-actions-rbac-namespace.yml ./scripts/ocp-setup.sh -s -t -n test-namespace-scoped"
echo "   RBAC_CONFIG=github-actions-rbac-hybrid.yml ./scripts/ocp-setup.sh -s -t -n test-hybrid"