pipeline {
  agent { docker { image 'python:3.10' } }
  environment { 
   NAME = "backend"
   VERSION = "${env.BUILD_ID}-${env.GIT_COMMIT}"
   IMAGE = "${NAME}:${VERSION}"
   dockerHome = tool 'myDocker'
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
      script {
          withEnv(["PATH+${dockerHome}/bin"]) {
            echo "Running ${VERSION} on ${env.JENKINS_URL}"
            sh "docker build -t ${NAME} ."
            sh "docker tag ${NAME}:latest ${IMAGE_REPO}/${NAME}:${VERSION}"
          }
        }   
      }
    }
  }
}
