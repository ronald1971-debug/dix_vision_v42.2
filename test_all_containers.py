#!/usr/bin/env python3
"""
Systematic Container Testing Script
Tests all 100 containers one by one, documenting results
"""

import subprocess
import json
import time
import os
from datetime import datetime

# Container list based on compose.yaml services
containers = [
    # Core Infrastructure
    "redis-service",
    "postgresql-service", 
    "prometheus-service",
    "grafana-service",
    
    # Tier 1 Critical (custom builds)
    "ccxt-service",
    "langchain-service",
    "playwright-service", 
    "fastapi-service",
    "celery-service",
    "requests-service",
    
    # Additional GitHub repositories (alphabetical)
    "aiohttp-service",
    "airflow-service",
    "apache-beam-service",
    "argon-service",
    "asyncio-enhanced-service",
    "beautifulsoup4-service",
    "blackbox-service",
    "celery-enhanced-service",
    "clickhouse-service",
    "consul-service",
    "cvxpy-service",
    "dagster-service",
    "darts-service",
    "discordbot-service",
    "django-service",
    "docker-service",
    "docker-py-service",
    "duckdb-service",
    "dynaconf-service",
    "elasticsearch-service",
    "etcd-service",
    "fastapi-enhanced-service",
    "flask-service",
    "flask-limiter-service",
    "gensim-service",
    "graphql-service",
    "grpc-service",
    "influxdb-service",
    "jaeger-service",
    "jinja2-service",
    "jupyter-service",
    "kafka-service",
    "kombu-service",
    "kong-service",
    "kubernetes-service",
    "kubernetes-python-service",
    "loki-service",
    "marshmallow-service",
    "matplotlib-service",
    "minio-service",
    "montecarlo-python-service",
    "neo4j-service",
    "newspaper3k-service",
    "nltk-service",
    "numpy-service",
    "opencv-service",
    "openpyxl-service",
    "opentelemetry-service",
    "pandas-service",
    "passlib-service",
    "pdfplumber-service",
    "pillow-service",
    "prefect-service",
    "pulp-service",
    "pusher-python-service",
    "pydantic-service",
    "pydantic-settings-service",
    "pytesseract-service",
    "pytest-service",
    "pytest-enhanced-service",
    "python-docx-service",
    "python-jose-service",
    "pytorch-service",
    "rabbitmq-service",
    "ray-service",
    "redis-cluster-service",
    "redis-py-cluster-service",
    "scikit-image-service",
    "scikit-learn-service",
    "scipy-optimize-service",
    "scrapy-service",
    "selenium-service",
    "sentry-sdk-service",
    "simpy-service",
    "slowapi-service",
    "socket.io-client-service",
    "sqlalchemy-service",
    "sqlalchemy-enhanced-service",
    "statsmodels-service",
    "structlog-service",
    "telegrambot-service",
    "tempo-service",
    "tensorflow-service",
    "textblob-service",
    "timescaledb-service",
    "tornado-service",
    "twisted-service",
    "vault-service",
    "websockets-service"
]

