#!/bin/bash
set -e

echo "=== SimHPC GPU Worker Starting ==="
echo "Runtime Version: ${RUNTIME_VERSION:-unknown}"
echo "CUDA Devices: $CUDA_VISIBLE_DEVICES"

if command -v nvidia-smi &> /dev/null; then
    nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
else
    echo "WARNING: nvidia-smi not found. Running without GPU verification."
fi

echo "Verifying scientific libraries..."
python3 -c "
import sys
libs = ['sundials', 'mfem', 'glvis']
for lib in libs:
    try:
        __import__(lib)
        print(f'  {lib}: available')
    except ImportError:
        print(f'  {lib}: NOT FOUND (will use system installation)')
"

if [ -n "$KERNEL_HOST" ]; then
    echo "Registering with kernel at $KERNEL_HOST:$KERNEL_PORT..."
    for i in $(seq 1 30); do
        if python3 -c "
import grpc
ch = grpc.insecure_channel('$KERNEL_HOST:$KERNEL_PORT')
grpc.channel_ready_future(ch).result(timeout=2)
" 2>/dev/null; then
            echo "Kernel is ready."
            break
        fi
        echo "Waiting for kernel... ($i/30)"
        sleep 2
    done

    python3 -c "
import grpc
from proto import plugin_host_pb2, plugin_host_pb2_grpc

channel = grpc.insecure_channel('$KERNEL_HOST:$KERNEL_PORT')
stub = plugin_host_pb2_grpc.PluginHostStub(channel)

response = stub.RegisterWorker(plugin_host_pb2.RegisterRequest(
    worker_type='gpu',
    capabilities=['physics.solve', 'physics.simulate', 'forecast.generate'],
    node_info={'gpu_type': 'A40', 'memory_mb': 49152},
))
print(f'Registration response: {response.status}')
"
    echo "Self-registration complete."
fi

echo "=== Starting GPU Worker ==="
exec "$@"
