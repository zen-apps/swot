import os
from datetime import datetime
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
import pandas as pd
from pathlib import Path

# Load environment variables
load_dotenv(override=True)
openai_api_key = os.getenv('OPENAI_API_KEY')
MODEL = "gpt-4o-mini"
llm = ChatOpenAI(model=MODEL, api_key=openai_api_key)

# Create FastAPI app
app = FastAPI()

# Ensure data directory exists
DATA_DIR = Path("swot_data")
DATA_DIR.mkdir(exist_ok=True)
CSV_FILE = DATA_DIR / "swot_responses.csv"


@app.get("/", response_class=HTMLResponse)
async def get_form():
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>SWOT Analysis Questionnaire</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }
            h1 { color: #333; }
            h2 { color: #666; margin-top: 30px; }
            label { font-weight: bold; color: #555; }
            input[type="text"], textarea {
                width: 100%;
                padding: 10px;
                margin: 5px 0 15px 0;
                border: 1px solid #ddd;
                border-radius: 4px;
                box-sizing: border-box;
            }
            input[type="submit"] {
                background-color: #4CAF50;
                color: white;
                padding: 14px 20px;
                margin: 20px 0;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                font-size: 16px;
            }
            input[type="submit"]:hover { background-color: #45a049; }
            .form-container {
                background-color: white;
                padding: 30px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            hr { border: none; border-top: 2px solid #eee; margin: 30px 0; }
            #status { margin: 20px 0; padding: 10px; border-radius: 4px; display: none; }
            .loading { background-color: #fff3cd; color: #856404; display: block !important; }
            .error { background-color: #f8d7da; color: #721c24; display: block !important; }
        </style>
        <script>
            function handleSubmit(event) {
                event.preventDefault();
                const form = event.target;
                const status = document.getElementById('status');
                const submitBtn = form.querySelector('input[type="submit"]');

                status.className = 'loading';
                status.textContent = 'Analyzing SWOT data with AI... This may take 30-60 seconds.';
                submitBtn.disabled = true;
                submitBtn.value = 'Analyzing...';

                const formData = new FormData(form);

                fetch('/analyze', {
                    method: 'POST',
                    body: formData
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.text();
                })
                .then(html => {
                    document.open();
                    document.write(html);
                    document.close();
                })
                .catch(error => {
                    status.className = 'error';
                    status.textContent = 'Error: ' + error.message + '. Please check console for details.';
                    submitBtn.disabled = false;
                    submitBtn.value = 'Analyze SWOT';
                    console.error('Error:', error);
                });
            }
        </script>
    </head>
    <body>
        <div class="form-container">
            <h1>Strategic Pipeline SWOT Questionnaire</h1>

            <div id="status"></div>

            <form action="/analyze" method="post" onsubmit="handleSubmit(event)">
                <h2>Company Information</h2>
                <label>Company Name:</label><br>
                <input type="text" name="company_name" required><br>
                
                <label>Desired Outcomes / KPIs:</label><br>
                <textarea name="desired_outcomes" rows="3" required placeholder="e.g., 30% revenue growth in clinical marketplace"></textarea><br>
                
                <hr>
                
                <h2>Strengths</h2>
                <p>Provide 4-5 inputs (about 50 words each) describing your organization's strengths:</p>
                <label>Strength 1:</label><br>
                <textarea name="strength_1" rows="3" required></textarea><br>
                
                <label>Strength 2:</label><br>
                <textarea name="strength_2" rows="3" required></textarea><br>
                
                <label>Strength 3:</label><br>
                <textarea name="strength_3" rows="3" required></textarea><br>
                
                <label>Strength 4:</label><br>
                <textarea name="strength_4" rows="3" required></textarea><br>
                
                <label>Strength 5 (optional):</label><br>
                <textarea name="strength_5" rows="3"></textarea><br>
                
                <hr>
                
                <h2>Weaknesses</h2>
                <p>Provide 4-5 inputs (about 50 words each) describing your organization's weaknesses:</p>
                <label>Weakness 1:</label><br>
                <textarea name="weakness_1" rows="3" required></textarea><br>
                
                <label>Weakness 2:</label><br>
                <textarea name="weakness_2" rows="3" required></textarea><br>
                
                <label>Weakness 3:</label><br>
                <textarea name="weakness_3" rows="3" required></textarea><br>
                
                <label>Weakness 4:</label><br>
                <textarea name="weakness_4" rows="3" required></textarea><br>
                
                <label>Weakness 5 (optional):</label><br>
                <textarea name="weakness_5" rows="3"></textarea><br>
                
                <hr>
                
                <h2>Opportunities</h2>
                <p>Provide 4-5 inputs (about 50 words each) describing opportunities:</p>
                <label>Opportunity 1:</label><br>
                <textarea name="opportunity_1" rows="3" required></textarea><br>
                
                <label>Opportunity 2:</label><br>
                <textarea name="opportunity_2" rows="3" required></textarea><br>
                
                <label>Opportunity 3:</label><br>
                <textarea name="opportunity_3" rows="3" required></textarea><br>
                
                <label>Opportunity 4:</label><br>
                <textarea name="opportunity_4" rows="3" required></textarea><br>
                
                <label>Opportunity 5 (optional):</label><br>
                <textarea name="opportunity_5" rows="3"></textarea><br>
                
                <hr>
                
                <h2>Threats</h2>
                <p>Provide 4-5 inputs (about 50 words each) describing threats:</p>
                <label>Threat 1:</label><br>
                <textarea name="threat_1" rows="3" required></textarea><br>
                
                <label>Threat 2:</label><br>
                <textarea name="threat_2" rows="3" required></textarea><br>
                
                <label>Threat 3:</label><br>
                <textarea name="threat_3" rows="3" required></textarea><br>
                
                <label>Threat 4:</label><br>
                <textarea name="threat_4" rows="3" required></textarea><br>
                
                <label>Threat 5 (optional):</label><br>
                <textarea name="threat_5" rows="3"></textarea><br>
                
                <hr>
                
                <input type="submit" value="Analyze SWOT">
            </form>
        </div>
    </body>
    </html>
    """
    return html_content


@app.post("/analyze", response_class=HTMLResponse)
async def analyze_swot(
    company_name: str = Form(...),
    desired_outcomes: str = Form(...),
    strength_1: str = Form(...),
    strength_2: str = Form(...),
    strength_3: str = Form(...),
    strength_4: str = Form(...),
    strength_5: str = Form(""),
    weakness_1: str = Form(...),
    weakness_2: str = Form(...),
    weakness_3: str = Form(...),
    weakness_4: str = Form(...),
    weakness_5: str = Form(""),
    opportunity_1: str = Form(...),
    opportunity_2: str = Form(...),
    opportunity_3: str = Form(...),
    opportunity_4: str = Form(...),
    opportunity_5: str = Form(""),
    threat_1: str = Form(...),
    threat_2: str = Form(...),
    threat_3: str = Form(...),
    threat_4: str = Form(...),
    threat_5: str = Form("")
):
    # Collect all inputs
    strengths = [s for s in [strength_1, strength_2, strength_3, strength_4, strength_5] if s]
    weaknesses = [w for w in [weakness_1, weakness_2, weakness_3, weakness_4, weakness_5] if w]
    opportunities = [o for o in [opportunity_1, opportunity_2, opportunity_3, opportunity_4, opportunity_5] if o]
    threats = [t for t in [threat_1, threat_2, threat_3, threat_4, threat_5] if t]
    
    # Save raw data to CSV
    save_to_csv(company_name, desired_outcomes, strengths, weaknesses, opportunities, threats)
    
    # Generate LLM analysis for each category
    strength_analysis = await generate_swot_category(
        "Strengths", company_name, desired_outcomes, strengths
    )
    
    weakness_analysis = await generate_swot_category(
        "Weaknesses", company_name, desired_outcomes, weaknesses
    )
    
    opportunity_analysis = await generate_swot_category(
        "Opportunities", company_name, desired_outcomes, opportunities
    )
    
    threat_analysis = await generate_swot_category(
        "Threats", company_name, desired_outcomes, threats
    )
    
    # Build results HTML
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>SWOT Analysis Results - {company_name}</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                max-width: 900px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }}
            h1 {{ color: #333; }}
            h2 {{
                color: #666;
                margin-top: 30px;
                padding-bottom: 10px;
                border-bottom: 2px solid #4CAF50;
            }}
            .results-container {{
                background-color: white;
                padding: 30px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            .analysis-section {{
                background-color: #f9f9f9;
                padding: 20px;
                border-radius: 4px;
                margin: 15px 0;
                white-space: pre-wrap;
                line-height: 1.6;
            }}
            hr {{ border: none; border-top: 2px solid #eee; margin: 30px 0; }}
            a {{
                display: inline-block;
                background-color: #4CAF50;
                color: white;
                padding: 10px 20px;
                text-decoration: none;
                border-radius: 4px;
                margin-top: 20px;
            }}
            a:hover {{ background-color: #45a049; }}
            .outcomes {{
                background-color: #e8f5e9;
                padding: 15px;
                border-radius: 4px;
                margin: 15px 0;
            }}
        </style>
    </head>
    <body>
        <div class="results-container">
            <h1>SWOT Analysis Results: {company_name}</h1>
            <h2>Desired Outcomes</h2>
            <div class="outcomes">{desired_outcomes}</div>
            
            <hr>
            
            <h2>Prioritized Strengths</h2>
            <div class="analysis-section">{strength_analysis}</div>
            
            <hr>
            
            <h2>Prioritized Weaknesses</h2>
            <div class="analysis-section">{weakness_analysis}</div>
            
            <hr>
            
            <h2>Prioritized Opportunities</h2>
            <div class="analysis-section">{opportunity_analysis}</div>
            
            <hr>
            
            <h2>Prioritized Threats</h2>
            <div class="analysis-section">{threat_analysis}</div>
            
            <hr>
            
            <p><a href="/">← Analyze Another Company</a></p>
        </div>
    </body>
    </html>
    """
    
    return html_content


async def generate_swot_category(category: str, company_name: str, desired_outcomes: str, inputs: list) -> str:
    """Generate LLM analysis for a SWOT category"""
    
    inputs_text = "\n".join([f"{i+1}. {inp}" for i, inp in enumerate(inputs)])
    
    prompt = f"""Create no more than 6 {category.lower()} statements of 60 words or less prioritized by their impact on {desired_outcomes} for a SWOT analysis of {company_name} based on the following inputs:

{inputs_text}

Provide your response as a numbered list (1-6) with each statement being 60 words or less. Prioritize by impact on the desired outcomes."""

    # Log the prompt being sent
    print(f"\n{'='*60}")
    print(f"LLM CALL - {category}")
    print(f"{'='*60}")
    print(f"PROMPT:\n{prompt}\n")
    
    response = llm.invoke([HumanMessage(content=prompt)])
    
    # Log the response received
    print(f"RESPONSE:\n{response.content}\n")
    print(f"{'='*60}\n")
    
    return response.content


def save_to_csv(company_name: str, desired_outcomes: str, strengths: list, weaknesses: list, opportunities: list, threats: list):
    """Save SWOT data to CSV"""
    
    data = {
        'timestamp': [datetime.now().isoformat()],
        'company_name': [company_name],
        'desired_outcomes': [desired_outcomes],
        'strengths': [' | '.join(strengths)],
        'weaknesses': [' | '.join(weaknesses)],
        'opportunities': [' | '.join(opportunities)],
        'threats': [' | '.join(threats)]
    }
    
    df = pd.DataFrame(data)
    
    # Append to CSV or create new one
    if CSV_FILE.exists():
        existing_df = pd.read_csv(CSV_FILE)
        combined_df = pd.concat([existing_df, df], ignore_index=True)
        combined_df.to_csv(CSV_FILE, index=False)
    else:
        df.to_csv(CSV_FILE, index=False)


if __name__ == "__main__":
    import uvicorn
    print("=" * 50)
    print("Starting SWOT Analysis FastAPI Server")
    print("=" * 50)
    print("\nServer will be available at:")
    print("  → http://localhost:8000")
    print("  → http://127.0.0.1:8000")
    print("\nPress CTRL+C to stop the server")
    print("=" * 50)
    print()
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")