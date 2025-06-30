#!groovy


pipeline {
    agent any
    stages {
        stage("Build and up") {
            steps {
                sh "cp /home/romakot/workspace/envs/${GIT_URL.tokenize('/.')[-2]}.env .env"
                sh "cp /home/romakot/workspace/envs/${GIT_URL.tokenize('/.')[-2]}.proxychains.conf proxychains.conf"
                sh "docker compose up -d --build"
            }
        }
    }
}
