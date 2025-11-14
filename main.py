import os
from typing import List, Optional, Literal, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI()

# CORS: allow requests from any domain (no credentials)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----- Models -----
Subject = Literal[
    "Math",
    "Science",
    "English",
    "Social Studies",
    "Languages",
    "Computer",
]

class AssistRequest(BaseModel):
    student_class: int = Field(..., ge=1, le=10, description="Class/Grade from 1 to 10")
    subject: Subject
    question: str = Field(..., min_length=3)
    language: Optional[str] = Field(default="English", description="Response language hint")
    needs: Optional[List[Literal[
        "explanation",
        "steps",
        "examples",
        "practice",
        "summary",
        "tips",
        "fun_facts",
        "related",
        "visuals",
        "revision",
        "quiz"
    ]]] = Field(default=None)

class Section(BaseModel):
    title: str
    content: Any

class AssistResponse(BaseModel):
    level: int
    subject: Subject
    topic: str
    sections: List[Section]
    safety_note: Optional[str] = None
    follow_up: Optional[str] = None

# ----- Utility: Simple safety and clarity checks -----
HARMFUL_KEYWORDS = {
    "self-harm", "suicide", "violence", "bomb", "weapon", "drugs", "extremism"
}

def is_harmful(text: str) -> bool:
    t = text.lower()
    return any(k in t for k in HARMFUL_KEYWORDS)

# Age-adjusted helpers

def level_tone(level: int) -> Dict[str, Any]:
    if level <= 2:
        return {
            "voice": "very simple, friendly",
            "sent_len": 8,
            "bullets": True
        }
    if level <= 5:
        return {
            "voice": "simple and clear",
            "sent_len": 12,
            "bullets": True
        }
    if level <= 8:
        return {
            "voice": "clear with a bit more detail",
            "sent_len": 16,
            "bullets": True
        }
    return {
        "voice": "concise, structured, and exam-oriented",
        "sent_len": 18,
        "bullets": True
    }

# Content generators (rule-based, no external calls)

def explain_math(level: int, question: str) -> Dict[str, List[str]]:
    q = question.strip()
    steps = []
    examples = []
    tips = []
    practice = []

    # Very lightweight heuristics
    if any(k in q.lower() for k in ["add", "sum", "+", "plus"]):
        steps = [
            "Line up the numbers by place value.",
            "Add digits from right to left.",
            "If a sum is 10 or more, carry to the next place.",
            "Write the final answer neatly."
        ]
        examples = ["23 + 19 = 42", "305 + 70 = 375"]
        practice = ["47 + 28 = ?", "506 + 289 = ?"]
        tips = ["Check by reversing the addends.", "Estimate first to see if your answer is reasonable."]
    elif any(k in q.lower() for k in ["subtrac", "-", "minus", "difference"]):
        steps = [
            "Line up the numbers by place value.",
            "Subtract from right to left.",
            "If the top digit is smaller, borrow from the next left place.",
            "Write the difference."
        ]
        examples = ["54 - 27 = 27", "700 - 256 = 444"]
        practice = ["63 - 38 = ?", "900 - 457 = ?"]
        tips = ["Add the answer to the smaller number to check."]
    elif any(k in q.lower() for k in ["fraction", "/", "numerator", "denominator"]):
        steps = [
            "Make denominators the same if you add or subtract.",
            "Multiply across for multiplication.",
            "Flip the second fraction and multiply for division.",
            "Simplify by dividing numerator and denominator by the same number."
        ]
        examples = ["1/2 + 1/3 = 5/6", "3/4 × 2/3 = 1/2"]
        practice = ["2/5 + 1/10 = ?", "5/6 ÷ 2/3 = ?"]
        tips = ["Always simplify your final fraction."]
    elif any(k in q.lower() for k in ["algebra", "solve", "equation", "x=", "find x"]):
        steps = [
            "Keep the equation balanced: do the same to both sides.",
            "Move constants to one side and variables to the other.",
            "Combine like terms.",
            "Isolate the variable to find its value."
        ]
        examples = ["2x + 5 = 13 → 2x = 8 → x = 4", "3(x-2) = 9 → x-2 = 3 → x = 5"]
        practice = ["5x - 7 = 18", "4(x + 3) = 28"]
        tips = ["Check by substituting your value back into the equation."]
    else:
        steps = [
            "Identify what is being asked.",
            "Write down the known information.",
            "Choose a suitable method or formula.",
            "Solve step by step and check your answer."
        ]
        examples = ["Area of rectangle: A = l × w", "Mean = sum of data ÷ number of items"]
        practice = ["Find the perimeter of a 6 cm by 9 cm rectangle.", "Calculate the mean of 5, 7, 3, 10."]
        tips = ["Underline key numbers and units."]

    summary = ["Solve carefully, show steps, and double-check."]
    fun = ["Zero is the only number that is neither positive nor negative."]
    related = ["Place value", "Word problems", "Estimation"]

    visuals = [
        "Picture: Number line showing jumps for addition/subtraction.",
        "Diagram: Balance scale to show equation solving."
    ]
    revision = [
        "Revise place value and basic operations.",
        "Memorize common fraction equivalents (1/2=0.5, 1/4=0.25)."
    ]
    quiz = [
        "Quick Quiz: 12 + 19 = ?",
        "True/False: To divide fractions, flip the second and multiply.",
    ]

    return {
        "steps": steps,
        "examples": examples,
        "practice": practice,
        "tips": tips,
        "summary": summary,
        "fun_facts": fun,
        "related": related,
        "visuals": visuals,
        "revision": revision,
        "quiz": quiz,
    }


