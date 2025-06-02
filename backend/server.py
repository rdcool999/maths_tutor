from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import os
from dotenv import load_dotenv
import json
import re

load_dotenv()

app = FastAPI()

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class MathQuestionRequest(BaseModel):
    year_level: int  # 1-6
    difficulty: str  # "easy", "medium", "hard"
    question_type: str  # "multiple_choice", "numerical", "comparison", "problem_solving"
    topic: str  # "arithmetic", "algebra", "geometry"
    num_questions: int = 20

@app.get("/")
def read_root():
    return {"message": "Math Question Generator API"}

@app.post("/api/generate-math-questions")
async def generate_math_questions(request: MathQuestionRequest):
    try:
        # Construct prompt based on requirements
        prompt = create_math_prompt(request)
        
        # Call DeepSeek API
        response = await call_deepseek_api(prompt)
        
        # Parse and format questions
        questions = parse_questions_response(response, request.question_type)
        
        return {"questions": questions, "count": len(questions)}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating questions: {str(e)}")

def create_math_prompt(request: MathQuestionRequest):
    """Create age-appropriate math question prompt"""
    
    difficulty_map = {
        "easy": "basic",
        "medium": "intermediate", 
        "hard": "challenging"
    }
    
    year_context = {
        1: "Year 1 (ages 5-6): Basic counting 1-20, simple addition/subtraction up to 10, basic shapes",
        2: "Year 2 (ages 6-7): Addition/subtraction up to 100, basic multiplication by 2,5,10, simple fractions",
        3: "Year 3 (ages 7-8): Multiplication tables 2-10, division, simple fractions, basic measurement",
        4: "Year 4 (ages 8-9): Larger numbers up to 10,000, decimals, basic geometry, area and perimeter",
        5: "Year 5 (ages 9-10): Advanced fractions, percentages, negative numbers, coordinate geometry",
        6: "Year 6 (ages 10-11): Algebra basics, ratios, complex geometry, basic statistics, problem solving"
    }
    
    topic_guidelines = {
        "arithmetic": "Focus on numbers, calculations, operations",
        "algebra": "Focus on patterns, equations, variables (age-appropriate)",
        "geometry": "Focus on shapes, angles, measurements, spatial reasoning"
    }
    
    if request.question_type == "multiple_choice":
        format_instruction = """
        Format EXACTLY as follows for each question:
        
        Q: [clear question text]
        A) [option 1]
        B) [option 2] 
        C) [option 3]
        D) [option 4]
        Answer: [A/B/C/D]
        Explanation: [brief explanation]
        
        ---
        """
    elif request.question_type == "numerical":
        format_instruction = """
        Format EXACTLY as follows for each question:
        
        Q: [question text requiring numerical answer]
        Answer: [numerical answer only]
        Explanation: [step-by-step solution]
        
        ---
        """
    else:
        format_instruction = """
        Format EXACTLY as follows for each question:
        
        Q: [question text]
        Answer: [answer]
        Explanation: [explanation]
        
        ---
        """
    
    prompt = f"""
    You are an expert math teacher. Generate exactly {request.num_questions} {difficulty_map[request.difficulty]} {request.topic} math questions 
    appropriate for {year_context[request.year_level]}.
    
    Topic focus: {topic_guidelines[request.topic]}
    Question type: {request.question_type}
    
    IMPORTANT REQUIREMENTS:
    - Use age-appropriate language and concepts
    - Make questions clear and unambiguous
    - Ensure all answers are correct
    - Vary question contexts (real-world scenarios)
    - Make questions engaging for children
    
    {format_instruction}
    
    Generate exactly {request.num_questions} questions following this format precisely.
    """
    
    return prompt

async def call_deepseek_api(prompt: str):
    """Call DeepSeek API with the generated prompt"""
    
    api_key = os.getenv("DEEPSEEK_API_KEY", "sk-9f803aa2095446219417669acb14f5a2")
    
    url = "https://api.deepseek.com/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {
                "role": "system", 
                "content": "You are an expert elementary math teacher creating educational questions for students. Always follow the exact format requested."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.7,
        "max_tokens": 3000
    }
    
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code, 
            detail=f"DeepSeek API error: {response.text}"
        )
    
    return response.json()

def parse_questions_response(response, question_type):
    """Parse DeepSeek response into structured questions"""
    
    content = response["choices"][0]["message"]["content"]
    questions = []
    
    # Split by separator
    question_blocks = content.split("---")
    
    for block in question_blocks:
        if not block.strip():
            continue
            
        try:
            question_data = parse_single_question(block.strip(), question_type)
            if question_data:
                questions.append(question_data)
        except Exception as e:
            print(f"Error parsing question block: {e}")
            continue
    
    return questions

def parse_single_question(block: str, question_type: str):
    """Parse a single question block"""
    
    lines = [line.strip() for line in block.split('\n') if line.strip()]
    
    question_text = ""
    options = []
    correct_answer = ""
    explanation = ""
    
    for line in lines:
        if line.startswith("Q:"):
            question_text = line.replace("Q:", "").strip()
        elif question_type == "multiple_choice" and re.match(r'^[A-D]\)', line):
            options.append(line)
        elif line.startswith("Answer:"):
            correct_answer = line.replace("Answer:", "").strip()
        elif line.startswith("Explanation:"):
            explanation = line.replace("Explanation:", "").strip()
    
    if question_text and correct_answer:
        return {
            "question": question_text,
            "options": options if question_type == "multiple_choice" else None,
            "correct_answer": correct_answer,
            "explanation": explanation,
            "question_type": question_type
        }
    
    return None

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)