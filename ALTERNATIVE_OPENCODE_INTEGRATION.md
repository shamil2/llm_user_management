# Alternative OpenCode Integration Methods

## Method 1: Direct API Configuration
If /connect is not available, try these alternatives:

### Option A: Environment Variables
export OPENAI_API_KEY='your-api-key-here'
export OPENAI_BASE_URL='http://localhost:8000/v1'

### Option B: Configuration File
Create or edit opencode.json:
{
  "models": {
    "llm-user-managed/opencode-llm": {
      "apiKey": "your-api-key-here",
      "baseURL": "http://localhost:8000/v1"
    }
  }
}

### Option C: Direct Model Usage
Use the model directly with full identifier:
llm-user-managed/opencode-llm

## Method 2: Check Available Commands
Run these commands in OpenCode to see what's available:
/help
/commands  
/models
/providers

## Method 3: Provider Registration
Some versions of OpenCode require explicit provider registration:
/register-provider llm-user-managed http://localhost:8000/v1
/set-api-key llm-user-managed your-api-key-here

## Method 4: Manual Configuration
Edit OpenCode's config file directly (usually ~/.opencode/config.json):
{
  "providers": {
    "llm-user-managed": {
      "baseURL": "http://localhost:8000/v1",
      "apiKey": "your-api-key-here"
    }
  },
  "models": {
    "opencode-llm": "llm-user-managed"
  }
}
