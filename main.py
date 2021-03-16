import praw
import matplotlib.pyplot as plt
import numpy as np

reddit = praw.Reddit(
    client_id='bUAYwo47haEZlg',
    client_secret='JRVi-XO2urAJAg41YlsEMgsLcrEVeA',
    user_agent='wsb_lossporn'
)

subreddit = 'wallstreetbets'
loss_posts = reddit.subreddit(subreddit).search('flair:"loss"', sort='new', time_filter='month', limit=250)


# Determines upvote threshold by identifying outliers below the lower whisker of a boxplot
def get_upvote_threshold():
    posts_upvote_ratio = []

    for post in loss_posts:
        posts_upvote_ratio.append(post.upvote_ratio)

    # creates boxplot if necessary
    plt.boxplot(posts_upvote_ratio)
    plt.show()

    # Determine Interquartile Range
    q1 = np.quantile(posts_upvote_ratio, 0.25)
    q3 = np.quantile(posts_upvote_ratio, 0.75)
    iqr = q3-q1

    # Formula for determining lower whisker
    lower_whisker = q1-1.5*iqr

    print(f"Upvote threshold for submissions is {lower_whisker}")
    return lower_whisker


get_upvote_threshold()











