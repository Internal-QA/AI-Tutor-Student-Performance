
import sys
import os
import csv
import time
import random
import argparse
import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def setup_logging():
    """Setup logging to both console and file"""
    # Create logs directory if it doesn't exist
    log_dir = "../results/logs"
    os.makedirs(log_dir, exist_ok=True)
    
    # Create log filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = os.path.join(log_dir, f"student_ppt_viewer_{timestamp}.log")
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return log_file

def log_print(message):
    """Print to console and log to file"""
    print(message)
    logging.info(message)

def load_config():
    """Load configuration from test_config.properties"""
    config = {}
    config_file = "../config/test_config.properties"
    
    if not os.path.exists(config_file):
        print(f"Config file not found: {config_file}")
        exit(1)
    
    with open(config_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                key, value = line.split('=', 1)
                config[key] = value
    
    return config

def load_student_credentials():
    """Load student credentials from the saved CSV file"""
    credentials_file = "../data/student_credentials.csv"
    
    if not os.path.exists(credentials_file):
        print(f"Credentials file not found: {credentials_file}")
        print("Please run create_students.py first to create students")
        return []
    
    credentials = []
    with open(credentials_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            credentials.append({
                'email': row['email'],
                'password': row['password']
            })
    
    return credentials

def generate_background_aspirations(config):
    """Generate simple 200-300 word background aspirations using business keywords from config"""
    # Read keywords from config
    keywords = config['BUSINESS_KEYWORDS'].split(',')
    keywords = [keyword.strip() for keyword in keywords]  # Remove any extra spaces
    
    # Select random keywords
    selected_keywords = random.sample(keywords, random.randint(8, 12))
    keyword_text = ", ".join(selected_keywords)
    
    # Get template from config and substitute keywords
    template = config['ASPIRATIONS_TEMPLATE']
    paragraph = template.format(keywords=keyword_text)
    
    return paragraph

def get_session_number(student_email, credentials_list):
    """Determine session number based on batches of 25 students (1-4)"""
    # Find student position in the credentials list
    try:
        # Find the index of current student in the list
        for i, cred in enumerate(credentials_list):
            if cred['email'] == student_email:
                student_index = i + 1  # 1-based index
                break
        else:
            # If not found, use random
            return random.randint(1, 4)
        
        # Assign sessions based on batches of 25
        if student_index <= 25:
            return 1
        elif student_index <= 50:
            return 2
        elif student_index <= 75:
            return 3
        else:
            return 4
            
    except:
        # Fallback to random session if anything fails
        return random.randint(1, 4)

def setup_driver(config):
    """Setup Chrome WebDriver in headless mode"""
    chrome_options = Options()
    
    # Always run in headless mode
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-images")
    chrome_options.add_argument("--disable-plugins")
    chrome_options.add_argument("--disable-background-timer-throttling")
    chrome_options.add_argument("--disable-backgrounding-occluded-windows")
    chrome_options.add_argument("--disable-renderer-backgrounding")
    chrome_options.add_argument("--remote-debugging-port=9222")
    
    window_size = config.get('WINDOW_SIZE', '1920,1080')
    chrome_options.add_argument(f"--window-size={window_size}")
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--allow-running-insecure-content")
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        return driver
    except Exception as e:
        print(f"Error setting up Chrome driver: {e}")
        print("Make sure ChromeDriver is installed and in PATH")
        return None

def run_student_session(student, config, student_index, total_students):
    """Run a single student session"""
    start_time = datetime.now()
    
    # Setup WebDriver
    driver = setup_driver(config)
    if not driver:
        print(f"ERROR: Failed to setup WebDriver for student {student_index + 1}")
        return False
    
    try:
        
        # Step 1: Navigate to AI Tutor URL
        login_url = config['LOGIN_URL']
        print(f"Navigating to: {login_url}")
        driver.get(login_url)
        
        # Load initial page and click Student button
        initial_timeout = int(config.get('INITIAL_PAGE_TIMEOUT', 30))
        wait = WebDriverWait(driver, initial_timeout)
        
        # Explicit wait for page ready
        wait.until(lambda driver: driver.execute_script("return document.readyState") == "complete")
        
        try:
            # Explicit wait for Student button
            student_button = wait.until(EC.element_to_be_clickable((By.XPATH, config['STUDENT_BUTTON_XPATH'])))
            student_button.click()
            
            # Explicit wait for page transition
            time.sleep(3)
        except TimeoutException as e:
            print(f"Student button not found: {e}")
            logging.error(f"FAILURE_STEP_STUDENT_BUTTON: {student['email']} - {e}")
            raise
        
        # Fill login form with explicit waits
        element_timeout = int(config.get('ELEMENT_WAIT_TIMEOUT', 30))
        wait = WebDriverWait(driver, element_timeout)
        
        try:
            # Explicit wait for email field
            email_field = wait.until(EC.element_to_be_clickable((By.XPATH, config['EMAIL_FIELD_XPATH'])))
            email_field.clear()
            email_field.send_keys(student['email'])
            
            # Explicit wait for password field
            password_field = wait.until(EC.element_to_be_clickable((By.XPATH, config['PASSWORD_FIELD_XPATH'])))
            password_field.clear()
            password_field.send_keys(student['password'])
            
            # Explicit wait for login button
            login_button = wait.until(EC.element_to_be_clickable((By.XPATH, config['LOGIN_BUTTON_XPATH'])))
            login_button.click()
            print("Login completed")
            
        except TimeoutException as e:
            print(f"Login failed: {e}")
            logging.error(f"FAILURE_STEP_LOGIN_FORM: {student['email']} - {e}")
            raise
        
        # Check for aspirations page with explicit wait
        aspirations_timeout = int(config.get('ASPIRATIONS_WAIT_TIMEOUT', 10))
        aspirations_wait = WebDriverWait(driver, aspirations_timeout)
        
        try:
            # Explicit wait for aspirations field
            aspirations_field = aspirations_wait.until(EC.element_to_be_clickable((By.XPATH, config['BACKGROUND_ASPIRATIONS_XPATH'])))
            aspirations_field.click()
            
            aspirations_text = generate_background_aspirations(config)
            aspirations_field.clear()
            aspirations_field.send_keys(aspirations_text)
            
            # Explicit wait for submit button
            submit_button = aspirations_wait.until(EC.element_to_be_clickable((By.XPATH, config['SUBMIT_INFORMATION_BUTTON_XPATH'])))
            submit_button.click()
            print("Aspirations completed")
            
        except TimeoutException:
            print("Aspirations skipped")
        
        # Navigate to sessions with explicit waits
        try:
            # Explicit wait for navigation link
            nav_link = wait.until(EC.element_to_be_clickable((By.XPATH, config['NAVIGATION_ENROLLED_UNITS_XPATH'])))
            nav_link.click()
            
            # Explicit wait for View Details button
            view_details_button = wait.until(EC.element_to_be_clickable((By.XPATH, config['VIEW_DETAILS_BUTTON_XPATH'])))
            view_details_button.click()
            
            # Explicit wait for sessions list
            wait.until(EC.presence_of_element_located((By.XPATH, "//tbody/tr[1]/td[6]/button[1]")))
            
            # Explicit wait for session button
            session_number = get_session_number(student['email'], credentials)
            session_xpath = config['SESSION_BUTTON_XPATH'].format(session_number=session_number)
            session_button = wait.until(EC.element_to_be_clickable((By.XPATH, session_xpath)))
            session_button.click()
            print(f"Session {session_number} selected")
            
        except TimeoutException as e:
            print(f"Navigation failed: {e}")
            logging.error(f"FAILURE_STEP_NAVIGATION: {student['email']} - {e}")
            raise
        
        # View PPT presentation with fluent wait for container
        try:
            # Fluent wait for PPT container - 20 minutes with 2-minute polling
            ppt_fluent_wait = WebDriverWait(driver, timeout=1200, poll_frequency=120)
            ppt_container = ppt_fluent_wait.until(
                EC.visibility_of_element_located((By.XPATH, config['PPT_CONTAINER_XPATH']))
            )
            
            # Explicit wait for PPT play button
            ppt_play_button = wait.until(EC.element_to_be_clickable((By.XPATH, config['PPT_PLAY_BUTTON_XPATH'])))
            ppt_play_button.click()
            
            viewing_duration = int(config.get('PPT_VIEWING_DURATION', 300))
            print(f"PPT viewing started ({viewing_duration}s)")
            time.sleep(viewing_duration)
            print("PPT viewing completed")
            
            # Open AI chatbot with explicit waits
            try:
                # Explicit wait for Raise Hand button
                raise_hand_button = wait.until(EC.element_to_be_clickable((By.XPATH, config['RAISE_HAND_BUTTON_XPATH'])))
                raise_hand_button.click()
                
                # Explicit wait for chat container
                wait.until(EC.visibility_of_element_located((By.XPATH, config['AI_CHAT_CONTAINER_XPATH'])))
                
                # Explicit wait for message textarea
                message_textarea = wait.until(EC.element_to_be_clickable((By.XPATH, config['AI_MESSAGE_TEXTAREA_XPATH'])))
                
                chat_question = config.get('AI_CHAT_QUESTION', 'how will mba benefit my career?')
                message_textarea.click()
                message_textarea.clear()
                message_textarea.send_keys(chat_question)
                
                # Explicit wait for send button
                send_button = wait.until(EC.element_to_be_clickable((By.XPATH, config['AI_SEND_BUTTON_XPATH'])))
                send_button.click()
                
                print("Chatbot interaction completed")
                
            except TimeoutException as e:
                print(f"Chatbot failed: {e}")
                logging.error(f"FAILURE_STEP_CHATBOT_TIMEOUT: {student['email']} - {e}")
                raise Exception("CHATBOT_OPEN_FAILURE: AI chatbot could not be opened after PPT viewing")
            except Exception as e:
                print(f"Chatbot error: {e}")
                logging.error(f"FAILURE_STEP_CHATBOT_ERROR: {student['email']} - {e}")
                raise Exception(f"CHATBOT_OPEN_FAILURE: {str(e)}")
            
        except TimeoutException:
            print("PPT container not found")
            logging.error(f"FAILURE_STEP_PPT_CONTAINER: {student['email']}")
            raise Exception("PPT_CONTAINER_NOT_FOUND: PPT container could not be loaded")

        # Session completed
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        print(f"Student {student_index + 1} completed ({duration:.1f}s)")
        return True
    
    except TimeoutException as e:
        print(f"Student {student_index + 1} timeout: {e}")
        logging.error(f"FAILURE_STEP_TIMEOUT: {student['email']} - {e}")
        return False
    except NoSuchElementException as e:
        print(f"Student {student_index + 1} element not found: {e}")
        logging.error(f"FAILURE_STEP_ELEMENT_NOT_FOUND: {student['email']} - {e}")
        return False
    except Exception as e:
        print(f"Student {student_index + 1} error: {e}")
        logging.error(f"FAILURE_STEP_UNEXPECTED: {student['email']} - {e}")
        return False
    
    finally:
        driver.quit()

def main():
    """Main function to run batch student sessions"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='AI Tutor Student PPT Viewer - Headless Batch Processing')
    parser.add_argument('--students', type=int, help='Number of students to test (overrides config)')
    args = parser.parse_args()
    
    # Setup logging first
    log_file = setup_logging()
    
    log_print("AI Tutor Student PPT Viewer - Headless Batch Processing")
    log_print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log_print(f"Log file: {log_file}")
    
    # Load configuration and credentials
    config = load_config()
    credentials = load_student_credentials()
    
    if not credentials:
        log_print("ERROR: No student credentials found")
        return
    
    # Determine execution parameters
    if args.students:
        total_students = args.students
        log_print(f"Command line override: {total_students} students")
    else:
        total_students = int(config.get('TOTAL_STUDENTS', len(credentials)))
    
    # Validate student count
    if total_students > len(credentials):
        total_students = len(credentials)
        log_print(f"WARNING: Limited to {total_students} students (available credentials)")
    
    log_print(f"Target: {total_students} students")
    log_print(f"Available credentials: {len(credentials)} students")
    log_print("Execution mode: Headless (server optimized)")
    log_print(f"Request delay: {config.get('REQUEST_DELAY', 0.1)}s between students")
    
    # Track results
    successful_sessions = 0
    failed_sessions = 0
    start_time = datetime.now()
    
    # Process students sequentially
    for i in range(total_students):
        student = credentials[i]
        
        log_print(f"Starting student {i+1}/{total_students}: {student['email']}")
        
        success = run_student_session(student, config, i, total_students)
        
        if success:
            successful_sessions += 1
        else:
            failed_sessions += 1
        
        # Progress update
        progress = ((i + 1) / total_students) * 100
        log_print(f"Progress: {i+1}/{total_students} ({progress:.1f}%) - Success: {successful_sessions}, Failed: {failed_sessions}")
        
        # Add delay between students
        request_delay = float(config.get('REQUEST_DELAY', 0.1))
        if request_delay > 0 and i < total_students - 1:
            time.sleep(request_delay)
    
    # Final summary
    end_time = datetime.now()
    total_duration = (end_time - start_time).total_seconds()
    
    log_print(f"\nBATCH EXECUTION SUMMARY")
    log_print(f"Successful sessions: {successful_sessions}")
    log_print(f"Failed sessions: {failed_sessions}")
    log_print(f"Success rate: {(successful_sessions/total_students)*100:.1f}%")
    log_print(f"Total duration: {total_duration:.1f} seconds")
    log_print(f"Average per student: {total_duration/total_students:.1f} seconds")
    log_print(f"Completed at: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    log_print(f"Log file: {log_file}")
    
    # Log summary for parsing
    logging.info(f"BATCH_SUMMARY: total={total_students}, success={successful_sessions}, failed={failed_sessions}, rate={(successful_sessions/total_students)*100:.1f}%, duration={total_duration:.1f}s")
    
    # Log failure summary if there were failures
    if failed_sessions > 0:
        log_print(f"Failure Analysis: {failed_sessions} total failures")
        logging.info(f"FAILURE_ANALYSIS: total_failures={failed_sessions}")

if __name__ == "__main__":
    main() 