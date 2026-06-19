pipeline {
    agent any

    // Replaces the input() prompts from run_tests.py with Jenkins UI Dropdowns
    parameters {
        choice(name: 'BRAND', choices: ['bell', 'virgin'], description: 'Which brand?')
        choice(name: 'DEVICE', choices: ['desktop', 'mobile', 'tablet', 'galaxy_s24_fe', 'iphone_15_pro_max', 'tablet_mobile_ui', 'tablet_desktop_ui'], description: 'Which device profile?')
        booleanParam(name: 'UPC_ENABLED', defaultValue: false, description: 'Enable UPC? (Bell only)')
    }

    environment {
        // Keeps Python from buffering outputs so you see logs in real-time
        PYTHONUNBUFFERED = '1'
    }

    stages {
        stage('Setup Environment') {
            steps {
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    # Assuming you have a requirements.txt with pytest, selenium, pyvirtualdisplay
                    pip install -r requirements.txt 
                '''
            }
        }

        stage('Execute UI Tests') {
            steps {
                script {
                    // Force UPC to false if Virgin is selected, mirroring your run_tests.py logic
                    def upc_choice = (params.BRAND == 'bell' && params.UPC_ENABLED) ? 'true' : 'false'
                    
                    sh """
                        . venv/bin/activate
                        
                        # We use xvfb-run to wrap the pytest command. 
                        # This creates the virtual display that PyVirtualDisplay and ffmpeg require.
                        xvfb-run --auto-servernum python3 -m pytest tests/test_${params.BRAND}_byod.py \
                            --device ${params.DEVICE} \
                            --upc ${upc_choice} \
                            -s -v \
                            --junitxml=results.xml
                    """
                }
            }
        }
    }

    post {
        always {
            // 1. Process the JUnit XML test report
            junit testResults: 'results.xml', allowEmptyResults: true

            // 2. Save your MP4 recordings and failure screenshots/text files
            archiveArtifacts artifacts: '**/*.mp4, failures/*.png, failures/*.txt', allowEmptyArchive: true
            
            // 3. Clean up the heavy video files to save VPS disk space after archiving
            sh 'rm -f **/*.mp4'
        }
    }
}
