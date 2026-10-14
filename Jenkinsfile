pipeline {
    agent any

    environment {
        DOCKER_IMAGE = 'journal-tracker'
        REGISTRY_CREDENTIALS_ID = 'docker-hub-credentials'
        AWS_CREDENTIALS_ID = 'aws-credentials'
        GROQ_API_KEY = credentials('groq-api-key')
        KUBECONFIG_ID = 'kubeconfig-eks'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                sh '''
                    python -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Lint') {
            steps {
                sh '''
                    . venv/bin/activate
                    pip install flake8
                    flake8 app/ tests/ --count --max-line-length=120 --statistics || true
                '''
            }
        }

        stage('Run Unit Tests') {
            steps {
                sh '''
                    . venv/bin/activate
                    python -m pytest --junitxml=test-results.xml
                '''
            }
            post {
                always {
                    junit 'test-results.xml'
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                sh 'docker build -t ${DOCKER_IMAGE}:${BUILD_NUMBER} .'
                sh 'docker tag ${DOCKER_IMAGE}:${BUILD_NUMBER} ${DOCKER_IMAGE}:latest'
            }
        }

        stage('Push Docker Image') {
            steps {
                script {
                    docker.withRegistry('', REGISTRY_CREDENTIALS_ID) {
                        docker.image("${DOCKER_IMAGE}:${BUILD_NUMBER}").push()
                        docker.image("${DOCKER_IMAGE}:latest").push()
                    }
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                withCredentials([file(credentialsId: KUBECONFIG_ID, variable: 'KUBECONFIG')]) {
                    sh '''
                        kubectl apply -f k8s/namespace.yaml
                        kubectl apply -f k8s/configmap.yaml
                        kubectl apply -f k8s/secret.yaml
                        kubectl apply -f k8s/deployment.yaml
                        kubectl apply -f k8s/service.yaml
                        kubectl apply -f k8s/ingress.yaml
                        kubectl apply -f k8s/hpa.yaml
                        kubectl set image deployment/tracker-web tracker-container=${DOCKER_IMAGE}:${BUILD_NUMBER} -n research-tracker
                        kubectl rollout status deployment/tracker-web -n research-tracker
                    '''
                }
            }
        }
    }

    post {
        success {
            echo 'CI/CD Pipeline Completed Successfully!'
        }
        failure {
            echo 'Pipeline failed. Please inspect build logs.'
        }
    }
}