def explain_science(level: int, question: str) -> Dict[str, List[str]]:
    q = question.lower()
    if "photosynthesis" in q:
        base = {
            "steps": [
                "Plants take in sunlight with chlorophyll in leaves.",
                "They use water from roots and carbon dioxide from air.",
                "They make glucose (food) and release oxygen."
            ],
            "examples": ["Leaf in sunlight makes more oxygen than in shade."],
            "practice": ["Name two things plants need for photosynthesis.", "Why is sunlight important?"],
            "tips": ["Remember: Sun + CO2 + Water → Glucose + Oxygen"],
            "summary": ["Photosynthesis is how plants make food using sunlight."],
            "fun_facts": ["Chloroplasts are the tiny food factories in plant cells."],
            "related": ["Food chains", "Respiration", "Plant cells"],
        }
    else:
        base = {
            "steps": ["Observe, ask a question, make a hypothesis, test, and conclude."],
            "examples": ["Testing which paper towel absorbs more water."],
            "practice": ["Write a simple hypothesis about melting ice."],
            "tips": ["Change only one variable at a time."],
            "summary": ["Science uses fair tests to learn about the world."],
            "fun_facts": ["Honey never spoils because it has very little water."],
            "related": ["Variables", "Fair test", "Data tables"],
        }

    base.update({
        "visuals": [
            "Diagram: Sun → Leaf → Sugar + Oxygen arrows.",
            "Chart: Variables vs outcomes in an experiment."
        ],
        "revision": [
            "Recall: solid, liquid, gas changes.",
            "Know the steps of the scientific method."
        ],
        "quiz": [
            "MCQ: Plants take in (a) oxygen (b) carbon dioxide during photosynthesis.",
            "Fill in the blank: Energy for photosynthesis comes from _____."
        ]
    })
    return base


