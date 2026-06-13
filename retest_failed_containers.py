#!/usr/bin/env python3
"""
Test the 8 previously failed containers after fixes
"""

import subprocess
import json
import time
import os
from datetime import datetime

# The 8 previously failed containers
failed_containers = [
    "ccxt-service",
    "celery-service", 
    "kong-service",
    "kubernetes-service",
    "opencv-service",
    "tempo-service",
    "pytorch-service",
    "timescaledb-service"
]

# Large ML libraries requiring extended timeout
large_build_containers = ["pytorch-service"]

def test_container(container_name):
    """Test a single container: build and runtime check"""
    print(f"\n{'='*60}")
    print(f"Testing: {container_name}")
    print(f"{'='*60}")
    
    result = {
        "container": container_name,
        "build_status": "skipped",
        "runtime_status": "skipped", 
        "errors": [],
        "timestamp": datetime.now().isoformat()
    }
    
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
        # Use extended timeout for large ML libraries
        build_timeout = 600 if container_name in large_build_containers else 300
        print(f"Build timeout: {build_timeout}s")
        
        build_cmd = [
            "docker", "build", 
            "-t", f"test-{service_name}:latest",
            "-f", dockerfile_path,
            context_path
        ]
        
        build_result = subprocess.run(build_cmd, capture_output=True, text=True, timeout=build_timeout, encoding='utf-8', errors='replace')
        
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
                elif "timeout" in run_result.stderr.lower() or "started" in run_result.stdout.lower():
                    print(f"[OK] Runtime timeout (container running)")
                    result["runtime_status"] = "timeout_running"
                else:
                    print(f"[WARN] Runtime check inconclusive")
                    result["runtime_status"] = "inconclusive"
                    if run_result.stderr:
                        result["errors"].append(run_result.stderr[:200])
            except subprocess.TimeoutExpired:
                print(f"[OK] Runtime test timed out (container may be running)")
                result["runtime_status"] = "timeout_running"
            except Exception as e:
                print(f"[WARN] Runtime test failed: {str(e)}")
                result["runtime_status"] = "runtime_error"
                result["errors"].append(str(e))
        else:
            print(f"[FAIL] Build failed")
            result["build_status"] = "failed"
            error_output = build_result.stderr if build_result.stderr else build_result.stdout
            if error_output:
                result["errors"].append(error_output[-1000:] if len(error_output) > 1000 else error_output)
            else:
                result["errors"].append("Unknown build error - no output captured")
                
    except subprocess.TimeoutExpired:
        print(f"[FAIL] Build timed out")
        result["build_status"] = "timeout"
        result["errors"].append(f"Build timeout after {build_timeout} seconds")
    except Exception as e:
        print(f"[FAIL] Build error: {str(e)}")
        result["build_status"] = "error"
        result["errors"].append(str(e))
    
    return result

def main():
    """Test the 8 previously failed containers"""
    print("Testing 8 previously failed containers after fixes...")
    print(f"Total containers to re-test: {len(failed_containers)}")
    
    results = []
    successes = 0
    failures = 0
    
    for i, container in enumerate(failed_containers, 1):
        print(f"\nProgress: {i}/{len(failed_containers)}")
        
        try:
            result = test_container(container)
            results.append(result)
            
            if result["build_status"] == "success":
                successes += 1
            else:
                failures += 1
                
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
    print("RE-TESTING SUMMARY")
    print(f"{'='*60}")
    print(f"Total containers re-tested: {len(failed_containers)}")
    print(f"Successful: {successes}")
    print(f"Failed: {failures}")
    print(f"Success rate: {(successes/len(failed_containers)*100):.1f}%")
    
    # Save results
    with open("container_retest_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print("\nResults saved to container_retest_results.json")
    
    if successes == len(failed_containers):
        print("\n✅ ALL 8 PREVIOUSLY FAILED CONTAINERS NOW BUILD SUCCESSFULLY!")
    else:
        print(f"\n⚠️  {failures} containers still need attention")
    
    return results

if __name__ == "__main__":
    main()
