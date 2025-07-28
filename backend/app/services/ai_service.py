import os
import json
import logging
import shutil
import tempfile
from typing import List, Dict, Optional
from fastapi import UploadFile
from openai import AsyncOpenAI

from app.core.config import settings

logger = logging.getLogger(__name__)


class AIService:
    def __init__(self):
        """Initialize OpenAI Async client."""
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    # =========================================================
    # ✅ FALLBACK CONTENT IDEAS (Used when AI request fails)
    # =========================================================
    def _generate_fallback_ideas(self, topic: str, count: int) -> List[Dict]:
        fallback_ideas = []
        for i in range(count):
            fallback_ideas.append({
                "title": f"Content Idea #{i + 1}: {topic}",
                "description": f"Create engaging content about {topic}. Focus on providing value.",
                "engagement_score": 75,
                "hashtags": [
                    f"#{topic.replace(' ', '').lower()}", "#content", "#viral", "#engagement", "#creator"
                ]
            })
        return fallback_ideas

    # =========================================================
    # ✅ GENERATE CONTENT IDEAS
    # =========================================================
    async def generate_content_ideas(
        self,
        topic: str,
        niche: str,
        audience: str,
        count: int = 5,
        platform: Optional[str] = None
    ) -> List[Dict]:
        """Generate AI-powered content ideas."""
        platform_prompt = f" optimized for {platform.title()}" if platform else ""

        prompt = f"""
        Generate {count} viral content ideas for a {niche} content creator.

        Topic: {topic}
        Target Audience: {audience}
        Platform{platform_prompt}

        For each idea, provide:
        1. A compelling title
        2. A detailed description (2-3 sentences)
        3. Engagement score (0-100)
        4. 3-5 relevant hashtags

        Return as a JSON array.
        """

        try:
            logger.info(f"STAGE ✅: Generating {count} content ideas for topic '{topic}'...")
            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are a viral content strategy expert."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=settings.OPENAI_MAX_TOKENS,
                temperature=0.8
            )

            content_raw = response.choices[0].message.content
            ideas = json.loads(content_raw.strip()) if content_raw else []
            logger.info(f"STAGE ✅: AI returned {len(ideas)} ideas.")
            return ideas if isinstance(ideas, list) else [ideas]

        except json.JSONDecodeError:
            logger.error("❌ Failed to parse AI response as JSON, using fallback ideas.")
            return self._generate_fallback_ideas(topic, count)
        except Exception as e:
            logger.error(f"❌ OpenAI API error: {e}")
            return self._generate_fallback_ideas(topic, count)

    # =========================================================
    # ✅ TRANSCRIBE VIDEO OR AUDIO (WHISPER)
    # =========================================================
    async def transcribe_video(self, video_file: UploadFile) -> str:
        """Transcribe video/audio using Whisper (optimized for production)."""
        temp_file_path = None
        try:
            # ✅ Validate file extension
            if not video_file.filename or not video_file.filename.lower().endswith((
                ".mp4", ".m4a", ".mp3", ".wav", ".webm", ".mpeg", ".oga", ".ogg", ".flac"
            )):
                raise Exception(f"Invalid file format: {video_file.filename}")

            # ✅ Save to temp file (streaming avoids memory overload)
            ext = os.path.splitext(video_file.filename)[1] or ".mp4"
            with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as temp_file:
                await video_file.seek(0)
                shutil.copyfileobj(video_file.file, temp_file)
                temp_file_path = temp_file.name

            file_size = os.path.getsize(temp_file_path)
            logger.info(f"📥 Saved temp video: {temp_file_path}, size={file_size} bytes")

            # ✅ Basic validation (avoid 0-byte corrupted uploads)
            if file_size < 50 * 1024:  # ~50KB min
                raise Exception("Video file too small or may not contain valid audio.")

            # ✅ Whisper transcription
            with open(temp_file_path, "rb") as audio_file:
                transcript = await self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="text"
                )

            logger.info("STAGE ✅: Transcription completed successfully.")
            return transcript if isinstance(transcript, str) else transcript.get("text", "")

        except Exception as e:
            logger.error(f"❌ Video transcription error: {e}")
            raise Exception(f"Failed to transcribe video: {e}")

        finally:
            # ✅ Always clean up
            video_file.file.close()
            if temp_file_path and os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                logger.info(f"🗑 Temp file deleted - {temp_file_path}")

    # =========================================================
    # ✅ REPURPOSE CONTENT
    # =========================================================
    async def repurpose_content(
        self,
        transcript: str,
        original_title: str,
        original_description: str,
        target_platforms: list,
        tone: str = "motivational"
    ) -> dict:
        """Repurpose transcript into platform-specific content."""
        repurposed = {}

        for platform in target_platforms:
            try:
                logger.info(f"STAGE ✅: Repurposing content for {platform}...")
                prompt = (
                    f"You are an expert social media content repurposer. "
                    f"Repurpose the following video for {platform} in a {tone} tone. "
                    f"Generate a catchy title/caption and 5 trending hashtags.\n\n"
                    f"Title: {original_title}\n"
                    f"Description: {original_description}\n"
                    f"Transcript: {transcript[:1000]}..."
                )

                response = await self.client.chat.completions.create(
                    model=settings.OPENAI_MODEL,
                    messages=[
                        {"role": "system", "content": "You create high-converting social media content."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=500,
                    temperature=0.7
                )

                content_raw = response.choices[0].message.content
                repurposed[platform.lower()] = content_raw.strip() if content_raw else ""
                logger.info(f"STAGE ✅: Repurposing completed for {platform}")

            except Exception as e:
                logger.error(f"❌ Repurpose_content error for {platform}: {e}")
                repurposed[platform.lower()] = f"Fallback: {tone.title()} snippet: {transcript[:120]}..."

        return repurposed

    # =========================================================
    # ✅ ANALYZE CONTENT PERFORMANCE
    # =========================================================
    async def analyze_content_performance(self, content_data: Dict, platform_metrics: Dict) -> Dict:
        """Analyze content performance and provide insights."""
        prompt = f"""
        Analyze this content performance data and provide actionable insights:

        Content: {json.dumps(content_data, indent=2)}
        Metrics: {json.dumps(platform_metrics, indent=2)}

        JSON output format with fields:
        performance_score, key_insights, improvement_suggestions, trend_analysis, next_content_recommendations
        """
        try:
            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are a content performance analyst."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.3
            )
            content_raw = response.choices[0].message.content
            return json.loads(content_raw.strip()) if content_raw else {
                "performance_score": 0,
                "key_insights": ["No response from AI"],
                "improvement_suggestions": ["Try again later"],
                "trend_analysis": "Unable to analyze",
                "next_content_recommendations": ["Check back soon"]
            }
        except Exception as e:
            logger.error(f"❌ Performance analysis error: {e}")
            return {
                "performance_score": 0,
                "key_insights": ["Analysis temporarily unavailable"],
                "improvement_suggestions": ["Try again later"],
                "trend_analysis": "Unable to analyze",
                "next_content_recommendations": ["Check back soon"]
            }


# =========================================================
# ✅ GLOBAL INSTANCE (IMPORT THIS IN ROUTES)
# =========================================================
ai_service = AIService()