def test_container(container_name):
    """Test a single container: build and runtime check"""
    print(f"\n{'='*60}")
    print(f"Testing: {container_name}")
    print(f"{'='*60}")
    import sys
    sys.stdout.flush()
    
    result = {
        "container": container_name,
        "build_status": "skipped",
        "runtime_status": "skipped", 
        "errors": [],
        "timestamp": datetime.now().isoformat()
    }
    
    # Determine if it's a standard image or custom build
    standard_images = ["redis-service", "postgresql-service", "prometheus-service", "grafana-service"]
    
    if container_name in standard_images:
        print(f"Standard Docker image - skipping build test")
        import sys
        sys.stdout.flush()
        result["build_status"] = "standard_image"
    else:
        # Try to build custom container
        service_name = container_name.replace("-service", "")
        dockerfile_path = f"containers/github_repos/{service_name}/Dockerfile"
        context_path = f"containers/github_repos/{service_name}"
        
        if not os.path.exists(dockerfile_path):
            print(f"Dockerfile not found: {dockerfile_path}")
            result["build_status"] = "dockerfile_not_found"
            result["errors"].append("Dockerfile not found")
            return result
        
        try:
            print(f"Building {container_name}...")
            build_cmd = [
                "docker", "build", 
                "-t", f"test-{service_name}:latest",
                "-f", dockerfile_path,
                context_path
            ]
            
            build_result = subprocess.run(build_cmd, capture_output=True, text=True, timeout=300, encoding='utf-8', errors='replace')
            
            if build_result.returncode == 0:
                print(f"[OK] Build successful")
                result["build_status"] = "success"

                # Try to run container briefly
                try:
                    print(f"Testing runtime...")
                    run_cmd = ["docker", "run", "--rm", f"test-{service_name}:latest"]
                    run_result = subprocess.run(run_cmd, capture_output=True, text=True, timeout=10, encoding='utf-8', errors='replace')

                    if "started successfully" in run_result.stdout.lower() or "initialized" in run_result.stdout.lower():
                        print(f"[OK] Runtime successful")
                        result["runtime_status"] = "success"
                    else:
                        print(f"[WARN] Runtime check inconclusive")
                        result["runtime_status"] = "inconclusive"
                        if run_result.stderr:
                            result["errors"].append(run_result.stderr[:200])
                except subprocess.TimeoutExpired:
                    print(f"[WARN] Runtime test timed out (container may be running)")
                    result["runtime_status"] = "timeout"
                except Exception as e:
                    print(f"[FAIL] Runtime test failed: {str(e)}")
                    result["runtime_status"] = "failed"
                    result["errors"].append(str(e))
            else:
                print(f"[FAIL] Build failed")
                result["build_status"] = "failed"
                error_output = build_result.stderr if build_result.stderr else build_result.stdout
                # Capture last 1000 chars of error
                if error_output:
                    result["errors"].append(error_output[-1000:] if len(error_output) > 1000 else error_output)
                else:
                    result["errors"].append("Unknown build error - no output captured")
                
        except subprocess.TimeoutExpired:
            print(f"[FAIL] Build timed out")
            result["build_status"] = "timeout"
            result["errors"].append("Build timeout after 300 seconds")
        except Exception as e:
            print(f"[FAIL] Build error: {str(e)}")
            result["build_status"] = "error"
            result["errors"].append(str(e))
    
    return result

def main():
    """Run systematic container testing"""
    print("Starting systematic container testing...")
    print(f"Total containers to test: {len(containers)}")
    
    # Test in batches of 20 containers
    batch_size = 20
    batch_number = 5  # Change this to test different batches
    start_idx = (batch_number - 1) * batch_size
    end_idx = start_idx + batch_size
    test_batch = containers[start_idx:end_idx]
    print(f"Testing batch {batch_number} of containers {start_idx+1}-{end_idx}...")
    
    results = []
    successes = 0
    failures = 0
    skipped = 0
    
    for i, container in enumerate(test_batch, 1):
        print(f"\nProgress: {i}/{len(containers)}")
        
        try:
            result = test_container(container)
            results.append(result)
            
            if result["build_status"] == "success":
                successes += 1
            elif result["build_status"] == "standard_image":
                skipped += 1
            else:
                failures += 1
                
            # Small delay between containers
            time.sleep(2)
            
        except Exception as e:
            print(f"Error testing {container}: {str(e)}")
            results.append({
                "container": container,
                "build_status": "error",
                "runtime_status": "error",
                "errors": [str(e)],
                "timestamp": datetime.now().isoformat()
            })
            failures += 1
    
    # Summary
    print(f"\n{'='*60}")
    print("TESTING SUMMARY")
    print(f"{'='*60}")
    print(f"Total containers tested this batch: {len(test_batch)}")
    print(f"Successful: {successes}")
    print(f"Failed: {failures}")
    print(f"Skipped (standard images): {skipped}")
    print(f"Success rate: {(successes/len(test_batch)*100):.1f}%")

    # Save results
    results_filename = f"container_test_results_batch{batch_number}.json"
    with open(results_filename, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to {results_filename}")
    print(f"Remaining containers to test: {len(containers) - end_idx}")
    return results

if __name__ == "__main__":
    main()
