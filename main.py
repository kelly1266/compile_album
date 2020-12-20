import praw
import config
from imgurpython import ImgurClient
import datetime
from time import sleep


def respond_to_comment(comment, album_user, album_url, num_images, num_gifs):
    body = "Here is an album of all unique image/gif posts made by " \
           "[{user}]({album_url}). ({num_images} images" \
           ")".format(user=album_user.name, album_url=album_url, num_images=num_images, num_gifs=num_gifs)
    comment.reply(body)
    return


def create_album(user, imgur_client, reddit_client):
    album = imgur_client.create_album({"title": user.name, "privacy": "hidden"})
    urls = []
    images = []
    for submission in reddit_client.redditor(user.name).submissions.top("all"):
        if not submission.is_self and submission.url not in urls:
            urls.append(submission.url)
            try:
                image = imgur_client.upload_from_url(submission.url, config=None, anon=False)
                images.append(image["id"])
                # Sleep command to avoid exceeding rate limit
                # 86400 seconds per day / 12500 requests per day = 1 request every 6.9 seconds
                sleep(8)
            except:
                None
    if len(images) > 0:
        imgur_client.album_add_images(album["id"], images)
    return album["id"]


def update_album(user, imgur_client, reddit_client):
    return


def is_image(url):
    return True


def is_gif(url):
    return True


def run_bot():
    reddit = praw.Reddit(
        client_id=config.CLIENT_ID_REDDIT,
        client_secret=config.SECRET_CODE_REDDIT,
        user_agent=config.USER_AGENT_REDDIT,
        username=config.USERNAME_REDDIT,
        password=config.PASSWORD_REDDIT
    )

    client=ImgurClient(
        client_id=config.CLIENT_ID_IMGUR,
        client_secret=config.SECRET_CODE_IMGUR,
        access_token=config.ACCESS_TOKEN_IMGUR,
        refresh_token=config.REFRESH_TOKEN_IMGUR
    )
    login_time = datetime.datetime.now(datetime.timezone.utc).timestamp()
    print('Bot Initiation Successful')
    print("Logged in at: {time}".format(time = login_time))
    print("Logged into Reddit as: {user}".format(user=reddit.user.me().name))
    print("Logged into Imgur as: {imgur_user}".format(imgur_user=""))
    print("{api_calls} Imgur API calls remaining for the day.".format(api_calls=client.credits["ClientRemaining"]))
    print("----------")
    default_url = "https://imgur.com/"
    command_call = '!compile-album'
    subreddit = reddit.subreddit("all")
    for comment in subreddit.stream.comments():
        if command_call in comment.body and comment.created_utc > login_time:
            parent_id = comment.parent_id
            if parent_id[0:3] == "t1_":
                parent_comment = reddit.comment(id=parent_id[3:])
                album_id = create_album(parent_comment.author, client, reddit)
                album = client.get_album(album_id)
                respond_to_comment(comment, parent_comment.author, album.link, album.images_count, 0)
            elif parent_id[0:3] == "t3_":
                parent_submission = reddit.submission(id=parent_id[3:])
                album_id = create_album(parent_submission.author, client, reddit)
                album = client.get_album(album_id)
                respond_to_comment(comment, parent_submission.author, album.link, album.images_count, 0)


run_bot()