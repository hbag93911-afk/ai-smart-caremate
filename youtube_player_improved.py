#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube 비디오 재생 개선 모듈
Streamlit 환경에서 최적화된 YouTube 비디오 임베드 및 재생 기능을 제공합니다.
"""

import streamlit as st
from typing import Dict, List, Any, Optional
import requests
import json

class YouTubeVideoPlayer:
    """Streamlit에서 최적화된 YouTube 비디오 플레이어"""
    
    # Streamlit에서 작동하는 임베드 방식들
    EMBED_METHODS = {
        'iframe': 'Streamlit iframe (권장)',
        'markdown': 'Streamlit markdown',
        'html': 'Streamlit HTML component',
        'direct_link': 'YouTube 직접 링크'
    }
    
    @staticmethod
    def create_iframe_html(video_id: str, width: int = 100, height: int = 600) -> str:
        """
        안전한 iframe HTML 생성 (Streamlit unsafe_allow_html=True 사용)
        """
        return f'''
        <div style="display:flex;justify-content:center;">
            <iframe 
                width="100%" 
                height="{height}" 
                src="https://www.youtube.com/embed/{video_id}?rel=0&showinfo=0&modestbranding=1" 
                frameborder="0" 
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
                allowfullscreen>
            </iframe>
        </div>
        '''
    
    @staticmethod
    def create_markdown_embed(video_id: str) -> str:
        """
        마크다운으로 비디오 URL 임베드
        """
        return f"https://www.youtube.com/embed/{video_id}"
    
    @staticmethod
    def play_video_in_app(video_id: str, title: str = "", method: str = 'iframe'):
        """
        Streamlit 앱 내에서 비디오 재생
        
        Args:
            video_id: YouTube 비디오 ID
            title: 비디오 제목
            method: 재생 방식 ('iframe', 'markdown', 'html', 'direct_link')
        """
        if title:
            st.markdown(f"### 🎬 {title}")
        
        try:
            if method == 'iframe':
                # 가장 안정적인 방식: 직접 iframe HTML
                html_content = YouTubeVideoPlayer.create_iframe_html(video_id)
                st.markdown(html_content, unsafe_allow_html=True)
                
            elif method == 'markdown':
                # 마크다운 방식 (일부 환경에서 작동 안 할 수 있음)
                embed_url = f"https://www.youtube.com/embed/{video_id}"
                st.markdown(f'<iframe width="100%" height="600" src="{embed_url}" frameborder="0" allowfullscreen></iframe>', 
                           unsafe_allow_html=True)
                
            elif method == 'html':
                # HTML component 방식
                html_content = YouTubeVideoPlayer.create_iframe_html(video_id)
                st.components.v1.html(html_content, height=650)
                
            elif method == 'direct_link':
                # 직접 YouTube 링크
                watch_url = f"https://www.youtube.com/watch?v={video_id}"
                st.link_button("🔗 YouTube에서 보기", watch_url, use_container_width=True)
                
        except Exception as e:
            st.error(f"⚠️ 비디오 재생 오류: {str(e)}")
            st.info("외부 링크에서 시청해주세요.")
            watch_url = f"https://www.youtube.com/watch?v={video_id}"
            st.link_button("🔗 YouTube에서 보기", watch_url, use_container_width=True)
    
    @staticmethod
    def get_fallback_play_methods(video_id: str) -> List[Dict[str, str]]:
        """
        비디오 재생 방법 목록 (우선순위 순)
        """
        return [
            {
                'method': '앱 내 재생 (Iframe)',
                'description': '앱 화면에서 직접 비디오 재생',
                'icon': '🎬',
                'type': 'iframe'
            },
            {
                'method': 'YouTube 외부 링크',
                'description': 'YouTube 웹사이트에서 비디오 시청',
                'icon': '🔗',
                'type': 'direct_link'
            }
        ]

class YouTubeVideoManager:
    """YouTube 비디오 관리 및 검증 클래스"""
    
    @staticmethod
    def validate_video_id(video_id: str) -> Dict[str, Any]:
        """
        비디오 ID 형식 및 접근 가능성 검증
        
        Returns:
            {
                'valid': bool,
                'accessible': bool,
                'playable': bool,
                'embeddable': bool,
                'title': str or None,
                'errors': list,
                'warnings': list
            }
        """
        result = {
            'valid': False,
            'accessible': False,
            'playable': False,
            'embeddable': False,
            'title': None,
            'errors': [],
            'warnings': []
        }
        
        # 1. 형식 검증
        if not video_id or not isinstance(video_id, str):
            result['errors'].append('유효하지 않은 비디오 ID')
            return result
        
        if not (11 <= len(video_id) <= 11):  # YouTube ID는 11자
            if len(video_id) != 11:
                result['warnings'].append(f'예상과 다른 길이: {len(video_id)}자 (일반적으로 11자)')
        
        result['valid'] = True
        
        # 2. 접근 가능성 검증
        try:
            watch_url = f"https://www.youtube.com/watch?v={video_id}"
            embed_url = f"https://www.youtube.com/embed/{video_id}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            # Watch URL 확인
            response = requests.head(watch_url, headers=headers, timeout=5, allow_redirects=True)
            if response.status_code == 200:
                result['accessible'] = True
                result['playable'] = True
            else:
                result['errors'].append(f'Watch URL 접근 불가 (HTTP {response.status_code})')
            
            # Embed URL 확인
            response = requests.head(embed_url, headers=headers, timeout=5)
            if response.status_code == 200:
                result['embeddable'] = True
            else:
                result['warnings'].append('임베드가 제한될 수 있습니다')
                
        except Exception as e:
            result['warnings'].append(f'검증 중 오류: {str(e)}')
        
        return result

def create_video_player_ui(video_id: str, title: str, channel: str, duration_text: str, thumbnail_url: str):
    """
    비디오 플레이어 UI 생성
    """
    col1, col2 = st.columns([1, 2])
    
    with col1:
        try:
            st.image(thumbnail_url, use_column_width=True)
        except:
            st.write("🖼️ 썸네일을 불러올 수 없습니다")
    
    with col2:
        st.markdown(f"**{title}**")
        st.caption(f"채널: {channel}")
        st.caption(f"길이: {duration_text}")
    
    st.divider()
    
    # 재생 옵션
    play_method = st.radio(
        "재생 방식을 선택하세요:",
        options=['iframe', 'direct_link'],
        format_func=lambda x: YouTubeVideoPlayer.EMBED_METHODS.get(x, x),
        horizontal=True
    )
    
    if st.button("▶️ 비디오 재생", use_container_width=True):
        YouTubeVideoPlayer.play_video_in_app(video_id, title, method=play_method)
    
    st.divider()
    
    # 외부 링크
    watch_url = f"https://www.youtube.com/watch?v={video_id}"
    st.link_button("🔗 YouTube에서 새 창으로 열기", watch_url, use_container_width=True)

if __name__ == '__main__':
    # 테스트
    st.title("YouTube 비디오 플레이어 테스트")
    
    video_id = "zkjlJL-aADs"
    title = "올바른 스쿼트 자세 배우기"
    channel = "ThenX"
    duration_text = "7:00"
    thumbnail_url = "https://i.ytimg.com/vi/zkjlJL-aADs/hqdefault.jpg"
    
    create_video_player_ui(video_id, title, channel, duration_text, thumbnail_url)
