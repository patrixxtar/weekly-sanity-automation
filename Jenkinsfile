pipeline {
    // This tells Jenkins to run the job on your VPS host, not inside the Docker container
    agent { 
        label 'vps-agent' // Ensure this matches the exact name of the node you created in Jenkins
    }

    environment {
        // Forces Python to output logs immediately to Jenkins console
        PYTHONUNBUFFERED = '1'
        // Sets a consistent path for the virtual environment
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
                // Prevents old videos and screenshots from bloating your VPS storage
                sh """
                    rm -f **/*.mp4
                    rm -rf failures/
                    rm -rf test_results/
                    mkdir -p test_results
                """
            }
        }

        stage('Parallel Test Execution') {
            // The matrix block automatically handles parallelization
            matrix {
                axes {
                    axis {
                        name 'BRAND'
                        values 'bell', 'virgin'
                    }
                    axis {
                        name 'DEVICE'
                        values 'desktop', 'galaxy_s24_fe', 'tablet_desktop_ui'
                    }
                }
                stages {
                    stage('Run Test') {
                        steps {
                            script {
                                def testFile = "tests/test_${env.BRAND}_byod.py"
                                // Generate a unique XML report name for each parallel run to avoid overwrites
                                def xmlReport = "test_results/junit_${env.BRAND}_${env.DEVICE}.xml"

                                echo "🚀 Executing in Parallel: Brand=${env.BRAND} | Device=${env.DEVICE}"

                                // catchError ensures one failed test doesn't stop the whole pipeline from archiving artifacts
                                catchError(buildResult: 'UNSTABLE', stageResult: 'FAILURE') {
                                    sh """
                                        . ${VENV_PATH}/bin/activate
                                        pytest ${testFile} \
                                            --device ${env.DEVICE} \
                                            --upc false \
                                            -s -v \
                                            --junitxml=${xmlReport}
                                    """
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
            
            // Generates the Pass/Fail trend graph using the JUnit plugin
            junit testResults: 'test_results/*.xml', allowEmptyResults: true

            // Uploads the videos, screenshots, and logs to the Jenkins UI
            archiveArtifacts artifacts: '**/*.mp4, failures/*.png, failures/*.txt', allowEmptyArchive: true
        }
    }
}