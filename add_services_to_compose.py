import yaml

# Read the current compose.yaml
with open('compose.yaml', 'r') as f:
    data = yaml.safe_load(f)

# Add the new services (39 containers from ports 9148-9184)
new_services = {
    'timescaledb-service': {
        'build': {'context': './containers/github_repos/timescaledb', 'dockerfile': 'Dockerfile'},
        'image': 'dix-timescaledb:latest',
        'container_name': 'dix-timescaledb-service',
        'ports': ['9148:9148'],
        'volumes': [
            './containers/github_repos/timescaledb/config:/app/config',
            './containers/github_repos/timescaledb/data:/app/data',
            './containers/github_repos/timescaledb/logs:/app/logs'
        ],
        'environment': ['TIMESCALEDB_LOG_LEVEL=INFO'],
        'restart': 'unless-stopped',
        'networks': ['dixvision-network'],
        'healthcheck': {
            'test': ['CMD', 'python', '/app/health_check.py'],
            'interval': '30s',
            'timeout': '10s',
            'retries': 3
        },
        'deploy': {
            'resources': {
                'limits': {'cpus': '1.0', 'memory': '1G'},
                'reservations': {'cpus': '0.5', 'memory': '512M'}
            }
        }
    },
    'duckdb-service': {
        'build': {'context': './containers/github_repos/duckdb', 'dockerfile': 'Dockerfile'},
        'image': 'dix-duckdb:latest',
        'container_name': 'dix-duckdb-service',
        'ports': ['9149:9149'],
        'volumes': [
            './containers/github_repos/duckdb/config:/app/config',
            './containers/github_repos/duckdb/data:/app/data',
            './containers/github_repos/duckdb/logs:/app/logs'
        ],
        'environment': ['DUCKDB_LOG_LEVEL=INFO'],
        'restart': 'unless-stopped',
        'networks': ['dixvision-network'],
        'healthcheck': {
            'test': ['CMD', 'python', '/app/health_check.py'],
            'interval': '30s',
            'timeout': '10s',
            'retries': 3
        },
        'deploy': {
            'resources': {
                'limits': {'cpus': '1.0', 'memory': '512M'},
                'reservations': {'cpus': '0.5', 'memory': '256M'}
            }
        }
    },
    'statsmodels-service': {
        'build': {'context': './containers/github_repos/statsmodels', 'dockerfile': 'Dockerfile'},
        'image': 'dix-statsmodels:latest',
        'container_name': 'dix-statsmodels-service',
        'ports': ['9150:9150'],
        'volumes': [
            './containers/github_repos/statsmodels/config:/app/config',
            './containers/github_repos/statsmodels/data:/app/data',
            './containers/github_repos/statsmodels/logs:/app/logs'
        ],
        'environment': ['STATSMODELS_LOG_LEVEL=INFO'],
        'restart': 'unless-stopped',
        'networks': ['dixvision-network'],
        'healthcheck': {
            'test': ['CMD', 'python', '/app/health_check.py'],
            'interval': '30s',
            'timeout': '10s',
            'retries': 3
        },
        'deploy': {
            'resources': {
                'limits': {'cpus': '1.0', 'memory': '512M'},
                'reservations': {'cpus': '0.5', 'memory': '256M'}
            }
        }
    },
    'scikit-image-service': {
        'build': {'context': './containers/github_repos/scikit-image', 'dockerfile': 'Dockerfile'},
        'image': 'dix-scikit-image:latest',
        'container_name': 'dix-scikit-image-service',
        'ports': ['9151:9151'],
        'volumes': [
            './containers/github_repos/scikit-image/config:/app/config',
            './containers/github_repos/scikit-image/data:/app/data',
            './containers/github_repos/scikit-image/logs:/app/logs'
        ],
        'environment': ['SCIKIT_IMAGE_LOG_LEVEL=INFO'],
        'restart': 'unless-stopped',
        'networks': ['dixvision-network'],
        'healthcheck': {
            'test': ['CMD', 'python', '/app/health_check.py'],
            'interval': '30s',
            'timeout': '10s',
            'retries': 3
        },
        'deploy': {
            'resources': {
                'limits': {'cpus': '1.0', 'memory': '512M'},
                'reservations': {'cpus': '0.5', 'memory': '256M'}
            }
        }
    },
    'pytesseract-service': {
        'build': {'context': './containers/github_repos/pytesseract', 'dockerfile': 'Dockerfile'},
        'image': 'dix-pytesseract:latest',
        'container_name': 'dix-pytesseract-service',
        'ports': ['9152:9152'],
        'volumes': [
            './containers/github_repos/pytesseract/config:/app/config',
            './containers/github_repos/pytesseract/data:/app/data',
            './containers/github_repos/pytesseract/logs:/app/logs'
        ],
        'environment': ['PYTESSERACT_LOG_LEVEL=INFO'],
        'restart': 'unless-stopped',
        'networks': ['dixvision-network'],
        'healthcheck': {
            'test': ['CMD', 'python', '/app/health_check.py'],
            'interval': '30s',
            'timeout': '10s',
            'retries': 3
        },
        'deploy': {
            'resources': {
                'limits': {'cpus': '1.0', 'memory': '512M'},
                'reservations': {'cpus': '0.5', 'memory': '256M'}
            }
        }
    },
    'gensim-service': {
        'build': {'context': './containers/github_repos/gensim', 'dockerfile': 'Dockerfile'},
        'image': 'dix-gensim:latest',
        'container_name': 'dix-gensim-service',
        'ports': ['9153:9153'],
        'volumes': [
            './containers/github_repos/gensim/config:/app/config',
            './containers/github_repos/gensim/data:/app/data',
            './containers/github_repos/gensim/logs:/app/logs'
        ],
        'environment': ['GENSIM_LOG_LEVEL=INFO'],
        'restart': 'unless-stopped',
        'networks': ['dixvision-network'],
        'healthcheck': {
            'test': ['CMD', 'python', '/app/health_check.py'],
            'interval': '30s',
            'timeout': '10s',
            'retries': 3
        },
        'deploy': {
            'resources': {
                'limits': {'cpus': '1.0', 'memory': '512M'},
                'reservations': {'cpus': '0.5', 'memory': '256M'}
            }
        }
    },
    'textblob-service': {
        'build': {'context': './containers/github_repos/textblob', 'dockerfile': 'Dockerfile'},
        'image': 'dix-textblob:latest',
        'container_name': 'dix-textblob-service',
        'ports': ['9154:9154'],
        'volumes': [
            './containers/github_repos/textblob/config:/app/config',
            './containers/github_repos/textblob/data:/app/data',
            './containers/github_repos/textblob/logs:/app/logs'
        ],
        'environment': ['TEXTBLOB_LOG_LEVEL=INFO'],
        'restart': 'unless-stopped',
        'networks': ['dixvision-network'],
        'healthcheck': {
            'test': ['CMD', 'python', '/app/health_check.py'],
            'interval': '30s',
            'timeout': '10s',
            'retries': 3
        },
        'deploy': {
            'resources': {
                'limits': {'cpus': '1.0', 'memory': '512M'},
                'reservations': {'cpus': '0.5', 'memory': '256M'}
            }
        }
    },
    'nltk-service': {
        'build': {'context': './containers/github_repos/nltk', 'dockerfile': 'Dockerfile'},
        'image': 'dix-nltk:latest',
        'container_name': 'dix-nltk-service',
        'ports': ['9155:9155'],
        'volumes': [
            './containers/github_repos/nltk/config:/app/config',
            './containers/github_repos/nltk/data:/app/data',
            './containers/github_repos/nltk/logs:/app/logs'
        ],
        'environment': ['NLTK_LOG_LEVEL=INFO'],
        'restart': 'unless-stopped',
        'networks': ['dixvision-network'],
        'healthcheck': {
            'test': ['CMD', 'python', '/app/health_check.py'],
            'interval': '30s',
            'timeout': '10s',
            'retries': 3
        },
        'deploy': {
            'resources': {
                'limits': {'cpus': '1.0', 'memory': '512M'},
                'reservations': {'cpus': '0.5', 'memory': '256M'}
            }
        }
    },
    'cvxpy-service': {
        'build': {'context': './containers/github_repos/cvxpy', 'dockerfile': 'Dockerfile'},
        'image': 'dix-cvxpy:latest',
        'container_name': 'dix-cvxpy-service',
        'ports': ['9156:9156'],
        'volumes': [
            './containers/github_repos/cvxpy/config:/app/config',
            './containers/github_repos/cvxpy/data:/app/data',
            './containers/github_repos/cvxpy/logs:/app/logs'
        ],
        'environment': ['CVXPY_LOG_LEVEL=INFO'],
        'restart': 'unless-stopped',
        'networks': ['dixvision-network'],
        'healthcheck': {
            'test': ['CMD', 'python', '/app/health_check.py'],
            'interval': '30s',
            'timeout': '10s',
            'retries': 3
        },
        'deploy': {
            'resources': {
                'limits': {'cpus': '1.0', 'memory': '512M'},
                'reservations': {'cpus': '0.5', 'memory': '256M'}
            }
        }
    },
    'scipy-optimize-service': {
        'build': {'context': './containers/github_repos/scipy-optimize', 'dockerfile': 'Dockerfile'},
        'image': 'dix-scipy-optimize:latest',
        'container_name': 'dix-scipy-optimize-service',
        'ports': ['9157:9157'],
        'volumes': [
            './containers/github_repos/scipy-optimize/config:/app/config',
            './containers/github_repos/scipy-optimize/data:/app/data',
            './containers/github_repos/scipy-optimize/logs:/app/logs'
        ],
        'environment': ['SCIPY_OPTIMIZE_LOG_LEVEL=INFO'],
        'restart': 'unless-stopped',
        'networks': ['dixvision-network'],
        'healthcheck': {
            'test': ['CMD', 'python', '/app/health_check.py'],
            'interval': '30s',
            'timeout': '10s',
            'retries': 3
        },
        'deploy': {
            'resources': {
                'limits': {'cpus': '1.0', 'memory': '512M'},
                'reservations': {'cpus': '0.5', 'memory': '256M'}
            }
        }
    },
    'simpy-service': {
        'build': {'context': './containers/github_repos/simpy', 'dockerfile': 'Dockerfile'},
        'image': 'dix-simpy:latest',
        'container_name': 'dix-simpy-service',
        'ports': ['9158:9158'],
        'volumes': [
            './containers/github_repos/simpy/config:/app/config',
            './containers/github_repos/simpy/data:/app/data',
            './containers/github_repos/simpy/logs:/app/logs'
        ],
        'environment': ['SIMPY_LOG_LEVEL=INFO'],
        'restart': 'unless-stopped',
        'networks': ['dixvision-network'],
        'healthcheck': {
            'test': ['CMD', 'python', '/app/health_check.py'],
            'interval': '30s',
            'timeout': '10s',
            'retries': 3
        },
        'deploy': {
            'resources': {
                'limits': {'cpus': '1.0', 'memory': '512M'},
                'reservations': {'cpus': '0.5', 'memory': '256M'}
            }
        }
    },
    'montecarlo-python-service': {
        'build': {'context': './containers/github_repos/montecarlo-python', 'dockerfile': 'Dockerfile'},
        'image': 'dix-montecarlo-python:latest',
        'container_name': 'dix-montecarlo-python-service',
        'ports': ['9159:9159'],
        'volumes': [
            './containers/github_repos/montecarlo-python/config:/app/config',
            './containers/github_repos/montecarlo-python/data:/app/data',
            './containers/github_repos/montecarlo-python/logs:/app/logs'
        ],
        'environment': ['MONTECARLO_PYTHON_LOG_LEVEL=INFO'],
        'restart': 'unless-stopped',
        'networks': ['dixvision-network'],
        'healthcheck': {
            'test': ['CMD', 'python', '/app/health_check.py'],
            'interval': '30s',
            'timeout': '10s',
            'retries': 3
        },
        'deploy': {
            'resources': {
                'limits': {'cpus': '1.0', 'memory': '512M'},
                'reservations': {'cpus': '0.5', 'memory': '256M'}
            }
        }
    },
    'argon-service': {
        'build': {'context': './containers/github_repos/argon', 'dockerfile': 'Dockerfile'},
        'image': 'dix-argon:latest',
        'container_name': 'dix-argon-service',
        'ports': ['9160:9160'],
        'volumes': [
            './containers/github_repos/argon/config:/app/config',
            './containers/github_repos/argon/data:/app/data',
            './containers/github_repos/argon/logs:/app/logs'
        ],
        'environment': ['ARGON_LOG_LEVEL=INFO'],
        'restart': 'unless-stopped',
        'networks': ['dixvision-network'],
        'healthcheck': {
            'test': ['CMD', 'python', '/app/health_check.py'],
            'interval': '30s',
            'timeout': '10s',
            'retries': 3
        },
        'deploy': {
            'resources': {
                'limits': {'cpus': '1.0', 'memory': '512M'},
                'reservations': {'cpus': '0.5', 'memory': '256M'}
            }
        }
    },
    'prefect-service': {
        'build': {'context': './containers/github_repos/prefect', 'dockerfile': 'Dockerfile'},
        'image': 'dix-prefect:latest',
        'container_name': 'dix-prefect-service',
        'ports': ['9161:9161'],
        'volumes': [
            './containers/github_repos/prefect/config:/app/config',
            './containers/github_repos/prefect/data:/app/data',
            './containers/github_repos/prefect/logs:/app/logs'
        ],
        'environment': ['PREFECT_LOG_LEVEL=INFO'],
        'restart': 'unless-stopped',
        'networks': ['dixvision-network'],
        'healthcheck': {
            'test': ['CMD', 'python', '/app/health_check.py'],
            'interval': '30s',
            'timeout': '10s',
            'retries': 3
        },
        'deploy': {
            'resources': {
                'limits': {'cpus': '1.0', 'memory': '512M'},
                'reservations': {'cpus': '0.5', 'memory': '256M'}
            }
        }
    },
    'dagster-service': {
        'build': {'context': './containers/github_repos/dagster', 'dockerfile': 'Dockerfile'},
        'image': 'dix-dagster:latest',
        'container_name': 'dix-dagster-service',
        'ports': ['9162:9162'],
        'volumes': [
            './containers/github_repos/dagster/config:/app/config',
            './containers/github_repos/dagster/data:/app/data',
            './containers/github_repos/dagster/logs:/app/logs'
        ],
        'environment': ['DAGSTER_LOG_LEVEL=INFO'],
        'restart': 'unless-stopped',
        'networks': ['dixvision-network'],
        'healthcheck': {
            'test': ['CMD', 'python', '/app/health_check.py'],
            'interval': '30s',
            'timeout': '10s',
            'retries': 3
        },
        'deploy': {
            'resources': {
                'limits': {'cpus': '1.0', 'memory': '512M'},
                'reservations': {'cpus': '0.5', 'memory': '256M'}
            }
        }
    },
    'apache-beam-service': {
        'build': {'context': './containers/github_repos/apache-beam', 'dockerfile': 'Dockerfile'},
        'image': 'dix-apache-beam:latest',
        'container_name': 'dix-apache-beam-service',
        'ports': ['9163:9163'],
        'volumes': [
            './containers/github_repos/apache-beam/config:/app/config',
            './containers/github_repos/apache-beam/data:/app/data',
            './containers/github_repos/apache-beam/logs:/app/logs'
        ],
        'environment': ['APACHE_BEAM_LOG_LEVEL=INFO'],
        'restart': 'unless-stopped',
        'networks': ['dixvision-network'],
        'healthcheck': {
            'test': ['CMD', 'python', '/app/health_check.py'],
            'interval': '30s',
            'timeout': '10s',
            'retries': 3
        },
        'deploy': {
            'resources': {
                'limits': {'cpus': '1.0', 'memory': '512M'},
                'reservations': {'cpus': '0.5', 'memory': '256M'}
            }
        }
    },
    'kubernetes-python-service': {
        'build': {'context': './containers/github_repos/kubernetes-python', 'dockerfile': 'Dockerfile'},
        'image': 'dix-kubernetes-python:latest',
        'container_name': 'dix-kubernetes-python-service',
        'ports': ['9164:9164'],
        'volumes': [
            './containers/github_repos/kubernetes-python/config:/app/config',
            './containers/github_repos/kubernetes-python/data:/app/data',
            './containers/github_repos/kubernetes-python/logs:/app/logs'
        ],
        'environment': ['KUBERNETES_PYTHON_LOG_LEVEL=INFO'],
        'restart': 'unless-stopped',
        'networks': ['dixvision-network'],
        'healthcheck': {
            'test': ['CMD', 'python', '/app/health_check.py'],
            'interval': '30s',
            'timeout': '10s',
            'retries': 3
        },
        'deploy': {
            'resources': {
                'limits': {'cpus': '1.0', 'memory': '512M'},
                'reservations': {'cpus': '0.5', 'memory': '256M'}
            }
        }
    },
    'docker-py-service': {
        'build': {'context': './containers/github_repos/docker-py', 'dockerfile': 'Dockerfile'},
        'image': 'dix-docker-py:latest',
        'container_name': 'dix-docker-py-service',
        'ports': ['9165:9165'],
        'volumes': [
            './containers/github_repos/docker-py/config:/app/config',
            './containers/github_repos/docker-py/data:/app/data',
            './containers/github_repos/docker-py/logs:/app/logs'
        ],
        'environment': ['DOCKER_PY_LOG_LEVEL=INFO'],
        'restart': 'unless-stopped',
        'networks': ['dixvision-network'],
        'healthcheck': {
            'test': ['CMD', 'python', '/app/health_check.py'],
            'interval': '30s',
            'timeout': '10s',
            'retries': 3
        },
        'deploy': {
            'resources': {
                'limits': {'cpus': '1.0', 'memory': '512M'},
                'reservations': {'cpus': '0.5', 'memory': '256M'}
            }
        }
    },
    'beautifulsoup4-service': {
        'build': {'context': './containers/github_repos/beautifulsoup4', 'dockerfile': 'Dockerfile'},
        'image': 'dix-beautifulsoup4:latest',
        'container_name': 'dix-beautifulsoup4-service',
        'ports': ['9166:9166'],
        'volumes': [
            './containers/github_repos/beautifulsoup4/config:/app/config',
            './containers/github_repos/beautifulsoup4/data:/app/data',
            './containers/github_repos/beautifulsoup4/logs:/app/logs'
        ],
        'environment': ['BEAUTIFULSOUP4_LOG_LEVEL=INFO'],
        'restart': 'unless-stopped',
        'networks': ['dixvision-network'],
        'healthcheck': {
            'test': ['CMD', 'python', '/app/health_check.py'],
            'interval': '30s',
            'timeout': '10s',
            'retries': 3
        },
        'deploy': {
            'resources': {
                'limits': {'cpus': '1.0', 'memory': '512M'},
                'reservations': {'cpus': '0.5', 'memory': '256M'}
            }
        }
    },
    'newspaper3k-service': {
        'build': {'context': './containers/github_repos/newspaper3k', 'dockerfile': 'Dockerfile'},
        'image': 'dix-newspaper3k:latest',
        'container_name': 'dix-newspaper3k-service',
        'ports': ['9167:9167'],
        'volumes': [
            './containers/github_repos/newspaper3k/config:/app/config',
            './containers/github_repos/newspaper3k/data:/app/data',
            './containers/github_repos/newspaper3k/logs:/app/logs'
        ],
        'environment': ['NEWSPAPER3K_LOG_LEVEL=INFO'],
        'restart': 'unless-stopped',
        'networks': ['dixvision-network'],
        'healthcheck': {
            'test': ['CMD', 'python', '/app/health_check.py'],
            'interval': '30s',
            'timeout': '10s',
            'retries': 3
        },
        'deploy': {
            'resources': {
                'limits': {'cpus': '1.0', 'memory': '512M'},
                'reservations': {'cpus': '0.5', 'memory': '256M'}
            }
        }
    },
    'pdfplumber-service': {
        'build': {'context': './containers/github_repos/pdfplumber', 'dockerfile': 'Dockerfile'},
        'image': 'dix-pdfplumber:latest',
        'container_name': 'dix-pdfplumber-service',
        'ports': ['9168:9168'],
        'volumes': [
            './containers/github_repos/pdfplumber/config:/app/config',
            './containers/github_repos/pdfplumber/data:/app/data',
            './containers/github_repos/pdfplumber/logs:/app/logs'
        ],
        'environment': ['PDFPLUMBER_LOG_LEVEL=INFO'],
        'restart': 'unless-stopped',
        'networks': ['dixvision-network'],
        'healthcheck': {
            'test': ['CMD', 'python', '/app/health_check.py'],
            'interval': '30s',
            'timeout': '10s',
            'retries': 3
        },
        'deploy': {
            'resources': {
                'limits': {'cpus': '1.0', 'memory': '512M'},
                'reservations': {'cpus': '0.5', 'memory': '256M'}
            }
        }
    },
    'python-docx-service': {
        'build': {'context': './containers/github_repos/python-docx', 'dockerfile': 'Dockerfile'},
        'image': 'dix-python-docx:latest',
        'container_name': 'dix-python-docx-service',
        'ports': ['9169:9169'],
        'volumes': [
            './containers/github_repos/python-docx/config:/app/config',
            './containers/github_repos/python-docx/data:/app/data',
            './containers/github_repos/python-docx/logs:/app/logs'
        ],
        'environment': ['PYTHON_DOCX_LOG_LEVEL=INFO'],
        'restart': 'unless-stopped',
        'networks': ['dixvision-network'],
        'healthcheck': {
            'test': ['CMD', 'python', '/app/health_check.py'],
            'interval': '30s',
            'timeout': '10s',
            'retries': 3
        },
        'deploy': {
            'resources': {
                'limits': {'cpus': '1.0', 'memory': '512M'},
                'reservations': {'cpus': '0.5', 'memory': '256M'}
            }
        }
    },
    'openpyxl-service': {
        'build': {'context': './containers/github_repos/openpyxl', 'dockerfile': 'Dockerfile'},
        'image': 'dix-openpyxl:latest',
        'container_name': 'dix-openpyxl-service',
        'ports': ['9170:9170'],
        'volumes': [
            './containers/github_repos/openpyxl/config:/app/config',
            './containers/github_repos/openpyxl/data:/app/data',
            './containers/github_repos/openpyxl/logs:/app/logs'
        ],
        'environment': ['OPENPYXL_LOG_LEVEL=INFO'],
        'restart': 'unless-stopped',
        'networks': ['dixvision-network'],
        'healthcheck': {
            'test': ['CMD', 'python', '/app/health_check.py'],
            'interval': '30s',
            'timeout': '10s',
            'retries': 3
        },
        'deploy': {
            'resources': {
                'limits': {'cpus': '1.0', 'memory': '512M'},
                'reservations': {'cpus': '0.5', 'memory': '256M'}
            }
        }
    },
    'twisted-service': {
        'build': {'context': './containers/github_repos/twisted', 'dockerfile': 'Dockerfile'},
        'image': 'dix-twisted:latest',
        'container_name': 'dix-twisted-service',
        'ports': ['9171:9171'],
        'volumes': [
            './containers/github_repos/twisted/config:/app/config',
            './containers/github_repos/twisted/data:/app/data',
            './containers/github_repos/twisted/logs:/app/logs'
        ],
        'environment': ['TWISTED_LOG_LEVEL=INFO'],
        'restart': 'unless-stopped',
        'networks': ['dixvision-network'],
        'healthcheck': {
            'test': ['CMD', 'python', '/app/health_check.py'],
            'interval': '30s',
            'timeout': '10s',
            'retries': 3
        },
        'deploy': {
            'resources': {
                'limits': {'cpus': '1.0', 'memory': '512M'},
                'reservations': {'cpus': '0.5', 'memory': '256M'}
            }
        }
    },
    'tornado-service': {
        'build': {'context': './containers/github_repos/tornado', 'dockerfile': 'Dockerfile'},
        'image': 'dix-tornado:latest',
        'container_name': 'dix-tornado-service',
        'ports': ['9172:9172'],
        'volumes': [
            './containers/github_repos/tornado/config:/app/config',
            './containers/github_repos/tornado/data:/app/data',
            './containers/github_repos/tornado/logs:/app/logs'
        ],
        'environment': ['TORNADO_LOG_LEVEL=INFO'],
        'restart': 'unless-stopped',
        'networks': ['dixvision-network'],
        'healthcheck': {
            'test': ['CMD', 'python', '/app/health_check.py'],
            'interval': '30s',
            'timeout': '10s',
            'retries': 3
        },
        'deploy': {
            'resources': {
                'limits': {'cpus': '1.0', 'memory': '512M'},
                'reservations': {'cpus': '0.5', 'memory': '256M'}
            }
        }
    },
    'pusher-python-service': {
        'build': {'context': './containers/github_repos/pusher-python', 'dockerfile': 'Dockerfile'},
        'image': 'dix-pusher-python:latest',
        'container_name': 'dix-pusher-python-service',
        'ports': ['9173:9173'],
        'volumes': [
            './containers/github_repos/pusher-python/config:/app/config',
            './containers/github_repos/pusher-python/data:/app/data',
            './containers/github_repos/pusher-python/logs:/app/logs'
        ],
        'environment': ['PUSHER_PYTHON_LOG_LEVEL=INFO'],
        'restart': 'unless-stopped',
        'networks': ['dixvision-network'],
        'healthcheck': {
            'test': ['CMD', 'python', '/app/health_check.py'],
            'interval': '30s',
            'timeout': '10s',
            'retries': 3
        },
        'deploy': {
            'resources': {
                'limits': {'cpus': '1.0', 'memory': '512M'},
                'reservations': {'cpus': '0.5', 'memory': '256M'}
            }
        }
    },
    'socket.io-client-service': {
        'build': {'context': './containers/github_repos/socket.io-client', 'dockerfile': 'Dockerfile'},
        'image': 'dix-socket.io-client:latest',
        'container_name': 'dix-socket.io-client-service',
        'ports': ['9174:9174'],
        'volumes': [
            './containers/github_repos/socket.io-client/config:/app/config',
            './containers/github_repos/socket.io-client/data:/app/data',
            './containers/github_repos/socket.io-client/logs:/app/logs'
        ],
        'environment': ['SOCKET_IO_CLIENT_LOG_LEVEL=INFO'],
        'restart': 'unless-stopped',
        'networks': ['dixvision-network'],
        'healthcheck': {
            'test': ['CMD', 'python', '/app/health_check.py'],
            'interval': '30s',
            'timeout': '10s',
            'retries': 3
        },
        'deploy': {
            'resources': {
                'limits': {'cpus': '1.0', 'memory': '512M'},
                'reservations': {'cpus': '0.5', 'memory': '256M'}
            }
        }
    },
    'pydantic-settings-service': {
        'build': {'context': './containers/github_repos/pydantic-settings', 'dockerfile': 'Dockerfile'},
        'image': 'dix-pydantic-settings:latest',
        'container_name': 'dix-pydantic-settings-service',
        'ports': ['9175:9175'],
        'volumes': [
            './containers/github_repos/pydantic-settings/config:/app/config',
            './containers/github_repos/pydantic-settings/data:/app/data',
            './containers/github_repos/pydantic-settings/logs:/app/logs'
        ],
        'environment': ['PYDANTIC_SETTINGS_LOG_LEVEL=INFO'],
        'restart': 'unless-stopped',
        'networks': ['dixvision-network'],
        'healthcheck': {
            'test': ['CMD', 'python', '/app/health_check.py'],
            'interval': '30s',
            'timeout': '10s',
            'retries': 3
        },
        'deploy': {
            'resources': {
                'limits': {'cpus': '1.0', 'memory': '512M'},
                'reservations': {'cpus': '0.5', 'memory': '256M'}
            }
        }
    },
    'dynaconf-service': {
        'build': {'context': './containers/github_repos/dynaconf', 'dockerfile': 'Dockerfile'},
        'image': 'dix-dynaconf:latest',
        'container_name': 'dix-dynaconf-service',
        'ports': ['9176:9176'],
        'volumes': [
            './containers/github_repos/dynaconf/config:/app/config',
            './containers/github_repos/dynaconf/data:/app/data',
            './containers/github_repos/dynaconf/logs:/app/logs'
        ],
        'environment': ['DYNACONF_LOG_LEVEL=INFO'],
        'restart': 'unless-stopped',
        'networks': ['dixvision-network'],
        'healthcheck': {
            'test': ['CMD', 'python', '/app/health_check.py'],
            'interval': '30s',
            'timeout': '10s',
            'retries': 3
        },
        'deploy': {
            'resources': {
                'limits': {'cpus': '1.0', 'memory': '512M'},
                'reservations': {'cpus': '0.5', 'memory': '256M'}
            }
        }
    },
    'structlog-service': {
        'build': {'context': './containers/github_repos/structlog', 'dockerfile': 'Dockerfile'},
        'image': 'dix-structlog:latest',
        'container_name': 'dix-structlog-service',
        'ports': ['9177:9177'],
        'volumes': [
            './containers/github_repos/structlog/config:/app/config',
            './containers/github_repos/structlog/data:/app/data',
            './containers/github_repos/structlog/logs:/app/logs'
        ],
        'environment': ['STRUCTLOG_LOG_LEVEL=INFO'],
        'restart': 'unless-stopped',
        'networks': ['dixvision-network'],
        'healthcheck': {
            'test': ['CMD', 'python', '/app/health_check.py'],
            'interval': '30s',
            'timeout': '10s',
            'retries': 3
        },
        'deploy': {
            'resources': {
                'limits': {'cpus': '1.0', 'memory': '512M'},
                'reservations': {'cpus': '0.5', 'memory': '256M'}
            }
        }
    },
    'sentry-sdk-service': {
        'build': {'context': './containers/github_repos/sentry-sdk', 'dockerfile': 'Dockerfile'},
        'image': 'dix-sentry-sdk:latest',
        'container_name': 'dix-sentry-sdk-service',
        'ports': ['9178:9178'],
        'volumes': [
            './containers/github_repos/sentry-sdk/config:/app/config',
            './containers/github_repos/sentry-sdk/data:/app/data',
            './containers/github_repos/sentry-sdk/logs:/app/logs'
        ],
        'environment': ['SENTRY_SDK_LOG_LEVEL=INFO'],
        'restart': 'unless-stopped',
        'networks': ['dixvision-network'],
        'healthcheck': {
            'test': ['CMD', 'python', '/app/health_check.py'],
            'interval': '30s',
            'timeout': '10s',
            'retries': 3
        },
        'deploy': {
            'resources': {
                'limits': {'cpus': '1.0', 'memory': '512M'},
                'reservations': {'cpus': '0.5', 'memory': '256M'}
            }
        }
    },
    'slowapi-service': {
        'build': {'context': './containers/github_repos/slowapi', 'dockerfile': 'Dockerfile'},
        'image': 'dix-slowapi:latest',
        'container_name': 'dix-slowapi-service',
        'ports': ['9179:9179'],
        'volumes': [
            './containers/github_repos/slowapi/config:/app/config',
            './containers/github_repos/slowapi/data:/app/data',
            './containers/github_repos/slowapi/logs:/app/logs'
        ],
        'environment': ['SLOWAPI_LOG_LEVEL=INFO'],
        'restart': 'unless-stopped',
        'networks': ['dixvision-network'],
        'healthcheck': {
            'test': ['CMD', 'python', '/app/health_check.py'],
            'interval': '30s',
            'timeout': '10s',
            'retries': 3
        },
        'deploy': {
            'resources': {
                'limits': {'cpus': '1.0', 'memory': '512M'},
                'reservations': {'cpus': '0.5', 'memory': '256M'}
            }
        }
    },
    'flask-limiter-service': {
        'build': {'context': './containers/github_repos/flask-limiter', 'dockerfile': 'Dockerfile'},
        'image': 'dix-flask-limiter:latest',
        'container_name': 'dix-flask-limiter-service',
        'ports': ['9180:9180'],
        'volumes': [
            './containers/github_repos/flask-limiter/config:/app/config',
            './containers/github_repos/flask-limiter/data:/app/data',
            './containers/github_repos/flask-limiter/logs:/app/logs'
        ],
        'environment': ['FLASK_LIMITER_LOG_LEVEL=INFO'],
        'restart': 'unless-stopped',
        'networks': ['dixvision-network'],
        'healthcheck': {
            'test': ['CMD', 'python', '/app/health_check.py'],
            'interval': '30s',
            'timeout': '10s',
            'retries': 3
        },
        'deploy': {
            'resources': {
                'limits': {'cpus': '1.0', 'memory': '512M'},
                'reservations': {'cpus': '0.5', 'memory': '256M'}
            }
        }
    },
    'redis-py-cluster-service': {
        'build': {'context': './containers/github_repos/redis-py-cluster', 'dockerfile': 'Dockerfile'},
        'image': 'dix-redis-py-cluster:latest',
        'container_name': 'dix-redis-py-cluster-service',
        'ports': ['9181:9181'],
        'volumes': [
            './containers/github_repos/redis-py-cluster/config:/app/config',
            './containers/github_repos/redis-py-cluster/data:/app/data',
            './containers/github_repos/redis-py-cluster/logs:/app/logs'
        ],
        'environment': ['REDIS_PY_CLUSTER_LOG_LEVEL=INFO'],
        'restart': 'unless-stopped',
        'networks': ['dixvision-network'],
        'healthcheck': {
            'test': ['CMD', 'python', '/app/health_check.py'],
            'interval': '30s',
            'timeout': '10s',
            'retries': 3
        },
        'deploy': {
            'resources': {
                'limits': {'cpus': '1.0', 'memory': '512M'},
                'reservations': {'cpus': '0.5', 'memory': '256M'}
            }
        }
    },
    'python-jose-service': {
        'build': {'context': './containers/github_repos/python-jose', 'dockerfile': 'Dockerfile'},
        'image': 'dix-python-jose:latest',
        'container_name': 'dix-python-jose-service',
        'ports': ['9182:9182'],
        'volumes': [
            './containers/github_repos/python-jose/config:/app/config',
            './containers/github_repos/python-jose/data:/app/data',
            './containers/github_repos/python-jose/logs:/app/logs'
        ],
        'environment': ['PYTHON_JOSE_LOG_LEVEL=INFO'],
        'restart': 'unless-stopped',
        'networks': ['dixvision-network'],
        'healthcheck': {
            'test': ['CMD', 'python', '/app/health_check.py'],
            'interval': '30s',
            'timeout': '10s',
            'retries': 3
        },
        'deploy': {
            'resources': {
                'limits': {'cpus': '1.0', 'memory': '512M'},
                'reservations': {'cpus': '0.5', 'memory': '256M'}
            }
        }
    },
    'passlib-service': {
        'build': {'context': './containers/github_repos/passlib', 'dockerfile': 'Dockerfile'},
        'image': 'dix-passlib:latest',
        'container_name': 'dix-passlib-service',
        'ports': ['9183:9183'],
        'volumes': [
            './containers/github_repos/passlib/config:/app/config',
            './containers/github_repos/passlib/data:/app/data',
            './containers/github_repos/passlib/logs:/app/logs'
        ],
        'environment': ['PASSLIB_LOG_LEVEL=INFO'],
        'restart': 'unless-stopped',
        'networks': ['dixvision-network'],
        'healthcheck': {
            'test': ['CMD', 'python', '/app/health_check.py'],
            'interval': '30s',
            'timeout': '10s',
            'retries': 3
        },
        'deploy': {
            'resources': {
                'limits': {'cpus': '1.0', 'memory': '512M'},
                'reservations': {'cpus': '0.5', 'memory': '256M'}
            }
        }
    },
    'kombu-service': {
        'build': {'context': './containers/github_repos/kombu', 'dockerfile': 'Dockerfile'},
        'image': 'dix-kombu:latest',
        'container_name': 'dix-kombu-service',
        'ports': ['9184:9184'],
        'volumes': [
            './containers/github_repos/kombu/config:/app/config',
            './containers/github_repos/kombu/data:/app/data',
            './containers/github_repos/kombu/logs:/app/logs'
        ],
        'environment': ['KOMBU_LOG_LEVEL=INFO'],
        'restart': 'unless-stopped',
        'networks': ['dixvision-network'],
        'healthcheck': {
            'test': ['CMD', 'python', '/app/health_check.py'],
            'interval': '30s',
            'timeout': '10s',
            'retries': 3
        },
        'deploy': {
            'resources': {
                'limits': {'cpus': '1.0', 'memory': '512M'},
                'reservations': {'cpus': '0.5', 'memory': '256M'}
            }
        }
    }
}

# Add new services to existing ones
data['services'].update(new_services)

# Write back to compose.yaml
with open('compose.yaml', 'w') as f:
    yaml.dump(data, f, default_flow_style=False, sort_keys=False)

print(f"Added {len(new_services)} new services to compose.yaml")
print(f"Total services: {len(data['services'])}")
