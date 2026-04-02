import httpx
from internal.model.schemas import Post
 
 
API_BASE = "https://jsonplaceholder.typicode.com"
 
# Мок-данные на случай если API недоступен (для локальной отладки)
_MOCK_POSTS = [
    {"userId": 1, "id": i, "title": f"Post title number {i}", "body": " ".join([f"word{j}" for j in range(10 + i)])}
    for i in range(1, 21)
]
 
 
async def fetch_posts(limit: int = 10) -> list[Post]:
    """Получает посты с JSONPlaceholder API. При ошибке использует мок."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{API_BASE}/posts")
            response.raise_for_status()
            data = response.json()
    except Exception:
        data = _MOCK_POSTS
 
    posts = [Post(**item) for item in data[:limit]]
    return posts