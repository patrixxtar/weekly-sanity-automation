pipeline {
    agent { 
        label 'vps-agent' 
    }

    environment {
        PYTHONUNBUFFERED = '1'
        VENV_PATH = "${WORKSPACE}/venv"
    }

    stages {
        stage('Setup Environment') {
            steps {
                echo "Setting up Python Virtual Environment on the VPS Host..."
                sh """
                    python3 -m venv ${VENV_PATH}
                    . ${VENV_PATH}/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                """
            }
        }

        stage('Clean Old Artifacts') {
            steps {
                sh """
                    rm -f **/*.mp4
                    rm -rf failures/
                    rm -rf test_results/
                    mkdir -p test_results
                """
            }
        }

        stage('Parallel Test Execution') {
            matrix {
                axes {
                    axis {
                        name 'BRAND'
                        values 'bell', 'virgin'
                    }
                    axis {
                        name 'DEVICE'
                        values 'desktop', 'mobile', 'tablet'
                    }
                    axis {
                        name 'UPC'
                        values 'true', 'false'
                    }
                }
                
                // This block removes the "Virgin + UPC True" combinations, 
                // leaving exactly the 9 test runs you requested.
                excludes {
                    exclude {
                        axis {
                            name 'BRAND'
                            values 'virgin'
                        }
                        axis {
                            name 'UPC'
                            values 'true'
                        }
                    }
                }

                stages {
                    stage('Run Test') {
                        steps {
                            script {
                                // Navigate to the correct directory
                                dir('selenium-web-automation/byod-automation-mvp2') {
                                    withEnv(["PATH+PYTHON=${tool 'Python'}/bin", "PYTHONPATH=. "]) {
                                        // Now run your tests
                                        sh "pytest tests/test_bell_byod.py --device ${env.DEVICE} --upc ${env.UPC} -s -v"
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    post {
        always {
            echo "📦 Processing Test Results and Archiving Artifacts..."
            junit testResults: 'test_results/*.xml', allowEmptyResults: true
            archiveArtifacts artifacts: '**/*.mp4, failures/*.png, failures/*.txt', allowEmptyArchive: true
        }
    }
}