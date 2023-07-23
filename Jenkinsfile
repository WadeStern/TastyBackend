pipeline {
  agent { docker { image 'dudesm00thie/backendmaster:latest' } }
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
    /*stage('test') {
      steps {
        sh 'pytest -v --junitxml=test_report.xml'
      }
      post {
        always {
          junit 'test_report.xml'
        }
      }    
    }*/
    stage('deploy') {
     steps {
                sh 'docker build -t dudesmoothie/backend .'
                sh "docker tag ${NAME}:latest ${IMAGE_REPO}/${NAME}:${VERSION}"
                sh 'echo $DOCKERHUB_CREDENTIALS_PSW | docker login -u $DOCKERHUB_CREDENTIALS_USR --password-stdin'
                sh 'docker push dudesmoothie/backend'
                sh 'docker logout'

          }
        }   
      }
    }

