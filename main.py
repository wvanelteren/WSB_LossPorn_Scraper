import praw
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

reddit = praw.Reddit(
    client_id='bUAYwo47haEZlg',
    client_secret='JRVi-XO2urAJAg41YlsEMgsLcrEVeA',
    user_agent='wsb_lossporn'
)

SUBREDDIT = 'wallstreetbets'
LOSS_POSTS = reddit.subreddit(SUBREDDIT).search('flair:"loss"', sort='new', time_filter='month', limit=250)


# Determines upvote threshold by identifying outliers below the lower whisker of a boxplot
def get_upvote_threshold(posts):
    posts_upvote_ratio = []

    for post in posts:
        # 2nd index of post object is the upvote ratio
        posts_upvote_ratio.append(post[2])

    # creates boxplot if necessary
    # plt.boxplot(posts_upvote_ratio)
    # plt.show()

    # Determine Interquartile Range
    q1 = np.quantile(posts_upvote_ratio, 0.25)
    q3 = np.quantile(posts_upvote_ratio, 0.75)
    iqr = q3-q1

    # Formula for determining lower whisker
    lower_whisker = q1-1.5*iqr

    print(f"Upvote threshold for submissions is {lower_whisker}")
    return lower_whisker


# Accesses Reddit API and returns loss-porn posts [Filter: Sort = new, time = since_last_month, amount = 250]
def get_posts():
    posts = []

    for post in LOSS_POSTS:
        posts.append([
            post.title,
            post.score,
            post.upvote_ratio,
            post.num_comments,
            post.selftext,
            'https://www.reddit.com' + post.permalink
        ])

    threshold = get_upvote_threshold(posts)

    # Remove posts from list if post is below the upvote threshold
    for post in posts:
        # 2nd index is the upvote_ratio
        if post[2] < threshold:
            posts.remove(post)

    return posts


def main():
    posts = get_posts()
    posts = pd.DataFrame(posts, columns=['title', 'score', 'upvote ratio', 'num_comments', 'body', 'url'])
    print(posts)


if __name__ == "__main__":
    main()




