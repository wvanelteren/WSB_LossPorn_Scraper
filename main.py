import praw
import time
from random import sample
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xlsxwriter

reddit = praw.Reddit(
    client_id='bUAYwo47haEZlg',
    client_secret='JRVi-XO2urAJAg41YlsEMgsLcrEVeA',
    user_agent='wsb_lossporn'
)

SUBREDDIT = 'wallstreetbets'
LOSS_POSTS = reddit.subreddit(SUBREDDIT).search('flair:"loss"', sort='new', time_filter='month', limit=250)


# Determines upvote threshold by identifying outliers below the lower whisker of a boxplot
def get_upvote_threshold(posts):
    post_upvote_percentage = []

    for post in posts:
        # 2nd index of post object is the upvote %
        post_upvote_percentage.append(post[2])

    #  creates boxplot if necessary
    plt.boxplot(post_upvote_percentage)
    plt.suptitle('Distribution of Upvote Percentage of WSB Loss Porn Threads')
    plt.ylabel('Upvote Percentage (%)')
    plt.gca().axes.get_xaxis().set_visible(False)
    plt.show()

    # Determine Interquartile Range
    q1 = np.quantile(post_upvote_percentage, 0.25)
    q3 = np.quantile(post_upvote_percentage, 0.75)
    iqr = q3 - q1

    # Formula for determining lower whisker
    lower_whisker = q1 - 1.5 * iqr

    print(f"Upvote threshold for submissions is {lower_whisker}")
    return lower_whisker


# Accesses Reddit API and returns loss-porn posts [Filter: Sort = new, time = since_last_month, amount = 250]
def get_posts():
    posts = []

    for post in LOSS_POSTS:
        posts.append([
            post.title,
            post.score,
            post.upvote_ratio * 100,  # To return the percentage instead of the ratio
            post.num_comments,
            post.selftext,
            'https://www.reddit.com' + post.permalink
        ])

    threshold = get_upvote_threshold(posts)

    # Remove posts from list if post is below the upvote threshold
    for post in posts:
        # 2nd index is the upvote percentage
        if post[2] < threshold:
            posts.remove(post)

    print(len(posts))
    return posts


# Fetches top level comments of the posts fetched from get_posts()
def get_top_level_comments(url):
    post = reddit.submission(url=url)
    post.comments.replace_more(limit=0)

    comments = []

    for top_level_comment in post.comments:
        if not top_level_comment.is_submitter:
            award_cost = 0

            # Getting the cost of gildings from the gildings dic
            gilded = top_level_comment.gildings
            award_cost += 100 * gilded.get('gid_1', 0)  # Silver
            award_cost += 500 * gilded.get('gid_2', 0)  # Gold
            award_cost += 1800 * gilded.get('gid_3', 0)  # Platinum

            # Getting the cost of awards from the awards dic
            for award in top_level_comment.all_awardings:
                award_cost += award.get('coin_price', 0)

            comments.append([
                top_level_comment.author,
                top_level_comment.score,
                award_cost,
                'https://www.reddit.com' + top_level_comment.permalink,
                top_level_comment.body,
            ])

    return comments


def main():
    start_time = time.time()
    writer = pd.ExcelWriter('wsb_loss-porn_tst.xlsx', engine='xlsxwriter')
    num_post_to_select = 100

    # Takes a random sample of all posts that are fetched
    posts = sample(get_posts(), num_post_to_select)
    print(len(posts))

    # Write Posts Dataframe to sheet one
    posts_pd = pd.DataFrame(posts, columns=['Title', 'Score', 'Upvote_%', 'Comments', 'Body', 'url'])
    posts_pd.to_excel(writer, sheet_name='Sheet1')

    # Write top level comments of each post to a different worksheet
    for count, post in enumerate(posts):
        comments = get_top_level_comments(post[5])
        comments_pd = pd.DataFrame(comments, columns=['Author',
                                                      'Score',
                                                      'Award_Score',
                                                      'url',
                                                      'Text'
                                                      ])
        # Sheet 0 does not exist and sheet 1 is reserved for the posts
        comments_pd.to_excel(writer, sheet_name='Sheet' + str(2 + count))

    writer.save()
    print("--- %s seconds ---" % (time.time() - start_time))


if __name__ == "__main__":
    main()
