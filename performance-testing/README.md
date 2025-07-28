# AI Tutor Performance Testing Suite

This directory contains scripts for creating student accounts and automating student workflows using Selenium for the AI Tutor application.

## 📁 Directory Structure

```
performance-testing/
├── config/
│   └── test_config.properties           # All configuration settings (URLs, XPaths, credentials)
│
├── data/
│   └── student_credentials.csv          # Created student email/password pairs
│
├── scripts/
│   ├── create_students.py               # Create student accounts via API
│   └── student_ppt_viewer.py            # Student end-to-end workflow (Selenium)
│
├── utils/
│   └── load_credentials.py              # Utility to load student credentials
│
├── results/
│   ├── logs/                           # Execution logs
│   ├── raw/                            # Raw test data
│   ├── reports/                        # Generated reports
│   └── summary/                        # Summary reports
│
├── requirements.txt                     # Python dependencies
└── README.md                           # This file
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd performance-testing
pip install -r requirements.txt
```

### 2. Create Students

```bash
cd scripts
python3 create_students.py
```

This creates 100 students (configurable in `test_config.properties`) and saves their email/password to `../data/student_credentials.csv`.

### 3. Run Student Workflow

```bash
python3 student_ppt_viewer.py
```

This script performs the complete student journey:
- Login to AI Tutor portal
- Fill background aspirations form
- Navigate to enrolled units
- Select and view session details
- Click session based on student batch (1-25 → session 1, 26-50 → session 2, etc.)
- Wait for PPT to load (up to 10 minutes)
- Watch PPT for 5 minutes
- Ask AI question via chat

## ⚙️ Configuration

All settings are centralized in `config/test_config.properties`:

### API Configuration
```properties
API_BASE_URL=https://ai-tutor.shorthills.ai
API_ENDPOINT=/api/v2/student-management/admin/create-student
```

### Portal URLs
```properties
LOGIN_URL=https://main.d1m76fcdpw4qrl.amplifyapp.com/login
```

### Student Settings
```properties
TOTAL_STUDENTS=100
DEFAULT_PASSWORD=123456
PROGRAM_ID=686e41476649bb21dd9c98f1
COHORT_ID=686cdfeafec63ba9681d5af2
ACADEMIC_YEAR_ID=686ce13bfec63ba9681d5b04
```

### Selenium XPaths
All element locators are configured in the properties file for easy maintenance.

### Execution Settings
```properties
MAX_CONCURRENT_STUDENTS=100
EXECUTION_TIMEOUT=10800  # 3 hours
```

## 🎯 Student Workflow Details

The Selenium script performs these steps:

1. **Login Process**
   - Navigate to login URL
   - Click student button
   - Enter email/password from credentials CSV
   - Wait for page load

2. **Background Aspirations**
   - Fill aspirations textarea with business keywords
   - Submit information form

3. **Session Selection**
   - Navigate to enrolled units
   - Click view details
   - Select session based on student batch:
     - Students 1-25: Session 1
     - Students 26-50: Session 2  
     - Students 51-75: Session 3
     - Students 76-100: Session 4

4. **PPT Viewing**
   - Wait for PPT container to load (up to 10 minutes with 2-minute polling)
   - Click play button
   - Watch for 5 minutes

5. **AI Interaction**
   - Click "Raise Hand / Ask AI" button
   - Wait for chat container
   - Enter question: "how will mba benefit my career?"
   - Send message

## 🔧 Key Features

### Explicit Waits
- Uses `WebDriverWait` and `ExpectedConditions` instead of static sleeps
- Separate waits for login page and post-login elements
- Fluent wait for PPT loading with custom polling

### Configuration Management
- All URLs, XPaths, and settings in `test_config.properties`
- Easy to modify without changing code
- Centralized credential management

### Error Handling
- Try-catch blocks for common Selenium exceptions
- Proper browser cleanup in finally blocks
- Informative error messages

### Session Distribution
- Automatic session assignment based on student index
- Evenly distributes load across 4 sessions

## 📝 File Details

### `create_students.py`
- Creates students via API calls
- Saves only email/password to CSV (no JWT tokens)
- Configurable number of students
- Sequential execution for stability

### `student_ppt_viewer.py`
- Complete Selenium automation for single student
- Loads random student from credentials CSV
- Follows full workflow from login to AI interaction
- Designed for parallel execution

### `test_config.properties`
- Single source of truth for all settings
- API endpoints and credentials
- Selenium element locators
- Business keywords for aspirations
- Execution timeouts

## 🚀 Running at Scale

To run for multiple students simultaneously:

1. **Create sufficient students first**:
   ```bash
   # Update TOTAL_STUDENTS in test_config.properties
   python3 create_students.py
   ```

2. **Run students in parallel** (server deployment):
   - Deploy scripts to server
   - Use process managers or containers
   - Monitor resource usage

## 📋 Prerequisites

- Python 3.7+
- Chrome browser + ChromeDriver (managed by webdriver-manager)
- Network access to AI Tutor API and portal
- Valid API credentials in config

## 🔍 Troubleshooting

### Common Issues

1. **XPath Changes**: Update selectors in `test_config.properties`
2. **Timeout Issues**: Increase `EXECUTION_TIMEOUT` for slower environments
3. **Student Creation Fails**: Check API credentials and network connectivity
4. **PPT Loading**: Fluent wait handles slow PPT generation (up to 10 minutes)

### Logs
- Chrome browser logs for debugging Selenium issues
- Python console output for execution status
- Results saved in `results/` directory

## 🔄 Next Steps

Ready for server deployment with provided configurations to run 100 concurrent students. 