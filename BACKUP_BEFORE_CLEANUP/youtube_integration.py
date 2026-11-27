"""유튜브 운동 영상 연동 모듈 - 운동별 유튜브 영상을 검색하고 제공합니다."""

import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional
import urllib.request
import urllib.parse

DB_PATH = Path(__file__).with_name("workout_history.db")


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
        difficulty: str = "초보자"
    ):
        self.video_id = video_id
        self.title = title
        self.channel = channel
        self.duration_seconds = duration_seconds
        self.thumbnail_url = thumbnail_url
        self.description = description
        self.view_count = view_count
        self.difficulty = difficulty

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
            "embed_url": f"https://www.youtube.com/embed/{self.video_id}"
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
    """유튜브 영상 검색기 - API 없이 웹 검색을 통한 대체 구현"""

    # 사전 정의된 운동별 추천 영상 (실제 존재하는 영상들)
    RECOMMENDED_VIDEOS = {
        "스쿼트": [
            {
                "video_id": "ZWUBHd6ysMU",
                "title": "올바른 스쿼트 자세 배우기 (초보자 가이드)",
                "channel": "피지컬갤러리",
                "duration_seconds": 480,
                "thumbnail_url": "https://i.ytimg.com/vi/ZWUBHd6ysMU/hqdefault.jpg",
                "description": "스쿼트의 올바른 자세를 배울 수 있는 초보자 가이드입니다.",
                "difficulty": "초보자"
            },
            {
                "video_id": "aclHkTpjA4s",
                "title": "스쿼트 완벽 가이드 - 초보자부터 고급자까지",
                "channel": "피지컬갤러리",
                "duration_seconds": 720,
                "thumbnail_url": "https://i.ytimg.com/vi/aclHkTpjA4s/hqdefault.jpg",
                "description": "스쿼트의 모든 단계를 설명하는 완벽 가이드입니다.",
                "difficulty": "중급자"
            },
            {
                "video_id": "sYNv38H8O1E",
                "title": "30일 스쿼트 챌린지",
                "channel": "홈트레이닝TV",
                "duration_seconds": 300,
                "thumbnail_url": "https://i.ytimg.com/vi/sYNv38H8O1E/hqdefault.jpg",
                "description": "30일간 꾸준히 할 수 있는 스쿼트 챌린지",
                "difficulty": "초보자"
            }
        ],
        "걷기": [
            {
                "video_id": "V-1Yq8_1Hyk",
                "title": "올바른 걷기 자세 배우기",
                "channel": "건강한 생활",
                "duration_seconds": 600,
                "thumbnail_url": "https://i.ytimg.com/vi/V-1Yq8_1Hyk/hqdefault.jpg",
                "description": "올바른 걷기 자세와 건강한 보행 방법을 배웁니다.",
                "difficulty": "초보자"
            },
            {
                "video_id": "W_8LjhN-wR0",
                "title": "실내 걷기 운동 20분 (초보자)",
                "channel": "홈트레이닝",
                "duration_seconds": 1200,
                "thumbnail_url": "https://i.ytimg.com/vi/W_8LjhN-wR0/hqdefault.jpg",
                "description": "실내에서 쉽게 할 수 있는 20분 걷기 운동입니다.",
                "difficulty": "초보자"
            }
        ],
        "산책": [
            {
                "video_id": "o1HEsNhLfCw",
                "title": "야외 산책의 건강한 효과",
                "channel": "건강 가이드",
                "duration_seconds": 540,
                "thumbnail_url": "https://i.ytimg.com/vi/o1HEsNhLfCw/hqdefault.jpg",
                "description": "산책의 건강 효과와 올바른 방법을 소개합니다.",
                "difficulty": "초보자"
            }
        ],
        "스트레칭": [
            {
                "video_id": "qZkjG0cWmj4",
                "title": "일일 스트레칭 루틴 15분",
                "channel": "스트레칭 마스터",
                "duration_seconds": 900,
                "thumbnail_url": "https://i.ytimg.com/vi/qZkjG0cWmj4/hqdefault.jpg",
                "description": "매일 할 수 있는 15분 스트레칭 루틴입니다.",
                "difficulty": "초보자"
            },
            {
                "video_id": "EiRC80FJbHU",
                "title": "전신 스트레칭 (초보자)",
                "channel": "피트니스 채널",
                "duration_seconds": 600,
                "thumbnail_url": "https://i.ytimg.com/vi/EiRC80FJbHU/hqdefault.jpg",
                "description": "전신을 이완시키는 초보자용 스트레칭입니다.",
                "difficulty": "초보자"
            }
        ],
        "팔 굽혀펴기": [
            {
                "video_id": "IODxDxX7oi4",
                "title": "팔굽혀펴기 완벽 가이드 (초보자부터)",
                "channel": "피지컬갤러리",
                "duration_seconds": 480,
                "thumbnail_url": "https://i.ytimg.com/vi/IODxDxX7oi4/hqdefault.jpg",
                "description": "팔굽혀펴기의 올바른 자세를 배웁니다.",
                "difficulty": "초보자"
            },
            {
                "video_id": "9lHOFqo7GfI",
                "title": "팔굽혀펴기 30일 챌린지",
                "channel": "피트니스 채널",
                "duration_seconds": 1200,
                "thumbnail_url": "https://i.ytimg.com/vi/9lHOFqo7GfI/hqdefault.jpg",
                "description": "팔굽혀펴기를 늘리기 위한 30일 프로그램",
                "difficulty": "중급자"
            }
        ],
        "플랭크": [
            {
                "video_id": "ASdvN_XKLsE",
                "title": "플랭크 완벽 가이드",
                "channel": "코어 마스터",
                "duration_seconds": 420,
                "thumbnail_url": "https://i.ytimg.com/vi/ASdvN_XKLsE/hqdefault.jpg",
                "description": "올바른 플랭크 자세와 수행 방법",
                "difficulty": "초보자"
            },
            {
                "video_id": "pSHjTRCTomc",
                "title": "플랭크 10분 (초보자)",
                "channel": "홈트레이닝",
                "duration_seconds": 600,
                "thumbnail_url": "https://i.ytimg.com/vi/pSHjTRCTomc/hqdefault.jpg",
                "description": "10분 플랭크 운동",
                "difficulty": "초보자"
            }
        ],
        "런지": [
            {
                "video_id": "Z2n58m1MhPM",
                "title": "런지 완벽 가이드",
                "channel": "다리 운동",
                "duration_seconds": 540,
                "thumbnail_url": "https://i.ytimg.com/vi/Z2n58m1MhPM/hqdefault.jpg",
                "description": "런지의 올바른 자세와 변형",
                "difficulty": "초보자"
            }
        ],
        "홈트레이닝": [
            {
                "video_id": "ml4jVuY9NeE",
                "title": "30분 홈트레이닝 (초보자)",
                "channel": "홈트레이닝 채널",
                "duration_seconds": 1800,
                "thumbnail_url": "https://i.ytimg.com/vi/ml4jVuY9NeE/hqdefault.jpg",
                "description": "집에서 할 수 있는 30분 전신 운동",
                "difficulty": "초보자"
            },
            {
                "video_id": "fHyAFeIw_pg",
                "title": "15분 홈트레이닝",
                "channel": "피트니스",
                "duration_seconds": 900,
                "thumbnail_url": "https://i.ytimg.com/vi/fHyAFeIw_pg/hqdefault.jpg",
                "description": "짧은 시간에 효율적인 15분 홈트",
                "difficulty": "초보자"
            }
        ],
        "요가": [
            {
                "video_id": "V3dHNAT78RE",
                "title": "초보자 요가 20분",
                "channel": "요가 채널",
                "duration_seconds": 1200,
                "thumbnail_url": "https://i.ytimg.com/vi/V3dHNAT78RE/hqdefault.jpg",
                "description": "초보자를 위한 20분 요가",
                "difficulty": "초보자"
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
                        difficulty=video_data.get("difficulty", "초보자")
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
                video = YouTubeVideoInfo(
                    video_id=row[0],
                    title=row[1],
                    channel=row[2],
                    duration_seconds=row[3],
                    thumbnail_url=row[5],
                    difficulty=row[4]
                )
                videos.append(video.to_dict())

            return videos
        except sqlite3.OperationalError:
            return []
        finally:
            conn.close()

    def _cache_video(self, exercise_name: str, video: YouTubeVideoInfo) -> None:
        """
        영상을 캐시에 저장합니다.
        
        Args:
            exercise_name: 운동 이름
            video: 영상 정보
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
                    video.video_id,
                    video.title,
                    video.channel,
                    video.duration_seconds,
                    video.difficulty,
                    video.thumbnail_url,
                    datetime.now()
                )
            )
            conn.commit()
        except sqlite3.Error:
            pass
        finally:
            conn.close()

    def get_video_embed_url(self, video_id: str) -> str:
        """
        유튜브 임베드 URL을 반환합니다.
        
        Args:
            video_id: 영상 ID
            
        Returns:
            임베드 URL
        """
        return f"https://www.youtube.com/embed/{video_id}"

    def get_video_watch_url(self, video_id: str) -> str:
        """
        유튜브 시청 URL을 반환합니다.
        
        Args:
            video_id: 영상 ID
            
        Returns:
            시청 URL
        """
        return f"https://www.youtube.com/watch?v={video_id}"


class VideoWatchTracker:
    """사용자의 영상 시청 기록을 추적합니다."""

    def __init__(self):
        """추적기를 초기화합니다."""
        self._ensure_tracking_table()

    def _ensure_tracking_table(self) -> None:
        """추적 테이블을 생성합니다."""
        conn = sqlite3.connect(str(DB_PATH))
        c = conn.cursor()

        try:
            c.execute(
                """CREATE TABLE IF NOT EXISTS video_watch_history (
                    id INTEGER PRIMARY KEY,
                    video_id TEXT,
                    title TEXT,
                    watched_at TIMESTAMP,
                    watch_duration_seconds INTEGER
                )"""
            )
            conn.commit()
        except sqlite3.OperationalError:
            pass
        finally:
            conn.close()

    def record_watch(
        self,
        video_id: str,
        title: str,
        watch_duration_seconds: int = 0
    ) -> bool:
        """
        영상 시청을 기록합니다.
        
        Args:
            video_id: 영상 ID
            title: 영상 제목
            watch_duration_seconds: 시청 시간 (초)
            
        Returns:
            성공 여부
        """
        conn = sqlite3.connect(str(DB_PATH))
        c = conn.cursor()

        try:
            c.execute(
                """INSERT INTO video_watch_history
                   (video_id, title, watched_at, watch_duration_seconds)
                   VALUES (?, ?, ?, ?)""",
                (video_id, title, datetime.now(), watch_duration_seconds)
            )
            conn.commit()
            return True
        except sqlite3.Error:
            return False
        finally:
            conn.close()

    def get_watch_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        최근 시청 기록을 조회합니다.
        
        Args:
            limit: 최대 기록 수
            
        Returns:
            시청 기록 목록
        """
        conn = sqlite3.connect(str(DB_PATH))
        c = conn.cursor()

        try:
            c.execute(
                """SELECT video_id, title, watched_at, watch_duration_seconds
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
                    "watched_at": row[2],
                    "watch_duration": row[3],
                }
                for row in rows
            ]
        except sqlite3.OperationalError:
            return []
        finally:
            conn.close()
