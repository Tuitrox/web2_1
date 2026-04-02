import asyncio
from internal.model.schemas import Post, ProcessedPost
 
 
async def stage_process(post: Post) -> ProcessedPost:
    """Этап обработки одного поста (fan-out worker)."""
    # Имитируем какую-то работу
    await asyncio.sleep(0.05)
    return ProcessedPost(
        id=post.id,
        userId=post.userId,
        title=post.title,
        word_count=len(post.body.split()),
        title_upper=post.title.upper(),
    )
 
 
async def stage_filter(posts: list[ProcessedPost], min_words: int) -> list[ProcessedPost]:
    """Этап фильтрации — оставляем посты с word_count >= min_words."""
    return [p for p in posts if p.word_count >= min_words]
 
 
async def run_pipeline(
    posts: list[Post],
    min_words: int = 0,
    workers: int = 4,
) -> list[ProcessedPost]:
    """
    Pipeline:
      1) Fan-out: раздаём посты на N воркеров для обработки
      2) Fan-in: собираем результаты
      3) Фильтрация по min_words
    """
 
    # --- Fan-out / Fan-in ---
    semaphore = asyncio.Semaphore(workers)
 
    async def limited_process(post: Post) -> ProcessedPost:
        async with semaphore:
            return await stage_process(post)
 
    # Запускаем все задачи конкурентно (fan-out),
    # gather собирает результаты обратно (fan-in)
    processed = await asyncio.gather(*(limited_process(p) for p in posts))
    processed = list(processed)
 
    # --- Stage 2: фильтрация ---
    result = await stage_filter(processed, min_words)
 
    return result