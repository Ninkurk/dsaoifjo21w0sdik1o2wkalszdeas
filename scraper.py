import feedparser
import itertools
import json

def get_top_usernames(subreddit):
    rss_url = f"https://www.reddit.com/r/{subreddit}/hot/.rss"
    feed = feedparser.parse(rss_url)

    usernames = []
    for entry in feed.entries[:10]:  # Limit to top 10 entries
        if 'author' in entry:
            author = entry.author.replace('/u/', '')
            usernames.append(author)

    return usernames

def get_subreddits_from_rss(username):
    rss_url = f"https://www.reddit.com/user/{username}/submitted/.rss"
    feed = feedparser.parse(rss_url)

    subreddits = set()
    for entry in feed.entries:
        if 'category' in entry:
            subreddit = entry.category
            if 'u/' in subreddit:
                continue
            subreddits.add(subreddit)

    return subreddits

def jaccard_similarity(set1, set2):
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    return intersection / union if union != 0 else 0

def get_subreddit_similarity(subreddit):
    top_usernames = get_top_usernames(subreddit)

    user_subreddits = {}
    for username in top_usernames:
        subreddits = get_subreddits_from_rss(username)
        user_subreddits[username] = subreddits

    subreddit_users = {}
    for username, subreddits in user_subreddits.items():
        for sub in subreddits:
            if sub not in subreddit_users:
                subreddit_users[sub] = set()
            subreddit_users[sub].add(username)

    similarity_table = {}
    subreddits = list(subreddit_users.keys())
    for sub1, sub2 in itertools.combinations(subreddits, 2):
        similarity = jaccard_similarity(subreddit_users[sub1], subreddit_users[sub2])
        if sub1 not in similarity_table:
            similarity_table[sub1] = {}
        if sub2 not in similarity_table:
            similarity_table[sub2] = {}
        similarity_table[sub1][sub2] = similarity
        similarity_table[sub2][sub1] = similarity

    return similarity_table

subreddit = input("Subreddit: ")
similarity_data = get_subreddit_similarity(subreddit)

with open('subreddit_similarity.json', 'w') as f:
    json.dump(similarity_data, f, indent=2)

print(f"Similarity data saved to 'subreddit_similarity.json'")
