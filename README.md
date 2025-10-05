# Navigate to your project directory
cd ~/swot

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install all dependencies
pip install fastapi uvicorn python-dotenv langchain-openai pandas python-multipart

# Create .env file (replace with your actual API key)
echo "OPENAI_API_KEY=sk-your-key-here" > .env

# Run the application
uvicorn main:app --reload