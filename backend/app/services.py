import os

from openai import AsyncOpenAI

from .schemas import MatchCreate


def get_openai_client() -> AsyncOpenAI:
    api_key = os.getenv("OPENROUTER_API_KEY")
    base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY environment variable is missing")
    return AsyncOpenAI(base_url=base_url, api_key=api_key)

async def generate_recap_service(match: MatchCreate) -> tuple[str, str]:
    model_name = os.getenv("OPENROUTER_MODEL", "openrouter/free")
    
    home_goals = [f"{s.player} {s.minute}'" for s in match.scorers if s.team == match.home_team]
    away_goals = [f"{s.player} {s.minute}'" for s in match.scorers if s.team == match.away_team]

    context = (
        f"Match: {match.home_team} vs {match.away_team} ({match.match_date}). "
        f"Final Score: {match.home_score}-{match.away_score}. "
        f"{match.home_team} goals: {', '.join(home_goals) if home_goals else 'None'}. "
        f"{match.away_team} goals: {', '.join(away_goals) if away_goals else 'None'}. "
        f"Key details: {match.summary_notes or 'Standard match flow.'}"
    )

    try:
        client = get_openai_client()
        system_prompt = (
            "An expert sports journalist. "
            "Write a 2-3 sentence match recap strictly based ONLY on the provided match stats."
        )

        response = await client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": context},
            ],
            temperature=0.5,
            max_tokens=250,
        )
        return response.choices[0].message.content or "", model_name
    except Exception as e:
        # Fallback-режим, если ИИ недоступен или заблокирован политикой
        fallback_recap = f"Match played between {match.home_team} and {match.away_team} ended with a score of {match.home_score}-{match.away_score}."
        return fallback_recap, "fallback-local"    