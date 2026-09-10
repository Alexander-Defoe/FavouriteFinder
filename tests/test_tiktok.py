from favourites.tiktok import embed_url, video_id


def test_video_id_from_the_share_link_stored_in_the_export():
    assert video_id(
        "https://www.tiktokv.com/share/video/7595255804333149470/"
    ) == "7595255804333149470"


def test_video_id_with_a_trailing_slash():
    assert video_id(
        "https://www.tiktok.com/@zachs.foods/video/7595255804333149470/"
    ) == "7595255804333149470"


def test_video_id_with_no_trailing_slash():
    assert video_id(
        "https://www.tiktok.com/@zachs.foods/video/7595255804333149470"
    ) == "7595255804333149470"


def test_video_id_from_a_path_with_no_domain():
    assert video_id("@zachs.foods/video/7595255804333149470") == "7595255804333149470"


def test_embed_url_builds_the_player_address():
    assert embed_url("123") == "https://www.tiktok.com/embed/v2/123"
