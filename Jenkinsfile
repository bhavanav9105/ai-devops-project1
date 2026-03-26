pipeline {
    agent any

    stages {

        stage('Clone Repo') {
            steps {
                git branch: 'main', url: 'https://github.com/Spoorthisgowda20s/ai-devops-project1.git'
            }
        }

        stage('Build Docker Image') {
            steps {
                bat 'docker build -t ai-devops-app .'
            }
        }

        stage('Stop Old Containers') {
            steps {
                bat 'docker rm -f ai-devops-dev ai-devops-test ai-devops-prod || exit 0'
                bat 'docker-compose down || exit 0'
            }
        }

        stage('Run All Environments') {
            steps {
                bat 'docker-compose up -d'
            }
        }

    }

    post {
        success { echo '✅ DEV:8081  TEST:8082  PROD:8083' }
        failure { echo '❌ Failed' }
    }
}