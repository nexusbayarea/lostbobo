#!/bin/bash
set -e

echo "🚀 Setting up Minikube for SimHPC..."

# Start Minikube (use docker driver by default)
minikube start --driver=docker --cpus=4 --memory=8192 --disk-size=40g

# Enable useful addons
minikube addons enable ingress
minikube addons enable metrics-server

# Set kubeconfig context
kubectl config use-context minikube

echo "✅ Minikube ready!"
echo "   - Dashboard: minikube dashboard"
echo "   - Tunnel (for ingress): minikube tunnel"
echo "   - Current context: $(kubectl config current-context)"
