"""
Простой WEB-клиент на FastAPI.
 
Получает посты с JSONPlaceholder API, прогоняет через pipeline
(fan-out обработка → fan-in сбор → фильтрация) и отдаёт результат.
 
Запуск:
    uvicorn cmd.main:app --reload
 
Примеры запросов:
    GET /posts?limit=10&min_words=5
    GET /posts?limit=20&min_words=10&workers=8
"""
 
from fastapi import FastAPI, Query, HTTPException
from internal.api.client import fetch_posts
from internal.pipeline.pipeline import run_pipeline
from internal.model.schemas import ProcessedPost
 
app = FastAPI(title="Simple Web Client", version="0.1.0")
 
 
@app.get("/posts", response_model=list[ProcessedPost])
async def get_processed_posts(
    limit: int = Query(10, ge=1, le=100, description="Кол-во постов для загрузки"),
    min_words: int = Query(0, ge=0, description="Минимум слов в body для фильтрации"),
    workers: int = Query(4, ge=1, le=16, description="Кол-во конкурентных воркеров"),
):
    """
    Эндпоинт:
    1. Забирает посты с JSONPlaceholder (HTTP GET + JSON parse)
    2. Fan-out: раздаёт на workers горутин для обработки
    3. Fan-in: собирает результаты
    4. Фильтрует по min_words
    """
    try:
        posts = await fetch_posts(limit)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Ошибка при запросе к API: {e}")
 
    try:
        result = await run_pipeline(posts, min_words=min_words, workers=workers)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка pipeline: {e}")
 
    return result
 
 
@app.get("/")
async def root():
    return {
        "message": "Simple Web Client",
        "usage": "GET /posts?limit=10&min_words=5",
        "docs": "/docs",
    }