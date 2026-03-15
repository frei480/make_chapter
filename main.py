import asyncio
import logging
from pathlib import Path

from openai import AsyncOpenAI

from chunks import get_chunks
from config import cfg
from prompts import system_prompt, user_prompt

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

input_dir = Path(cfg.main.OUTPUT_DIR)

files = [f for f in input_dir.rglob(cfg.main.FILE_EXTENSION)]

max_tokens_per_request = cfg.main.OPENAI_MAX_TOKENS


def get_openai_client() -> AsyncOpenAI:
    return AsyncOpenAI(
        api_key=cfg.api_keys.OPENAI_API_KEY,
        base_url=cfg.api_keys.OPENAI_BASE_URL,
    )


async def summarize_chunk(chunk: list[str], i: int) -> str:
    logger.info(f"Summarizing chunk {i}")
    client = get_openai_client()
    response = await client.chat.completions.create(
        model=cfg.main.MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": system_prompt[0],
            },
            {
                "role": "user",
                "content": user_prompt[0].format(subtitles_chunk="\n".join(chunk)),
            },
        ],
        max_tokens=cfg.main.OPENAI_MAX_TOKENS,
        n=1,
        stop=None,
        temperature=0.2,
        stream=False,
        reasoning_effort="none",
    )
    return response.choices[0].message.content


async def process_file(file: Path) -> None:
    chunks = get_chunks(file, max_tokens_per_request)
    logger.info(f"File: {file}")
    logger.info(f"Chunks count: {len(chunks)}")
    summarizations = [await summarize_chunk(chunk, i) for i, chunk in enumerate(chunks)]
    with open(file.with_suffix(".md"), "w", encoding="utf-8") as f:
        f.write("\n\n".join(summarizations))


async def main() -> None:
    file = files[0]
    for file in files:
        if file.with_suffix(".md").exists():
            logger.info(f"Skipping {file}")
            continue
        await process_file(file)


if __name__ == "__main__":
    asyncio.run(main())
