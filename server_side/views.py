from django.shortcuts import render
from django.contrib import messages

from .services.youtube_search_and_download import search, download_mp3

def add_song(request):

    results = []
    query = ""

    if request.method == "POST":
        action = request.POST.get("action")
        query = request.POST.get("q", "").strip()

        if action == "search" and query:
            try:
                results = search(query)
            except Exception as e:
                messages.error(request, f"Search failed {e}")

        elif action == "download":
            url = request.POST.get("url")
            if url: 
                try:
                    meta = download_mp3(url)

                    messages.success(
                        request,
                        f"Downloaded: {meta['title']} -> {meta['path']}"
                    )
                except Exception as e:
                    messages.error(request, f"Download Failed {e}")

    return render(request, 'add_song_section.html', {
        "results": results,
        "query": query,
    })


def home(request):
    return render(request, 'home_page.html')