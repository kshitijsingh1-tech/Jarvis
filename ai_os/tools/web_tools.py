
from ddgs import DDGS
from youtubesearchpython import VideosSearch

def search_web(query: str, max_results: int = 5) -> str:
    """
    Performs a web search using DuckDuckGo.
    Returns a formatted string of results.
    """
    try:
        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                results.append(f"Title: {r['title']}\nLink: {r['href']}\nSnippet: {r['body']}\n")
        
        if not results:
            return "No results found."
        
        return "\n---\n".join(results)
    except Exception as e:
        return f"Error during web search: {str(e)}"

def search_youtube(query: str, max_results: int = 5) -> str:
    """
    Performs a YouTube video search.
    Returns a formatted string of results.
    """
    try:
        videos_search = VideosSearch(query, limit=max_results)
        results = videos_search.result()
        
        formatted_results = []
        for video in results.get('result', []):
            title = video.get('title')
            link = video.get('link')
            duration = video.get('duration')
            view_count = video.get('viewCount', {}).get('short')
            formatted_results.append(f"Title: {title}\nLink: {link}\nDuration: {duration}\nViews: {view_count}\n")
            
        if not formatted_results:
            return "No YouTube results found."
            
        return "\n---\n".join(formatted_results)
    except Exception as e:
        return f"Error during YouTube search: {str(e)}"
