pipeline {
    // Target the specific VPS node you set up
    agent { 
        label 'vps-agent' 
    }

    // These parameters replace your run_tests.py inputs
    parameters {
        choice(name: 'BRAND', choices: ['bell', 'virgin'], description: 'Which brand to test?')
        choice(name: 'DEVICE', choices: ['desktop', 'mobile', 'tablet', 'galaxy_s24_fe', 'iphone_15_pro_max', 'tablet_mobile_ui', 'tablet_desktop_ui'], description: 'Which device profile?')
        booleanParam(name: 'UPC', defaultValue: false, description: 'Run with UPC enabled? (Bell only)')
    }

    environment {
        // Ensure Python outputs directly to Jenkins console without buffering
        PYTHONUNBUFFERED = '1'
        // Define paths
        VENV_PATH = "${WORKSPACE}/venv"
        RESULTS_DIR = "${WORKSPACE}/test_results"
    }

    stages {
        stage('Setup Environment') {
            steps {
                script {
                    echo "Setting up Python Virtual Environment..."
                    sh """
                        python3 -m venv ${VENV_PATH}
                        . ${VENV_PATH}/bin/activate
                        
                        # Upgrade pip and install requirements
                        # Ensure you have a requirements.txt with pytest, selenium, pyvirtualdisplay, etc.
                        pip install --upgrade pip
                        pip install -r requirements.txt
                    """
                }
            }
        }

        stage('Clean Old Artifacts') {
            steps {
                // Remove old videos, screenshots, and logs so they don't bloat the workspace
                sh """
                    rm -f **/*.mp4
                    rm -rf failures/
                    rm -rf ${RESULTS_DIR}
                    mkdir -p ${RESULTS_DIR}
                """
            }
        }

        stage('Execute Pytest') {
            steps {
                script {
                    def upcFlag = params.UPC ? "true" : "false"
                    def testFile = "tests/test_${params.BRAND}_byod.py"
                    def xmlReport = "${RESULTS_DIR}/junit_report.xml"

                    echo "🚀 Running Tests: Brand=${params.BRAND}, Device=${params.DEVICE}, UPC=${upcFlag}"

                    // We use catchError to ensure the pipeline continues to the post block even if tests fail
                    catchError(buildResult: 'UNSTABLE', stageResult: 'FAILURE') {
                        sh """
                            . ${VENV_PATH}/bin/activate
                            pytest ${testFile} \
                                --device ${params.DEVICE} \
                                --upc ${upcFlag} \
                                -s -v \
                                --junitxml=${xmlReport}
                        """
                    }
                }
            }
        }
    }

    post {
        always {
            echo "📦 Archiving Test Artifacts..."
            
            // Archive JUnit XML for Jenkins Test Trend Graphs
            junit testResults: 'test_results/junit_report.xml', allowEmptyResults: true

            // Archive the videos (desktop-views, mobile-views, etc.) and failure screenshots
            archiveArtifacts artifacts: '**/*.mp4, failures/*.png, failures/*.txt', allowEmptyArchive: true
        }
        cleanup {
            echo "🧹 Cleaning up workspace to save VPS disk space..."
            // Optional: Uncomment the line below to wipe the workspace after the run
            // cleanWs()
        }
    }
}
