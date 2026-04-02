import asyncio
from internal.model.schemas import Post, ProcessedPost
 
 
async def stage_process(post: Post) -> ProcessedPost:
    """Этап обработки одного поста (fan-out worker)."""
    await asyncio.sleep(0.05)
    return ProcessedPost(
        id=post.id,
        userId=post.userId,
        title=post.title,
        word_count=len(post.body.split()),
        title_upper=post.title.upper(),
    )
 
 
async def stage_filter(posts: list[ProcessedPost], min_words: int) -> list[ProcessedPost]:
    """Оставляем посты с word_count >= min_words."""
    return [p for p in posts if p.word_count >= min_words]
 
 
async def run_pipeline(
    posts: list[Post],
    min_words: int = 0,
    workers: int = 4,
) -> list[ProcessedPost]:
    """
    Pipeline:
      Fan-out: раздаём посты на N воркеров для обработки
      Fan-in: собираем результаты
      Фильтрация по min_words
    """
 
    semaphore = asyncio.Semaphore(workers)
 
    async def limited_process(post: Post) -> ProcessedPost:
        async with semaphore:
            return await stage_process(post)
 
    # Запускаем все задачи конкурентно (fan-out),
    # gather собирает результаты обратно (fan-in)
    processed = await asyncio.gather(*(limited_process(p) for p in posts))
    processed = list(processed)
 
    result = await stage_filter(processed, min_words)
 
    return result