def explain_english(level: int, question: str) -> Dict[str, List[str]]:
    q = question.lower()
    if any(k in q for k in ["noun", "verb", "adjective", "adverb"]):
        base = {
            "steps": ["Find the word's job in the sentence."],
            "examples": ["Noun: dog; Verb: runs; Adjective: happy; Adverb: quickly."],
            "practice": ["Underline the verbs in: The cat quietly slept."],
            "tips": ["Adjectives describe nouns; adverbs describe verbs/adjectives."],
            "summary": ["Parts of speech tell how words work."],
            "fun_facts": ["English borrows words from many languages!"],
            "related": ["Sentence types", "Punctuation"],
        }
    else:
        base = {
            "steps": ["Read closely, find main idea, then details."],
            "examples": ["Main idea: what the text is mostly about."],
            "practice": ["Write a 2-sentence summary of a short paragraph."],
            "tips": ["Use transition words: first, then, finally."],
            "summary": ["Clarity and structure make writing strong."],
            "fun_facts": ["There are more than a million English words."],
            "related": ["Synonyms", "Paragraphs", "Summaries"],
        }

    base.update({
        "visuals": [
            "Mind map: Topic in center with branches for main idea and details.",
            "Color-coded sentence showing noun/verb/adjective/adverb."
        ],
        "revision": [
            "Revise punctuation basics: . , ? !",
            "Know the difference between there/they're/their."
        ],
        "quiz": [
            "Identify the adjective: The small puppy barked loudly.",
            "Choose a transition to add: First/Then/Finally."
        ]
    })
    return base


def explain_social(level: int, question: str) -> Dict[str, List[str]]:
    q = question.lower()
    if any(k in q for k in ["democracy", "government"]):
        base = {
            "steps": ["People choose leaders, leaders make and enforce rules."],
            "examples": ["Voting in local elections."],
            "practice": ["Name two features of a democracy."],
            "tips": ["Remember: rights and responsibilities go together."],
            "summary": ["Democracy means rule by the people."],
            "fun_facts": ["Ancient Athens had an early form of democracy."],
            "related": ["Constitution", "Citizenship"],
        }
    else:
        base = {
            "steps": ["Identify time, place, people, and causes/effects."],
            "examples": ["Cause and effect in historical events."],
            "practice": ["Make a timeline of three key events from a chapter."],
            "tips": ["Use maps and dates to organize information."],
            "summary": ["Social studies connects people, places, and time."],
            "fun_facts": ["The Silk Road was a network, not one road."],
            "related": ["Timelines", "Maps", "Civics"],
        }

    base.update({
        "visuals": [
            "Timeline sketch with dates and short notes.",
            "Map outline highlighting key regions."
        ],
        "revision": [
            "Remember key terms: democracy, constitution, citizen.",
            "Practice reading maps and legends."
        ],
        "quiz": [
            "Short answer: What is one feature of a democracy?",
            "Match: Event → Year (from your chapter)."
        ]
    })
    return base


def explain_languages(level: int, question: str) -> Dict[str, List[str]]:
    base = {
        "steps": ["Learn basic greetings, numbers, and simple grammar."],
        "examples": ["Hola (Hello) in Spanish; Namaste in Hindi."],
        "practice": ["Translate five classroom objects into the target language."],
        "tips": ["Practice a little every day and speak out loud."],
        "summary": ["Start small and build vocabulary steadily."],
        "fun_facts": ["Many languages share common roots called cognates."],
        "related": ["Pronunciation", "Vocabulary", "Grammar"],
    }
    base.update({
        "visuals": ["Flashcards with picture on one side and word on the other."],
        "revision": ["Revise 10 core words daily and one grammar rule."],
        "quiz": ["Say or write 3 greetings and 3 numbers in the language."]
    })
    return base


