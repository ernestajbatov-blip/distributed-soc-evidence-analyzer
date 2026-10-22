pipeline {
    agent any

    environment {
        IMAGE_NAME = 'dsoc-evidence-analyzer'
        IMAGE_TAG = "${env.BUILD_NUMBER}"
    }

    options {
        timestamps()
        disableConcurrentBuilds()
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Unit Tests') {
            steps {
                sh '''
                    docker run --rm \
                      -v "$PWD:/workspace" \
                      -w /workspace \
                      python:3.13-slim \
                      sh -c "pip install -q pytest && PYTHONPATH=src pytest -q"
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                sh 'docker build --pull -t ${IMAGE_NAME}:${IMAGE_TAG} .'
            }
        }

        stage('Container Smoke Test') {
            steps {
                sh '''
                    docker run --rm ${IMAGE_NAME}:${IMAGE_TAG} \
                      data/sample_runs.csv > container-output.json
                    grep -q '"overall_pass": true' container-output.json
                '''
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'container-output.json', allowEmptyArchive: true
        }
        success {
            echo "CI succeeded: tests passed, Docker image built, smoke test passed."
        }
        cleanup {
            sh 'docker image rm -f ${IMAGE_NAME}:${IMAGE_TAG} || true'
        }
    }
}
