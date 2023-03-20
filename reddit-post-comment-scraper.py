import praw
import time
import csv
import tkinter as tk
from tkinter import Entry, Label
import threading

def reddit_instance(client_id, client_secret, user_agent):
    reddit = praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        user_agent=user_agent
    )
    return reddit

def get_comments(post, max_comments=5):
    post.comment_sort = 'top'
    post.comments.replace_more(limit=None)
    comments = post.comments.list()[:max_comments]
    return [comment.body for comment in comments]

def scrape_subreddit(reddit, subreddit_name, filename):
    subreddit = reddit.subreddit(subreddit_name)

    current_time = int(time.time())
    one_day_ago = current_time - 86400

    all_posts = []

    post_count = 0
    for i, post in enumerate(subreddit.new(limit=100)):
        timestamp = int(post.created_utc)
        if timestamp < one_day_ago:
            break

        post_comments = get_comments(post)
        all_posts.append({
            'title': post.title,
            'url': post.url,
            'timestamp': timestamp,
            'score': post.score,
            'comments': post.num_comments,
            'top_comments': post_comments
        })

        post_count += 1
        progress_label.config(text=f"Scraping progress: {i+1}/{post_count} posts")
        root.update()

    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['title', 'url', 'timestamp', 'score', 'comments', 'top_comments']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for post in all_posts:
            writer.writerow(post)

    progress_label.config(text="Scraping complete!")


def start_scraping():
    subreddit = subreddit_entry.get()
    filename = filename_entry.get()
    if subreddit and filename:
        reddit = reddit_instance("client_id", "client_secret", "username")
        scraper_thread = threading.Thread(target=scrape_subreddit, args=(reddit, subreddit, filename))
        scraper_thread.start()

# Set up GUI
root = tk.Tk()
root.title("Reddit Scraper")

subreddit_label = Label(root, text="Subreddit:")
subreddit_entry = Entry(root)
filename_label = Label(root, text="Output CSV Filename:")
filename_entry = Entry(root)
start_button = tk.Button(root, text="Start Scraping", command=start_scraping)
progress_label = Label(root, text="Scraping progress: 0/0 posts")

subreddit_label.grid(row=0, column=0, padx=(10, 0), pady=(10, 0), sticky="E")
subreddit_entry.grid(row=0, column=1, padx=(0, 10), pady=(10, 0), sticky="W")
filename_label.grid(row=1, column=0, padx=(10, 0), pady=(10, 0), sticky="E")
filename_entry.grid(row=1, column=1, padx=(0, 10), pady=(10, 0), sticky="W")
start_button.grid(row=2, column=0, columnspan=2, pady=(10, 10))
progress_label.grid(row=3, column=0, columnspan=2, pady=(10, 10))

root.mainloop()
