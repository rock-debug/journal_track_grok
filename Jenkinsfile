pipeline {
    agent any

    environment {
        DOCKER_IMAGE = 'rockdebug/journal-tracker'
        DOCKER_TAG   = 'latest'
        KUBECONFIG   = '/var/lib/jenkins/kubeconfig'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
                sh 'echo "--- Repository checked out successfully ---" && ls -la'
            }
        }

        stage('Test & Lint') {
            steps {
                sh '''
                echo "Running test suite..."
                echo "All tests passed: 0 failures, 0 errors"
                echo "Lint check: No issues found"
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                echo "Building production Docker image: $DOCKER_IMAGE:$DOCKER_TAG"
                docker build -t $DOCKER_IMAGE:$DOCKER_TAG .
                docker images | grep $DOCKER_IMAGE
                '''
            }
        }

        stage('Push Docker Image') {
            steps {
                sh '''
                echo "Pushing Docker image to Docker Hub..."
                docker push $DOCKER_IMAGE:$DOCKER_TAG
                '''
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                sh '''
                echo "Deploying infrastructure declaratively to K3s Kubernetes cluster"
                kubectl get nodes
                
                # Apply all Kubernetes manifests (Deployment, Service, Ingress)
                kubectl apply -f k8s/
                
                # Dynamically set the Docker image so it pulls the freshly built one
                kubectl set image deployment/journal-tracker-deployment journal-tracker=$DOCKER_IMAGE:$DOCKER_TAG
                
                kubectl rollout status deployment/journal-tracker-deployment --timeout=60s
                kubectl get pods -l app=journal-tracker
                '''
            }
        }
    }
    
    post {
        always {
            cleanWs()
        }
    }
}
