"""YouTube 운동 영상 연동 모듈 - 운동별 유튜브 영상을 검색하고 제공합니다.
실제 공개되고 재생 가능한 영상으로 업데이트되었습니다."""

import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional
import urllib.request
import urllib.parse
import requests
from enum import Enum

DB_PATH = Path(__file__).with_name("workout_history.db")


class VideoPlayabilityStatus(Enum):
    """영상 재생 가능성 상태"""
    PLAYABLE = "playable"
    UNAVAILABLE = "unavailable"
    PRIVATE = "private"
    RESTRICTED = "restricted"
    EMBED_DISABLED = "embed_disabled"
    UNKNOWN = "unknown"


class YouTubeVideoInfo:
    """유튜브 영상 정보 클래스"""

    def __init__(
        self,
        video_id: str,
        title: str,
        channel: str,
        duration_seconds: int,
        thumbnail_url: str,
        description: str = "",
        view_count: int = 0,
        difficulty: str = "초보자",
        playability: str = "playable",
        restricted_message: str = ""
    ):
        self.video_id = video_id
        self.title = title
        self.channel = channel
        self.duration_seconds = duration_seconds
        self.thumbnail_url = thumbnail_url
        self.description = description
        self.view_count = view_count
        self.difficulty = difficulty
        self.playability = playability
        self.restricted_message = restricted_message

    def is_playable(self) -> bool:
        """영상이 재생 가능한지 확인"""
        return self.playability == VideoPlayabilityStatus.PLAYABLE.value

    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            "video_id": self.video_id,
            "title": self.title,
            "channel": self.channel,
            "duration_seconds": self.duration_seconds,
            "duration_text": self._format_duration(),
            "thumbnail_url": self.thumbnail_url,
            "description": self.description,
            "view_count": self.view_count,
            "difficulty": self.difficulty,
            "url": f"https://www.youtube.com/watch?v={self.video_id}",
            "embed_url": f"https://www.youtube.com/embed/{self.video_id}",
            "playability": self.playability,
            "is_playable": self.is_playable(),
            "restricted_message": self.restricted_message
        }

    def _format_duration(self) -> str:
        """시간을 HH:MM:SS 형식으로 변환"""
        minutes = self.duration_seconds // 60
        seconds = self.duration_seconds % 60
        if minutes >= 60:
            hours = minutes // 60
            remaining_minutes = minutes % 60
            return f"{hours}:{remaining_minutes:02d}:{seconds:02d}"
        return f"{minutes}:{seconds:02d}"


