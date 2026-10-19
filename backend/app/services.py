import os
import logging
from gigachat import GigaChat
from opentelemetry import trace
from .schemas import StoryCreate

logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)


def generate_story_service_sync(story: StoryCreate) -> tuple[str, str]:
    auth_key = os.getenv("GIGACHAT_AUTH_KEY")
    model_name = os.getenv("GIGACHAT_MODEL", "GigaChat-2")

    if not auth_key:
        fallback_story = (
            f"Story '{story.title}'. In {story.when_happens} at {story.where_happens}, "
            f"heroes ({story.heroes}) faced the following events: {story.summary}."
        )
        return fallback_story, "fallback-local"

    context = (
        f"Title: {story.title}\n"
        f"When: {story.when_happens}\n"
        f"Where: {story.where_happens}\n"
        f"Heroes: {story.heroes}\n"
        f"Plot summary: {story.summary}"
    )

    # Кастомный OpenTelemetry спан для отслеживания времени генерации GigaChat
    with tracer.start_as_current_span("gigachat_generation") as span:
        span.set_attribute("gigachat.model", model_name)
        span.set_attribute("story.title", story.title)

        try:
            with GigaChat(
                credentials=auth_key,
                scope="GIGACHAT_API_PERS",
                model=model_name,
                verify_ssl_certs=False
            ) as client:
                system_prompt = (
                    "You are an expert sci-fi fiction writer. "
                    "Write an engaging, detailed, and immersive science fiction short story "
                    "strictly based on the provided input data."
                )

                response = client.chat(f"{system_prompt}\n\n{context}")
                story_text = response.choices[0].message.content if response.choices else ""
                span.set_attribute("gigachat.success", True)
                return story_text, model_name

        except Exception as e:
            logger.error(f"GigaChat service error: {e}")
            span.record_exception(e)
            span.set_attribute("gigachat.success", False)
            fallback_story = (
                f"Story '{story.title}'. In {story.when_happens} at {story.where_happens}, "
                f"heroes ({story.heroes}) faced the following events: {story.summary}."
            )
            return fallback_story, "fallback-local"


async def generate_story_service(story: StoryCreate) -> tuple[str, str]:
    return generate_story_service_sync(story)