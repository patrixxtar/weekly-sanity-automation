pipeline {
    agent { 
        label 'vps-agent' 
    }

    environment {
        // Defines the folder where your actual Python scripts live
        SCRIPT_DIR = 'selenium-web-automation/byod-automation-mvp2'
        PYTHONUNBUFFERED = '1'
    }

    stages {
        stage('Parallel Execution') {
            parallel {
                // Bell Brand Permutations
                stage('Bell Desktop') { steps { runTest('bell', 'desktop') } }
                stage('Bell Mobile') { steps { runTest('bell', 'mobile') } }
                stage('Bell Tablet') { steps { runTest('bell', 'tablet') } }
                
                // Virgin Brand Permutations
                stage('Virgin Desktop') { steps { runTest('virgin', 'desktop') } }
                stage('Virgin Mobile') { steps { runTest('virgin', 'mobile') } }
                stage('Virgin Tablet') { steps { runTest('virgin', 'tablet') } }
            }
        }
    }

    post {
        always {
            // Clean up: Archive artifacts and gather reports
            junit "${SCRIPT_DIR}/results_*.xml"
            archiveArtifacts artifacts: "${SCRIPT_DIR}/**/*.mp4, ${SCRIPT_DIR}/failures/*.png, ${SCRIPT_DIR}/failures/*.txt", allowEmptyArchive: true
            
            // Housekeeping: remove heavy video/report files to keep VPS disk clean
            sh "rm -f ${SCRIPT_DIR}/results_*.xml ${SCRIPT_DIR}/**/*.mp4"
        }
    }
}

// Reusable function to handle the test execution logic
def runTest(brand, device) {
    def upc = (brand == 'bell') ? 'true' : 'false'
    // Create a totally unique venv name for this specific parallel thread
    def venvName = "venv_${brand}_${device}"
    
    sh """
        cd ${SCRIPT_DIR}
        
        # Ensure a completely isolated virtual environment exists for this thread
        [ -d ${venvName} ] || python3 -m venv ${venvName}
        . ${venvName}/bin/activate
        
        # Install dependencies inside this specific environment safely
        pip install -r ../../requirements.txt
        
        # Execute tests using headless virtual display
        xvfb-run --auto-servernum python3 -m pytest tests/test_${brand}_byod.py \
            --device ${device} \
            --upc ${upc} \
            -s -v \
            --junitxml=results_${brand}_${device}.xml
    """
}
