from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from groq import Groq
import os
from dotenv import load_dotenv
import json
import re
from typing import List, Optional

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

# Initialize Groq client
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY", "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"))

class MathQuestionRequest(BaseModel):
    year_level: int  # 1-6
    difficulty: str  # "easy", "medium", "hard"
    question_type: str  # "multiple_choice", "numerical", "comparison", "problem_solving"
    topic: str  # "arithmetic", "algebra", "geometry"
    num_questions: int = 20

@app.get("/")
def read_root():
    return {"message": "Math Question Generator API with Groq"}

@app.post("/api/generate-math-questions")
async def generate_math_questions(request: MathQuestionRequest):
    try:
        # Generate questions using Groq
        questions = await generate_questions_with_groq(request)
        
        return {"questions": questions, "count": len(questions)}
        
    except Exception as e:
        print(f"Error generating questions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating questions: {str(e)}")

async def generate_questions_with_groq(request: MathQuestionRequest):
    """Generate math questions using Groq API"""
    
    # Define age-appropriate topics for each year level
    topics_by_year = {
        1: "Basic counting 1-20, simple addition/subtraction up to 10, basic shapes (circle, square, triangle)",
        2: "Addition/subtraction up to 100, basic multiplication by 2,5,10, simple fractions (halves, quarters)",
        3: "Multiplication tables 2-12, division, simple fractions, basic measurement (cm, m), time",
        4: "Larger numbers up to 10,000, decimals (tenths, hundredths), area and perimeter, data interpretation",
        5: "Advanced fractions, percentages, negative numbers, coordinate geometry, basic statistics",
        6: "Ratios, algebra basics (simple equations), complex geometry, probability, problem solving"
    }
    
    year_topics = topics_by_year.get(request.year_level, topics_by_year[3])
    
    # Create specific prompt based on question type
    if request.question_type == "multiple_choice":
        prompt = f"""You are a math teacher creating {request.num_questions} multiple choice questions for Year {request.year_level} students (ages {request.year_level + 4}-{request.year_level + 5}).

DIFFICULTY: {request.difficulty}
TOPIC FOCUS: {request.topic}
CURRICULUM: {year_topics}

Create exactly {request.num_questions} questions. Each question MUST follow this EXACT format:

Q: [Clear question text]
A) [option 1]
B) [option 2]
C) [option 3]
D) [option 4]
Answer: [A/B/C/D]
Explanation: [Brief explanation]

---

REQUIREMENTS:
- Use age-appropriate language and real-world contexts
- Make questions clear and unambiguous
- Ensure all math is correct
- Mix different problem types within the topic
- Make questions engaging for children

Generate exactly {request.num_questions} questions now:"""

    elif request.question_type == "numerical":
        prompt = f"""You are a math teacher creating {request.num_questions} numerical answer questions for Year {request.year_level} students (ages {request.year_level + 4}-{request.year_level + 5}).

DIFFICULTY: {request.difficulty}
TOPIC FOCUS: {request.topic}
CURRICULUM: {year_topics}

Create exactly {request.num_questions} questions. Each question MUST follow this EXACT format:

Q: [Question requiring numerical answer]
Answer: [Numerical answer only]
Explanation: [Step-by-step solution]

---

REQUIREMENTS:
- Questions should have clear numerical answers
- Use age-appropriate contexts (toys, sweets, animals, etc.)
- Show working steps in explanations
- Mix different calculation types

Generate exactly {request.num_questions} questions now:"""

    elif request.question_type == "comparison":
        prompt = f"""You are a math teacher creating {request.num_questions} quantitative comparison questions for Year {request.year_level} students (ages {request.year_level + 4}-{request.year_level + 5}).

DIFFICULTY: {request.difficulty}
TOPIC FOCUS: {request.topic}
CURRICULUM: {year_topics}

Create exactly {request.num_questions} questions. Each question MUST follow this EXACT format:

Q: Compare Quantity A and Quantity B. Which is greater?
Quantity A: [value/expression]
Quantity B: [value/expression]
A) Quantity A is greater
B) Quantity B is greater
C) They are equal
D) Cannot be determined
Answer: [A/B/C/D]
Explanation: [Brief explanation]

---

Generate exactly {request.num_questions} questions now:"""

    else:  # problem_solving
        prompt = f"""You are a math teacher creating {request.num_questions} word problem questions for Year {request.year_level} students (ages {request.year_level + 4}-{request.year_level + 5}).

DIFFICULTY: {request.difficulty}
TOPIC FOCUS: {request.topic}
CURRICULUM: {year_topics}

Create exactly {request.num_questions} questions. Each question MUST follow this EXACT format:

Q: [Real-world word problem]
Answer: [Answer with units if needed]
Explanation: [Step-by-step solution]

---

REQUIREMENTS:
- Use engaging real-world scenarios (school, home, playground, shopping)
- Include appropriate units where needed
- Make problems relatable to children
- Show clear solution steps

Generate exactly {request.num_questions} questions now:"""

    try:
        # Call Groq API
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert elementary school math teacher. Always follow the exact format requested. Generate accurate, age-appropriate questions."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model="llama3-8b-8192",  # Fast and free model
            temperature=0.7,
            max_tokens=4000
        )
        
        # Parse the response
        content = chat_completion.choices[0].message.content
        questions = parse_groq_response(content, request.question_type)
        
        return questions
        
    except Exception as e:
        print(f"Groq API error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate questions: {str(e)}")

def parse_groq_response(content: str, question_type: str):
    """Parse Groq response into structured questions"""
    
    questions = []
    
    # Split by separator
    question_blocks = content.split("---")
    
    for block in question_blocks:
        if not block.strip():
            continue
            
        try:
            question_data = parse_single_question_block(block.strip(), question_type)
            if question_data:
                questions.append(question_data)
        except Exception as e:
            print(f"Error parsing question block: {e}")
            continue
    
    return questions

def parse_single_question_block(block: str, question_type: str):
    """Parse a single question block"""
    
    lines = [line.strip() for line in block.split('\n') if line.strip()]
    
    question_text = ""
    options = []
    correct_answer = ""
    explanation = ""
    quantity_a = ""
    quantity_b = ""
    
    for line in lines:
        if line.startswith("Q:"):
            question_text = line.replace("Q:", "").strip()
        elif question_type == "multiple_choice" and re.match(r'^[A-D]\)', line):
            options.append(line.strip())
        elif question_type == "comparison" and line.startswith("Quantity A:"):
            quantity_a = line.replace("Quantity A:", "").strip()
        elif question_type == "comparison" and line.startswith("Quantity B:"):
            quantity_b = line.replace("Quantity B:", "").strip()
        elif line.startswith("Answer:"):
            correct_answer = line.replace("Answer:", "").strip()
        elif line.startswith("Explanation:"):
            explanation = line.replace("Explanation:", "").strip()
    
    # Handle comparison questions specially
    if question_type == "comparison" and quantity_a and quantity_b:
        question_text = f"Compare Quantity A and Quantity B.\nQuantity A: {quantity_a}\nQuantity B: {quantity_b}"
        options = [
            "A) Quantity A is greater",
            "B) Quantity B is greater", 
            "C) They are equal",
            "D) Cannot be determined"
        ]
    
    if question_text and correct_answer:
        return {
            "question": question_text,
            "options": options if options else None,
            "correct_answer": correct_answer,
            "explanation": explanation,
            "question_type": question_type
        }
    
    return None

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)