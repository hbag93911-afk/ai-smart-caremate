"""YouTube 비디오 재생 가능성 세밀 검사 도구"""

import requests
import urllib.request
import urllib.error
import json
from typing import Dict, List, Any, Tuple
from datetime import datetime
from pathlib import Path

# 등록된 모든 비디오 ID
VIDEOS_TO_CHECK = {
    "스쿼트": ["zkjlJL-aADs", "aClHKpqkqmQ", "xNR3hpx2eQw", "JAgBYcCauNI"],
    "걷기": ["7wAUmQVMFxY", "oD6X0ysX0bA", "yGh7Hxgk-70"],
    "산책": ["Zz_rXjVJqbU"],
    "스트레칭": ["l_7zw2swSnk", "1LvjYbPqMfQ", "g-5bLrGcHmo"],
    "팔 굽혀펴기": ["IODxDxX7oi4", "xsf6nxBg6Ng", "GS4EZ1J2eGc"],
    "플랭크": ["XVNHlPmJcKg", "jRLTdUVH6II", "F9GfzDOhZvw"],
    "런지": ["QOVaHcNveoU", "s40_cQnZxDw"],
    "홈트레이닝": ["tYzlqKqPLM4", "ViKvQy_wqgg", "ml4jVuY9NeE"],
    "요가": ["V3dHNAT78RE", "MKXScXx0HqA"],
    "근력 운동": ["jM92E7YX5GA", "jnHaH6i_0NQ"],
}

