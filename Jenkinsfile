pipeline {
    agent any

    environment {
        DOCKER_IMAGE = 'journal-tracker'
        DOCKER_TAG = "latest"
        // In a real environment, KUBECONFIG would be a credential
        // KUBECONFIG = credentials('kubeconfig-credentials-id')
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Test & Lint') {
            steps {
                sh '''
                pip install -r requirements.txt
                # Add test commands here, for example:
                # pytest tests/
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    dockerImage = docker.build("${DOCKER_IMAGE}:${DOCKER_TAG}")
                }
            }
        }

        stage('Push Docker Image') {
            steps {
                script {
                    echo "Skipping Docker push for local Minikube demonstration."
                    // docker.withRegistry('https://index.docker.io/v1/', 'dockerhub-credentials-id') {
                    //     dockerImage.push()
                    //     dockerImage.push('latest')
                    // }
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                sh '''
                echo "Deploying to local Minikube cluster"
                # If running locally without credentials:
                kubectl apply -f k8s/
                kubectl rollout restart deployment/journal-tracker-deployment
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
