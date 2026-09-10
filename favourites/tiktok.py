def video_id(link: str) -> str:
    return link.rstrip("/").split("/")[-1]


def embed_url(video_id: str) -> str:
    return f"https://www.tiktok.com/embed/v2/{video_id}"