def explain_computer(level: int, question: str) -> Dict[str, List[str]]:
    q = question.lower()
    if any(k in q for k in ["algorithm", "flowchart"]):
        base = {
            "steps": [
                "Define the problem clearly.",
                "List steps in order (algorithm).",
                "Draw a flowchart with start/end, input/output, and process boxes.",
                "Test the steps with a simple example."
            ],
            "examples": [
                "Algorithm: Make tea → Boil water → Add tea → Pour → Add milk/sugar.",
                "Flowchart: Start → Read two numbers → Add → Show sum → End"
            ],
            "practice": ["Write an algorithm for brushing teeth.", "Draw a flowchart for adding two numbers."],
            "tips": ["Use clear, short steps; one action per step."],
            "summary": ["Algorithms are ordered steps; flowcharts show them visually."],
            "fun_facts": ["The word 'algorithm' comes from Al-Khwarizmi, a Persian scholar."],
            "related": ["Pseudocode", "Debugging", "Programming basics"],
        }
    else:
        base = {
            "steps": ["Input → Process → Output → Storage (IPO cycle)."],
            "examples": ["Typing (input), Word processor (process), Printed page (output)."],
            "practice": ["List 2 input and 2 output devices."],
            "tips": ["Keep files organized with clear names and folders."],
            "summary": ["Computers take input, process it, and give output; they can store data."],
            "fun_facts": ["Early computers filled whole rooms!"],
            "related": ["Hardware", "Software", "Networks"],
        }
    base.update({
        "visuals": ["Block diagram: Input → CPU → Output, with Storage connected."],
        "revision": ["Revise basic parts: CPU, memory, storage, input/output devices."],
        "quiz": ["MCQ: CPU stands for _____.", "Name one input and one output device."]
    })
    return base


def generate_content(level: int, subject: Subject, question: str) -> Dict[str, List[str]]:
    if subject == "Math":
        return explain_math(level, question)
    if subject == "Science":
        return explain_science(level, question)
    if subject == "English":
        return explain_english(level, question)
    if subject == "Social Studies":
        return explain_social(level, question)
    if subject == "Computer":
        return explain_computer(level, question)
    return explain_languages(level, question)

# ----- Routes -----
@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI Backend!"}

@app.get("/api/hello")
def hello():
    return {"message": "Hello from the backend API!"}

@app.post("/api/assist", response_model=AssistResponse)
def assist(req: AssistRequest):
    # Safety filtering
    if is_harmful(req.question):
        return AssistResponse(
            level=req.student_class,
            subject=req.subject,
            topic="Safety Guard",
            sections=[Section(title="Notice", content=[
                "I can't help with harmful or inappropriate content.",
                "Please ask about your school subjects like Math, Science, English, Social Studies, Languages, or Computer."
            ])],
            safety_note="Content filtered for safety."
        )

    # Generate structured content
    content = generate_content(req.student_class, req.subject, req.question)

    # Pick sections according to req.needs or include all
    order = [
        "explanation", "steps", "examples", "practice", "summary", "tips", "fun_facts", "related",
        "visuals", "revision", "quiz"
    ]
    include = set(req.needs) if req.needs else set(order)

    sections: List[Section] = []

    # A brief age-adjusted explanation headline
    tone = level_tone(req.student_class)
    intro = [
        f"Let's learn about: {req.question.strip()}.",
        "I'll keep it " + tone["voice"] + ".",
        "You'll get steps, examples, practice, visuals, a short quiz, and revision notes."
    ]
    if "explanation" in include:
        sections.append(Section(title="Explanation", content=intro))

    # Add the rest from generated content
    mapping = {
        "steps": "Step-by-step",
        "examples": "Examples",
        "practice": "Practice Questions",
        "summary": "Quick Summary",
        "tips": "Helpful Tips",
        "fun_facts": "Fun Facts",
        "related": "Related Topics",
        "visuals": "Visual Description",
        "revision": "Revision Notes",
        "quiz": "Interactive Quiz",
    }
    for key, title in mapping.items():
        if key in include and key in content:
            sections.append(Section(title=title, content=content[key]))

    follow_up = "If this isn't quite your topic, tell me your class (1-10) and the exact chapter or exercise number."

    return AssistResponse(
        level=req.student_class,
        subject=req.subject,
        topic=req.question.strip(),
        sections=sections,
        follow_up=follow_up,
    )

@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    
    try:
        # Try to import database module
        from database import db
        
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            
            # Try to list collections to verify connectivity
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]  # Show first 10 collections
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
            
    except ImportError:
        response["database"] = "❌ Database module not found (run enable-database first)"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    
    # Check environment variables
    import os
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    
    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
