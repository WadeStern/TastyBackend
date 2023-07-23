pipeline {
  agent { docker { image 'python:3.10' } }
  options {
    buildDiscarder(logRotator(numToKeepStr: '5'))
  }
  environment { 
   NAME = "backend"
   VERSION = "${env.BUILD_ID}-${env.GIT_COMMIT}"
   IMAGE = "${NAME}:${VERSION}"
   DOCKERHUB_CREDENTIALS = credentials('dockerhub')
  }
  stages {
    stage('build') {
      steps {
        sh 'pip install -r requirements.txt'
      }
    }
    stage('test') {
      steps {
        sh "pip install pytest"
        sh "pytest test_main.py"
      }
      post {
        always {
          junit allowEmptyResults: true, testResults: '**/test-results/*.xml'
        }
      }    
    }
    stage('deploy') {
     steps {
                sh 'docker build -t dudesm00thie/jenkins-docker-hub .'
                sh 'docker build -t dudesmoothie/backend .'
                sh "docker tag ${NAME}:latest ${IMAGE_REPO}/${NAME}:${VERSION}"
                sh 'echo $DOCKERHUB_CREDENTIALS_PSW | docker login -u $DOCKERHUB_CREDENTIALS_USR --password-stdin'
                sh 'docker push dudesmoothie/backend'
                sh 'docker logout'

          }
        }   
      }
    }