class VideoPlaybackChecker:
    """YouTube 비디오 재생 가능성 검사"""
    
    def __init__(self):
        self.results = []
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def check_video_access(self, video_id: str) -> Dict[str, Any]:
        """비디오 접근 가능성 검사"""
        result = {
            "video_id": video_id,
            "url": f"https://www.youtube.com/watch?v={video_id}",
            "embed_url": f"https://www.youtube.com/embed/{video_id}",
            "timestamp": datetime.now().isoformat(),
            "tests": {}
        }
        
        # 1. YouTube 페이지 직접 접근
        result["tests"]["page_access"] = self._test_page_access(video_id)
        
        # 2. 비디오 정보 페이지 접근
        result["tests"]["oembed"] = self._test_oembed(video_id)
        
        # 3. 썸네일 접근
        result["tests"]["thumbnail"] = self._test_thumbnail(video_id)
        
        # 4. 임베드 가능성
        result["tests"]["embed"] = self._test_embed(video_id)
        
        # 5. API를 통한 상태 확인 (oEmbed)
        result["tests"]["oembed_full"] = self._test_oembed_full(video_id)
        
        # 최종 상태 판정
        result["playable"] = self._determine_playability(result)
        
        return result
    
    def _test_page_access(self, video_id: str) -> Dict[str, Any]:
        """YouTube 페이지 접근 테스트"""
        url = f"https://www.youtube.com/watch?v={video_id}"
        try:
            response = requests.head(url, headers=self.headers, timeout=10, allow_redirects=True)
            return {
                "status": "✓" if 200 <= response.status_code < 400 else "✗",
                "status_code": response.status_code,
                "url": response.url,
                "accessible": 200 <= response.status_code < 400
            }
        except Exception as e:
            return {
                "status": "✗",
                "error": str(e),
                "accessible": False
            }
    
    def _test_oembed(self, video_id: str) -> Dict[str, Any]:
        """oEmbed를 통한 비디오 정보 조회"""
        url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return {
                    "status": "✓",
                    "accessible": True,
                    "title": data.get("title"),
                    "author_name": data.get("author_name"),
                    "thumbnail_url": data.get("thumbnail_url")
                }
            elif response.status_code == 404:
                return {
                    "status": "✗",
                    "accessible": False,
                    "error": "Video not found (404)"
                }
            else:
                return {
                    "status": "?",
                    "accessible": None,
                    "status_code": response.status_code
                }
        except Exception as e:
            return {
                "status": "✗",
                "error": str(e),
                "accessible": False
            }
    
    def _test_thumbnail(self, video_id: str) -> Dict[str, Any]:
        """썸네일 접근 테스트"""
        thumbnails = [
            f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg",
            f"https://i.ytimg.com/vi/{video_id}/sddefault.jpg",
            f"https://i.ytimg.com/vi/{video_id}/maxresdefault.jpg",
        ]
        
        for thumb_url in thumbnails:
            try:
                response = requests.head(thumb_url, headers=self.headers, timeout=5)
                if response.status_code == 200:
                    return {
                        "status": "✓",
                        "accessible": True,
                        "url": thumb_url
                    }
            except:
                continue
        
        return {
            "status": "✗",
            "accessible": False,
            "error": "No accessible thumbnail found"
        }
    
    def _test_embed(self, video_id: str) -> Dict[str, Any]:
        """임베드 URL 테스트"""
        url = f"https://www.youtube.com/embed/{video_id}"
        try:
            response = requests.head(url, headers=self.headers, timeout=10)
            return {
                "status": "✓" if 200 <= response.status_code < 400 else "✗",
                "status_code": response.status_code,
                "accessible": 200 <= response.status_code < 400
            }
        except Exception as e:
            return {
                "status": "✗",
                "error": str(e),
                "accessible": False
            }
    
    def _test_oembed_full(self, video_id: str) -> Dict[str, Any]:
        """최대 해상도 oEmbed 테스트"""
        url = f"https://noembed.com/embed?url=https://www.youtube.com/watch?v={video_id}"
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "error" not in data:
                    return {
                        "status": "✓",
                        "accessible": True,
                        "data": data
                    }
                else:
                    return {
                        "status": "✗",
                        "accessible": False,
                        "error": data.get("error")
                    }
            else:
                return {
                    "status": "✗",
                    "accessible": False,
                    "status_code": response.status_code
                }
        except Exception as e:
            return {
                "status": "?",
                "error": str(e),
                "accessible": None
            }
    
    def _determine_playability(self, result: Dict[str, Any]) -> bool:
        """재생 가능성 판정"""
        tests = result["tests"]
        
        # 페이지와 oEmbed가 모두 성공하면 재생 가능
        page_ok = tests.get("page_access", {}).get("accessible", False)
        oembed_ok = tests.get("oembed", {}).get("accessible", False)
        
        return page_ok and oembed_ok
    
    def check_all_videos(self) -> Dict[str, Any]:
        """모든 비디오 검사"""
        print("=" * 80)
        print("YouTube 비디오 재생 가능성 세밀 검사")
        print("=" * 80)
        
        all_results = {}
        total_videos = 0
        playable_count = 0
        
        for category, video_ids in VIDEOS_TO_CHECK.items():
            print(f"\n📂 {category} ({len(video_ids)}개 비디오)")
            print("-" * 80)
            
            category_results = []
            for video_id in video_ids:
                result = self.check_video_access(video_id)
                category_results.append(result)
                total_videos += 1
                
                if result["playable"]:
                    playable_count += 1
                    status_icon = "✅"
                else:
                    status_icon = "❌"
                
                # 간단한 요약 출력
                page_status = result["tests"]["page_access"]["status"]
                oembed_status = result["tests"]["oembed"]["status"]
                embed_status = result["tests"]["embed"]["status"]
                thumb_status = result["tests"]["thumbnail"]["status"]
                
                print(f"  {status_icon} {video_id}")
                print(f"     페이지: {page_status} | oEmbed: {oembed_status} | 임베드: {embed_status} | 썸네일: {thumb_status}")
            
            all_results[category] = category_results
        
        # 최종 요약
        print("\n" + "=" * 80)
        print("최종 요약")
        print("=" * 80)
        print(f"총 비디오: {total_videos}개")
        print(f"재생 가능: {playable_count}개 ({playable_count*100//total_videos}%)")
        print(f"재생 불가: {total_videos - playable_count}개")
        
        # 재생 불가능한 비디오 목록
        if total_videos > playable_count:
            print("\n⚠️ 재생 불가능한 비디오:")
            for category, results in all_results.items():
                for result in results:
                    if not result["playable"]:
                        print(f"  - {category}: {result['video_id']}")
                        print(f"    URL: {result['url']}")
        
        return all_results
    
    def save_report(self, results: Dict[str, Any], filename: str = "video_playback_check.json"):
        """보고서 저장"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_videos": sum(len(v) for v in results.values()),
            "playable_videos": sum(1 for videos in results.values() for v in videos if v["playable"]),
            "results": results
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ 보고서 저장: {filename}")
        return report


if __name__ == "__main__":
    import sys
    import io
    # UTF-8 출력 설정
    if sys.stdout.encoding != 'utf-8':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    checker = VideoPlaybackChecker()
    results = checker.check_all_videos()
    checker.save_report(results)
