import requests
import time
import base64
from django.conf import settings


class Judge0Service:
    """Service to interact with Judge0 API for code execution"""
    
    # Language IDs for Judge0
    LANGUAGE_IDS = {
        'python': 71,      # Python 3
        'javascript': 63,  # JavaScript (Node.js)
        'java': 62,        # Java
        'cpp': 54,         # C++ (GCC 9.2.0)
    }
    
    def __init__(self):
        self.api_url = settings.JUDGE0_API_URL
        self.api_key = settings.JUDGE0_API_KEY
        self.headers = {
            'Content-Type': 'application/json',
        }
        if self.api_key:
            self.headers['X-RapidAPI-Key'] = self.api_key
    
    def submit_code(self, code, language, stdin='', expected_output=''):
        """Submit code to Judge0 for execution"""
        
        language_id = self.LANGUAGE_IDS.get(language)
        if not language_id:
            raise ValueError(f"Unsupported language: {language}")
        
        # Encode code and input/output
        encoded_code = base64.b64encode(code.encode()).decode()
        encoded_stdin = base64.b64encode(stdin.encode()).decode()
        encoded_expected_output = base64.b64encode(expected_output.encode()).decode()
        
        payload = {
            'source_code': encoded_code,
            'language_id': language_id,
            'stdin': encoded_stdin,
            'expected_output': encoded_expected_output,
        }
        
        try:
            response = requests.post(
                f'{self.api_url}/submissions',
                json=payload,
                headers=self.headers,
                params={'base64_encoded': 'true', 'wait': 'false'}
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Judge0 API error: {str(e)}")
    
    def get_submission(self, token):
        """Get submission result from Judge0"""
        
        try:
            response = requests.get(
                f'{self.api_url}/submissions/{token}',
                headers=self.headers,
                params={'base64_encoded': 'true'}
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Judge0 API error: {str(e)}")
    
    def wait_for_result(self, token, max_attempts=10, delay=1):
        """Poll Judge0 until submission is processed"""
        
        for _ in range(max_attempts):
            result = self.get_submission(token)
            status_id = result.get('status', {}).get('id')
            
            # Status IDs: 1-2 = In Queue/Processing, 3+ = Finished
            if status_id and status_id > 2:
                return result
            
            time.sleep(delay)
        
        raise Exception("Timeout waiting for Judge0 result")
    
    def run_test_case(self, code, language, input_data, expected_output):
        """Run code against a single test case"""
        
        # Submit code
        submission = self.submit_code(code, language, input_data, expected_output)
        token = submission.get('token')
        
        if not token:
            raise Exception("Failed to get submission token from Judge0")
        
        # Wait for result
        result = self.wait_for_result(token)
        
        # Parse result
        return self.parse_result(result)
    
    def parse_result(self, result):
        """Parse Judge0 result into a standardized format"""
        
        status = result.get('status', {})
        status_id = status.get('id')
        status_description = status.get('description', 'Unknown')
        
        # Decode outputs
        stdout = self.decode_base64(result.get('stdout', ''))
        stderr = self.decode_base64(result.get('stderr', ''))
        compile_output = self.decode_base64(result.get('compile_output', ''))
        
        # Map Judge0 status to our status
        status_map = {
            3: 'Accepted',              # Accepted
            4: 'Wrong Answer',          # Wrong Answer
            5: 'Time Limit Exceeded',   # Time Limit Exceeded
            6: 'Compilation Error',     # Compilation Error
            7: 'Runtime Error',         # Runtime Error (SIGSEGV)
            8: 'Runtime Error',         # Runtime Error (SIGXFSZ)
            9: 'Runtime Error',         # Runtime Error (SIGFPE)
            10: 'Runtime Error',        # Runtime Error (SIGABRT)
            11: 'Runtime Error',        # Runtime Error (NZEC)
            12: 'Runtime Error',        # Runtime Error (Other)
            13: 'Internal Error',       # Internal Error
            14: 'Internal Error',       # Exec Format Error
        }
        
        parsed_status = status_map.get(status_id, 'Internal Error')
        
        return {
            'status': parsed_status,
            'status_id': status_id,
            'status_description': status_description,
            'runtime': result.get('time'),  # in seconds
            'memory': result.get('memory'),  # in KB
            'stdout': stdout,
            'stderr': stderr,
            'compile_output': compile_output,
            'error_message': stderr or compile_output or '',
        }
    
    @staticmethod
    def decode_base64(encoded_str):
        """Decode base64 encoded string"""
        if not encoded_str:
            return ''
        try:
            return base64.b64decode(encoded_str).decode()
        except Exception:
            return encoded_str
