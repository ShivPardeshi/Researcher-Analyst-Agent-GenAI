pipeline {
    agent any

    environment {
        APP_NAME         = 'research-analyst-agents'
        IMAGE_NAME       = 'research-analyst-agents'
        IMAGE_TAG        = "${env.BUILD_NUMBER ?: 'latest'}"
        HOST_PORT        = '8000'
        TEST_CONTAINER   = 'research-analyst-ci-smoke-test'
    }

    stages {
        stage('Checkout SCM') {
            steps {
                echo "Fetching repository source code..."
                checkout scm
            }
        }

        stage('Verify Environment') {
            steps {
                echo "Checking system tools and Docker availability..."
                sh 'docker --version'
                sh 'python3 --version || python --version'
            }
        }

        stage('Run Unit & Integration Tests') {
            steps {
                echo "Running unit and integration tests inside isolated container..."
                // Build a lightweight test image and execute pytest
                sh '''
                    docker build -t ${IMAGE_NAME}:test .
                    docker run --rm ${IMAGE_NAME}:test pytest -v
                '''
            }
        }

        stage('Build Production Docker Image') {
            steps {
                echo "Building production Docker image: ${IMAGE_NAME}:${IMAGE_TAG}..."
                sh '''
                    docker build -t ${IMAGE_NAME}:${IMAGE_TAG} -t ${IMAGE_NAME}:latest .
                '''
            }
        }

        stage('Container Smoke & Health Check') {
            steps {
                echo "Deploying test container and verifying /health endpoint..."
                sh '''
                    # Stop previous smoke test container if left over
                    docker rm -f ${TEST_CONTAINER} 2>/dev/null || true

                    # Start container on dynamic port 8001 to prevent port conflicts on host
                    docker run -d --name ${TEST_CONTAINER} -p 8001:8000 -e PORT=8000 ${IMAGE_NAME}:latest

                    # Wait up to 30 seconds for healthy startup
                    echo "Waiting for container startup..."
                    sleep 5

                    # Determine reachable endpoint (host.docker.internal for Docker-in-Docker on Mac, or localhost)
                    MAX_RETRIES=8
                    COUNT=0
                    PASSED=false

                    while [ $COUNT -lt $MAX_RETRIES ]; do
                        echo "Probing container health (attempt $((COUNT + 1))/$MAX_RETRIES)..."
                        if curl -s -f http://host.docker.internal:8001/health >/dev/null 2>&1; then
                            echo "Health check PASSED via host.docker.internal:8001/health!"
                            curl -s http://host.docker.internal:8001/health
                            echo ""
                            PASSED=true
                            break
                        elif curl -s -f http://localhost:8001/health >/dev/null 2>&1; then
                            echo "Health check PASSED via localhost:8001/health!"
                            curl -s http://localhost:8001/health
                            echo ""
                            PASSED=true
                            break
                        elif docker exec ${TEST_CONTAINER} python3 -c "import urllib.request; resp=urllib.request.urlopen('http://127.0.0.1:8000/health'); print(resp.read().decode())" 2>/dev/null; then
                            echo "Health check PASSED directly inside container via 127.0.0.1:8000/health!"
                            PASSED=true
                            break
                        fi
                        sleep 4
                        COUNT=$((COUNT + 1))
                    done

                    if [ "$PASSED" = "false" ]; then
                        echo "Smoke test FAILED! Health endpoint did not respond within deadline."
                        docker logs ${TEST_CONTAINER}
                        docker rm -f ${TEST_CONTAINER}
                        exit 1
                    fi

                    # Cleanup smoke test container
                    docker rm -f ${TEST_CONTAINER}
                '''
            }
        }
    }

    post {
        always {
            echo "Cleaning up temporary CI test containers..."
            sh "docker rm -f ${TEST_CONTAINER} 2>/dev/null || true"
        }
        success {
            echo "=========================================================="
            echo "SUCCESS: Docker image '${IMAGE_NAME}:latest' built and verified!"
            echo "Access the application on host port ${HOST_PORT}."
            echo "Run: docker run -d -p 8000:8000 --env-file .env ${IMAGE_NAME}:latest"
            echo "=========================================================="
        }
        failure {
            echo "Pipeline build failed. Review stage logs above."
        }
    }
}