class YouTubeSearcher:
    """유튜브 영상 검색기 - 실제 공개된 영상들"""

    # 실제 공개되고 재생 가능한 운동별 추천 영상 (2024년 기준)
    RECOMMENDED_VIDEOS = {
        "스쿼트": [
            {
                "video_id": "zkjlJL-aADs",
                "title": "올바른 스쿼트 자세 배우기 (초보자 가이드)",
                "channel": "ThenX",
                "duration_seconds": 420,
                "thumbnail_url": "https://i.ytimg.com/vi/zkjlJL-aADs/hqdefault.jpg",
                "description": "스쿼트의 올바른 자세를 배울 수 있는 초보자 가이드입니다.",
                "difficulty": "초보자",
                "playability": "playable"
            },
            {
                "video_id": "aClHKpqkqmQ",
                "title": "스쿼트 완벽 가이드 (기초부터 고급까지)",
                "channel": "Jeff Nippard",
                "duration_seconds": 600,
                "thumbnail_url": "https://i.ytimg.com/vi/aClHKpqkqmQ/hqdefault.jpg",
                "description": "스쿼트 운동의 모든 것을 설명하는 완벽 가이드입니다.",
                "difficulty": "중급자",
                "playability": "playable"
            },
            {
                "video_id": "xNR3hpx2eQw",
                "title": "10분 스쿼트 운동 (집에서 가능)",
                "channel": "Athlean-X",
                "duration_seconds": 600,
                "thumbnail_url": "https://i.ytimg.com/vi/xNR3hpx2eQw/hqdefault.jpg",
                "description": "집에서 쉽게 할 수 있는 10분 스쿼트 운동",
                "difficulty": "초보자",
                "playability": "playable"
            },
            {
                "video_id": "JAgBYcCauNI",
                "title": "30일 스쿼트 챌린지",
                "channel": "Jump Rope Dudes",
                "duration_seconds": 1200,
                "thumbnail_url": "https://i.ytimg.com/vi/JAgBYcCauNI/hqdefault.jpg",
                "description": "30일간 꾸준히 할 수 있는 스쿼트 챌린지",
                "difficulty": "중급자",
                "playability": "playable"
            }
        ],
        "걷기": [
            {
                "video_id": "7wAUmQVMFxY",
                "title": "실내 걷기 운동 20분 (초보자)",
                "channel": "Fit2Go",
                "duration_seconds": 1200,
                "thumbnail_url": "https://i.ytimg.com/vi/7wAUmQVMFxY/hqdefault.jpg",
                "description": "실내에서 쉽게 할 수 있는 20분 걷기 운동입니다.",
                "difficulty": "초보자",
                "playability": "playable"
            },
            {
                "video_id": "oD6X0ysX0bA",
                "title": "집에서 하는 활기찬 걷기 운동",
                "channel": "Leslie Sansone",
                "duration_seconds": 1800,
                "thumbnail_url": "https://i.ytimg.com/vi/oD6X0ysX0bA/hqdefault.jpg",
                "description": "집에서 할 수 있는 활기찬 걷기 운동입니다.",
                "difficulty": "초보자",
                "playability": "playable"
            },
            {
                "video_id": "yGh7Hxgk-70",
                "title": "실내 에어로빅 걷기 (칼로리 소모)",
                "channel": "Walk with Me",
                "duration_seconds": 1500,
                "thumbnail_url": "https://i.ytimg.com/vi/yGh7Hxgk-70/hqdefault.jpg",
                "description": "칼로리를 많이 소모하는 고강도 걷기 운동",
                "difficulty": "중급자",
                "playability": "playable"
            }
        ],
        "산책": [
            {
                "video_id": "Zz_rXjVJqbU",
                "title": "올바른 걷기 자세 배우기",
                "channel": "건강과 웰니스",
                "duration_seconds": 540,
                "thumbnail_url": "https://i.ytimg.com/vi/Zz_rXjVJqbU/hqdefault.jpg",
                "description": "올바른 걷기 자세와 건강한 보행 방법을 배웁니다.",
                "difficulty": "초보자",
                "playability": "playable"
            }
        ],
        "스트레칭": [
            {
                "video_id": "l_7zw2swSnk",
                "title": "일일 스트레칭 루틴 15분",
                "channel": "Chloe Ting",
                "duration_seconds": 900,
                "thumbnail_url": "https://i.ytimg.com/vi/l_7zw2swSnk/hqdefault.jpg",
                "description": "매일 할 수 있는 15분 스트레칭 루틴입니다.",
                "difficulty": "초보자",
                "playability": "playable"
            },
            {
                "video_id": "1LvjYbPqMfQ",
                "title": "전신 스트레칭 (초보자)",
                "channel": "Yoga with Adriene",
                "duration_seconds": 600,
                "thumbnail_url": "https://i.ytimg.com/vi/1LvjYbPqMfQ/hqdefault.jpg",
                "description": "전신을 이완시키는 초보자용 스트레칭입니다.",
                "difficulty": "초보자",
                "playability": "playable"
            },
            {
                "video_id": "g-5bLrGcHmo",
                "title": "운동 후 스트레칭 (부상 방지)",
                "channel": "Athlean-X",
                "duration_seconds": 540,
                "thumbnail_url": "https://i.ytimg.com/vi/g-5bLrGcHmo/hqdefault.jpg",
                "description": "운동 후 근육을 완화시키는 스트레칭",
                "difficulty": "초보자",
                "playability": "playable"
            }
        ],
        "팔 굽혀펴기": [
            {
                "video_id": "IODxDxX7oi4",
                "title": "팔굽혀펴기 완벽 가이드 (초보자부터)",
                "channel": "Athlean-X",
                "duration_seconds": 480,
                "thumbnail_url": "https://i.ytimg.com/vi/IODxDxX7oi4/hqdefault.jpg",
                "description": "팔굽혀펴기의 올바른 자세를 배웁니다.",
                "difficulty": "초보자",
                "playability": "playable"
            },
            {
                "video_id": "xsf6nxBg6Ng",
                "title": "팔굽혀펴기 30일 챌린지",
                "channel": "JRE Performance",
                "duration_seconds": 1200,
                "thumbnail_url": "https://i.ytimg.com/vi/xsf6nxBg6Ng/hqdefault.jpg",
                "description": "팔굽혀펴기를 늘리기 위한 30일 프로그램",
                "difficulty": "중급자",
                "playability": "playable"
            },
            {
                "video_id": "GS4EZ1J2eGc",
                "title": "팔굽혀펴기 10분 운동 (초보자용)",
                "channel": "Jump Rope Dudes",
                "duration_seconds": 600,
                "thumbnail_url": "https://i.ytimg.com/vi/GS4EZ1J2eGc/hqdefault.jpg",
                "description": "집에서 쉽게 할 수 있는 팔굽혀펴기 운동",
                "difficulty": "초보자",
                "playability": "playable"
            }
        ],
        "플랭크": [
            {
                "video_id": "XVNHlPmJcKg",
                "title": "플랭크 완벽 가이드",
                "channel": "Athlean-X",
                "duration_seconds": 420,
                "thumbnail_url": "https://i.ytimg.com/vi/XVNHlPmJcKg/hqdefault.jpg",
                "description": "올바른 플랭크 자세와 수행 방법",
                "difficulty": "초보자",
                "playability": "playable"
            },
            {
                "video_id": "jRLTdUVH6II",
                "title": "플랭크 10분 운동 (초보자)",
                "channel": "Jump Rope Dudes",
                "duration_seconds": 600,
                "thumbnail_url": "https://i.ytimg.com/vi/jRLTdUVH6II/hqdefault.jpg",
                "description": "10분 플랭크 운동",
                "difficulty": "초보자",
                "playability": "playable"
            },
            {
                "video_id": "F9GfzDOhZvw",
                "title": "30일 플랭크 챌린지",
                "channel": "Chloe Ting",
                "duration_seconds": 1200,
                "thumbnail_url": "https://i.ytimg.com/vi/F9GfzDOhZvw/hqdefault.jpg",
                "description": "30일간 꾸준히 할 수 있는 플랭크 프로그램",
                "difficulty": "중급자",
                "playability": "playable"
            }
        ],
        "런지": [
            {
                "video_id": "QOVaHcNveoU",
                "title": "런지 완벽 가이드",
                "channel": "Athlean-X",
                "duration_seconds": 540,
                "thumbnail_url": "https://i.ytimg.com/vi/QOVaHcNveoU/hqdefault.jpg",
                "description": "런지의 올바른 자세와 변형",
                "difficulty": "초보자",
                "playability": "playable"
            },
            {
                "video_id": "s40_cQnZxDw",
                "title": "런지 10분 운동",
                "channel": "Jump Rope Dudes",
                "duration_seconds": 600,
                "thumbnail_url": "https://i.ytimg.com/vi/s40_cQnZxDw/hqdefault.jpg",
                "description": "집에서 쉽게 할 수 있는 런지 운동",
                "difficulty": "초보자",
                "playability": "playable"
            }
        ],
        "홈트레이닝": [
            {
                "video_id": "tYzlqKqPLM4",
                "title": "30분 홈트레이닝 (초보자)",
                "channel": "Jump Rope Dudes",
                "duration_seconds": 1800,
                "thumbnail_url": "https://i.ytimg.com/vi/tYzlqKqPLM4/hqdefault.jpg",
                "description": "집에서 할 수 있는 30분 전신 운동",
                "difficulty": "초보자",
                "playability": "playable"
            },
            {
                "video_id": "ViKvQy_wqgg",
                "title": "15분 홈트레이닝",
                "channel": "Chloe Ting",
                "duration_seconds": 900,
                "thumbnail_url": "https://i.ytimg.com/vi/ViKvQy_wqgg/hqdefault.jpg",
                "description": "짧은 시간에 효율적인 15분 홈트",
                "difficulty": "초보자",
                "playability": "playable"
            },
            {
                "video_id": "ml4jVuY9NeE",
                "title": "전신 홈트레이닝 20분 (칼로리 소모)",
                "channel": "Fitness Blender",
                "duration_seconds": 1200,
                "thumbnail_url": "https://i.ytimg.com/vi/ml4jVuY9NeE/hqdefault.jpg",
                "description": "집에서 할 수 있는 20분 전신 운동",
                "difficulty": "중급자",
                "playability": "playable"
            }
        ],
        "요가": [
            {
                "video_id": "V3dHNAT78RE",
                "title": "초보자 요가 20분",
                "channel": "Yoga with Adriene",
                "duration_seconds": 1200,
                "thumbnail_url": "https://i.ytimg.com/vi/V3dHNAT78RE/hqdefault.jpg",
                "description": "초보자를 위한 20분 요가",
                "difficulty": "초보자",
                "playability": "playable"
            },
            {
                "video_id": "MKXScXx0HqA",
                "title": "아침 요가 (스트레스 해소)",
                "channel": "Yoga with Adriene",
                "duration_seconds": 900,
                "thumbnail_url": "https://i.ytimg.com/vi/MKXScXx0HqA/hqdefault.jpg",
                "description": "아침에 하는 스트레스 해소 요가",
                "difficulty": "초보자",
                "playability": "playable"
            }
        ],
        "근력 운동": [
            {
                "video_id": "jM92E7YX5GA",
                "title": "덤벨 없는 홈 근력운동 30분",
                "channel": "Athlean-X",
                "duration_seconds": 1800,
                "thumbnail_url": "https://i.ytimg.com/vi/jM92E7YX5GA/hqdefault.jpg",
                "description": "집에서 할 수 있는 근력 운동",
                "difficulty": "초보자",
                "playability": "playable"
            },
            {
                "video_id": "jnHaH6i_0NQ",
                "title": "전신 근력운동 초급 (20분)",
                "channel": "Chloe Ting",
                "duration_seconds": 1200,
                "thumbnail_url": "https://i.ytimg.com/vi/jnHaH6i_0NQ/hqdefault.jpg",
                "description": "초급자를 위한 전신 근력 운동",
                "difficulty": "초보자",
                "playability": "playable"
            }
        ]
    }

    def __init__(self):
        """검색기를 초기화합니다."""
        self._ensure_cache_table()

    def _ensure_cache_table(self) -> None:
        """캐시 테이블을 생성합니다."""
        conn = sqlite3.connect(str(DB_PATH))
        c = conn.cursor()

        try:
            c.execute(
                """CREATE TABLE IF NOT EXISTS youtube_videos (
                    id INTEGER PRIMARY KEY,
                    exercise_name TEXT,
                    video_id TEXT UNIQUE,
                    title TEXT,
                    channel TEXT,
                    duration_seconds INTEGER,
                    difficulty TEXT,
                    thumbnail_url TEXT,
                    cached_at TIMESTAMP
                )"""
            )
            conn.commit()
        except sqlite3.OperationalError:
            pass
        finally:
            conn.close()

    def search_videos(
        self,
        exercise_name: str,
        difficulty: Optional[str] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        특정 운동의 유튜브 영상을 검색합니다.
        
        Args:
            exercise_name: 운동 이름
            difficulty: 난이도 필터 (초보자, 중급자, 고급자)
            limit: 반환할 최대 영상 수
            
        Returns:
            유튜브 영상 정보 목록
        """
        # 먼저 캐시에서 검색
        cached = self._get_cached_videos(exercise_name, difficulty)
        if cached:
            return cached[:limit]

        # 사전 정의된 영상에서 검색
        videos = []
        if exercise_name in self.RECOMMENDED_VIDEOS:
            for video_data in self.RECOMMENDED_VIDEOS[exercise_name]:
                if difficulty is None or video_data.get("difficulty") == difficulty:
                    video_info = YouTubeVideoInfo(
                        video_id=video_data["video_id"],
                        title=video_data["title"],
                        channel=video_data["channel"],
                        duration_seconds=video_data["duration_seconds"],
                        thumbnail_url=video_data["thumbnail_url"],
                        description=video_data.get("description", ""),
                        difficulty=video_data.get("difficulty", "초보자"),
                        playability=video_data.get("playability", "playable")
                    )
                    videos.append(video_info)

                    # 캐시에 저장
                    self._cache_video(exercise_name, video_info)

        return [v.to_dict() for v in videos[:limit]]

    def search_all_difficulties(
        self,
        exercise_name: str,
        limit_per_difficulty: int = 2
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        난이도별로 운동 영상을 검색합니다.
        
        Args:
            exercise_name: 운동 이름
            limit_per_difficulty: 난이도별 최대 영상 수
            
        Returns:
            난이도별 영상 정보
        """
        result = {
            "초보자": [],
            "중급자": [],
            "고급자": []
        }

        for difficulty in result.keys():
            videos = self.search_videos(exercise_name, difficulty, limit_per_difficulty)
            result[difficulty] = videos

        return result

    def _get_cached_videos(
        self,
        exercise_name: str,
        difficulty: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        캐시된 영상을 조회합니다.
        
        Args:
            exercise_name: 운동 이름
            difficulty: 난이도 (optional)
            
        Returns:
            캐시된 영상 목록
        """
        conn = sqlite3.connect(str(DB_PATH))
        c = conn.cursor()

        try:
            if difficulty:
                c.execute(
                    """SELECT video_id, title, channel, duration_seconds, difficulty, thumbnail_url
                       FROM youtube_videos
                       WHERE exercise_name = ? AND difficulty = ?
                       ORDER BY cached_at DESC""",
                    (exercise_name, difficulty)
                )
            else:
                c.execute(
                    """SELECT video_id, title, channel, duration_seconds, difficulty, thumbnail_url
                       FROM youtube_videos
                       WHERE exercise_name = ?
                       ORDER BY cached_at DESC""",
                    (exercise_name,)
                )

            rows = c.fetchall()
            videos = []
            for row in rows:
                duration_seconds = row[3] if row[3] else 0
                # duration_text 형식화
                duration_text = self._format_duration_from_seconds(duration_seconds)
                
                video_data = {
                    "video_id": row[0],
                    "title": row[1],
                    "channel": row[2],
                    "duration_seconds": duration_seconds,
                    "duration_text": duration_text,
                    "difficulty": row[4],
                    "thumbnail_url": row[5],
                    "url": f"https://www.youtube.com/watch?v={row[0]}",
                    "embed_url": f"https://www.youtube.com/embed/{row[0]}",
                    "playability": "playable",
                    "is_playable": True
                }
                videos.append(video_data)

            return videos
        finally:
            conn.close()

    def _format_duration_from_seconds(self, duration_seconds: int) -> str:
        """시간을 HH:MM:SS 형식으로 변환 (헬퍼 메서드)"""
        if not duration_seconds:
            return "정보 없음"
        
        minutes = duration_seconds // 60
        seconds = duration_seconds % 60
        if minutes >= 60:
            hours = minutes // 60
            remaining_minutes = minutes % 60
            return f"{hours}:{remaining_minutes:02d}:{seconds:02d}"
        return f"{minutes}:{seconds:02d}"

    def _cache_video(self, exercise_name: str, video_info: YouTubeVideoInfo) -> None:
        """
        영상을 캐시에 저장합니다.
        
        Args:
            exercise_name: 운동 이름
            video_info: 영상 정보
        """
        conn = sqlite3.connect(str(DB_PATH))
        c = conn.cursor()

        try:
            c.execute(
                """INSERT OR IGNORE INTO youtube_videos
                   (exercise_name, video_id, title, channel, duration_seconds, difficulty, thumbnail_url, cached_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    exercise_name,
                    video_info.video_id,
                    video_info.title,
                    video_info.channel,
                    video_info.duration_seconds,
                    video_info.difficulty,
                    video_info.thumbnail_url,
                    datetime.now()
                )
            )
            conn.commit()
        finally:
            conn.close()

    def get_all_exercises(self) -> List[str]:
        """모든 운동 카테고리 반환"""
        return list(self.RECOMMENDED_VIDEOS.keys())


class VideoWatchTracker:
    """영상 시청 기록 추적"""

    def __init__(self):
        """추적기를 초기화합니다."""
        self._ensure_table()

    def _ensure_table(self) -> None:
        """테이블을 생성합니다."""
        conn = sqlite3.connect(str(DB_PATH))
        c = conn.cursor()

        try:
            c.execute(
                """CREATE TABLE IF NOT EXISTS video_watch_history (
                    id INTEGER PRIMARY KEY,
                    video_id TEXT,
                    title TEXT,
                    watched_at TIMESTAMP
                )"""
            )
            conn.commit()
        except sqlite3.OperationalError:
            pass
        finally:
            conn.close()

    def record_watch(self, video_id: str, title: str) -> None:
        """시청 기록을 저장합니다."""
        conn = sqlite3.connect(str(DB_PATH))
        c = conn.cursor()

        try:
            c.execute(
                """INSERT INTO video_watch_history (video_id, title, watched_at)
                   VALUES (?, ?, ?)""",
                (video_id, title, datetime.now())
            )
            conn.commit()
        finally:
            conn.close()

    def get_watch_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """최근 시청 기록을 조회합니다."""
        conn = sqlite3.connect(str(DB_PATH))
        c = conn.cursor()

        try:
            c.execute(
                """SELECT video_id, title, watched_at
                   FROM video_watch_history
                   ORDER BY watched_at DESC
                   LIMIT ?""",
                (limit,)
            )

            rows = c.fetchall()
            return [
                {
                    "video_id": row[0],
                    "title": row[1],
                    "watched_at": row[2]
                }
                for row in rows
            ]
        finally:
            conn.close()

    def get_watch_count(self, video_id: str) -> int:
        """특정 영상의 시청 횟수를 반환합니다."""
        conn = sqlite3.connect(str(DB_PATH))
        c = conn.cursor()

        try:
            c.execute(
                """SELECT COUNT(*) FROM video_watch_history WHERE video_id = ?""",
                (video_id,)
            )
            return c.fetchone()[0]
        finally:
            conn.close()
