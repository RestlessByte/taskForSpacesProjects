from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer, util
from typing import List
from fastapi.responses import RedirectResponse

app = FastAPI()

# Инициализация модели Sentence Transformers
model = SentenceTransformer('all-MiniLM-L6-v2')

# Пример данных пользователей для мэтчинга
users = [
    {
        "name": "Bob",
        "skills": ["VR Design", "AI", "3D Modeling"],
        "interests": ["Art Collaboration", "Tech Innovation"]
    },
    {
        "name": "Sarah",
        "skills": ["UI/UX Design", "AI"],
        "interests": ["Tech Innovation", "Sustainability"]
    },
    {
        "name": "Alice",
        "skills": ["3D Modeling", "Animation"],
        "interests": ["Art Collaboration", "Digital Art"]
    }
]

# Предварительный расчет эмбеддингов для всех пользователей
user_texts = [' '.join(user['skills'] + user['interests']) for user in users]
user_embeddings = model.encode(user_texts)

class UserProfile(BaseModel):
    skills: List[str]
    interests: List[str]

class ChatRequest(BaseModel):
    message: str

# Главная страница с редиректом на документацию
@app.get("/")
async def root():
    return RedirectResponse(url="/docs")

# Обработка favicon.ico
@app.get("/favicon.ico")
async def favicon():
    return RedirectResponse(url="https://fastapi.tiangolo.com/img/favicon.png")

@app.post("/match")
async def match_users(profile: UserProfile):
    """Эндпоинт для AI-мэтчинга"""
    input_text = ' '.join(profile.skills + profile.interests)
    input_embedding = model.encode(input_text)
    
    # Вычисление косинусного сходства
    similarities = util.cos_sim(input_embedding, user_embeddings)[0]
    
    # Формирование результатов
    matches = []
    for i, score in enumerate(similarities):
        matches.append({
            "name": users[i]["name"],
            "relevance_score": round(score.item(), 2)
        })
    
    # Сортировка по релевантности
    matches.sort(key=lambda x: x["relevance_score"], reverse=True)
    return {"matches": matches}

@app.post("/chat")
async def handle_chat(request: ChatRequest):
    """Эндпоинт для чат-ассистента"""
    message = request.message.lower()
    detected_skills = []
    
    # Простая эвристика для определения навыков
    if "vr design" in message:
        detected_skills.append("VR Design")
    if "ai" in message or "artificial intelligence" in message:
        detected_skills.append("AI")
    if "3d modeling" in message:
        detected_skills.append("3D Modeling")
    
    if not detected_skills:
        return {"response": "Please specify the skills you're looking for."}
    
    # Используем мэтчинг-систему
    fake_profile = UserProfile(skills=detected_skills, interests=[])
    matches = await match_users(fake_profile)
    
    if matches["matches"]:
        top_match = matches["matches"][0]
        return {
            "response": f"Sure! I recommend reaching out to {top_match['name']}, "
                       f"who specializes in {', '.join(detected_skills)}."
        }
    return {"response": "No matches found."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)