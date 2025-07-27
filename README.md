## Running steps

1. Clone repo  
   ```
   git clone https://github.com/Ravi-chandera/finance_ai_agent.git
   ```

2. Create virtual environment  
   ```
   python -m venv venv
   ```

3. Activate virtual environment  
   ```
   venv\Scripts\activate
   ```

4. Enter into directory  
   ```
   cd finance_ai_agent
   ```

5. Add API key into `config.json`

6. Install dependencies  
   ```
   pip install -r requirements.txt
   ```

7. Run the following command  
   ```
   uvicorn main:app --reload
   ```
