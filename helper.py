# Importing modules
import streamlit as st
from urlextract import URLExtract
from wordcloud import WordCloud
import pandas as pd
from collections import Counter
import emoji

# Object
extract = URLExtract()
def fetch_stats(selected_user,df):
    if selected_user!='Overall':
        df = df[df['User'] == selected_user]
    num_messages = df.shape[0]
    words = []
    for message in df['message']:
        words.extend(message.split())

    # fetch number of media messages
    num_media_messages = df[df['message'] == '<Media omitted>\n'].shape[0]

    #fetch links
    links=[]
    for message in df['message']:
        links.extend(extract.find_urls(message))
    return num_messages, len(words),num_media_messages,len(links)

def most_busy_users(df):
    x = df['user'].value_counts().head()

    # Fix: Apply round() correctly
    df = (df['user'].value_counts() / df.shape[0] * 100).round(2).reset_index()
    df.rename(columns={'index': 'name', 'user': 'percent'}, inplace=True)

    return x, df

# -1 => Negative
# 0 => Neutral
# 1 => Positive

# Will return count of messages of selected user per day having k(0/1/-1) sentiment
def week_activity_map(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df['day_name'].value_counts()

def month_activity_map(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df['month'].value_counts()

def activity_heatmap(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    user_heatmap = df.pivot_table(index='day_name', columns='period', values='message', aggfunc='count').fillna(0)

    return user_heatmap



# Will return count of messages of selected user per date having k(0/1/-1) sentiment
def daily_timeline(selected_user,df,k):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    df = df[df['value']==k]
    # count of message on a specific date
    daily_timeline = df.groupby('only_date').count()['message'].reset_index()
    return daily_timeline


# Will return count of messages of selected user per {year + month number + month} having k(0/1/-1) sentiment
def monthly_timeline(selected_user,df,k):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    df = df[df['value']==-k]
    timeline = df.groupby(['year', 'month_num', 'month']).count()['message'].reset_index()
    time = []
    for i in range(timeline.shape[0]):
        time.append(timeline['month'][i] + "-" + str(timeline['year'][i]))
    timeline['time'] = time
    return timeline

# Will return percentage of message contributed having k(0/1/-1) sentiment
def percentage(df,k):
    df = round((df['user'][df['value']==k].value_counts() / df[df['value']==k].shape[0]) * 100, 2).reset_index().rename(
        columns={'index': 'name', 'user': 'percent'})
    return df

# Return wordcloud from words in message
def create_wordcloud(selected_user,df,k):
    f = open('stop_hinglish.txt', 'r')
    stop_words = f.read()
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    
    # Remove entries of no significance
    temp = df[df['user'] != 'group_notification']
    temp = temp[temp['message'] != '<Media omitted>\n']
    
    # Remove stop words according to text file "stop_hinglish.txt"
    def remove_stop_words(message):
        y = []
        for word in message.lower().split():
            if word not in stop_words:
                y.append(word)
        return " ".join(y)
    # Dimensions of wordcloud
    wc = WordCloud(width=500,height=500,min_font_size=10,background_color='white')
    
    # Actual removing
    temp['message'] = temp['message'].apply(remove_stop_words)
    temp['message'] = temp['message'][temp['value'] == k]
    
    # Word cloud generated
    df_wc = wc.generate(temp['message'].str.cat(sep=" "))
    return df_wc

# Return set of most common words having k(0/1/-1) sentiment
import pandas as pd
from collections import Counter

def most_common_words(selected_user, df, k):
    try:
        # ✅ Load stop words safely
        try:
            with open('stop_hinglish.txt', 'r') as f:
                stop_words = set(f.read().split())  # Use a set for faster lookup
        except FileNotFoundError:
            print("Error: stop_hinglish.txt file not found!")
            return pd.DataFrame()  # Return empty DataFrame

        if selected_user != 'Overall':
            df = df[df['user'] == selected_user]

        # ✅ Ensure 'value' column exists before filtering
        if 'value' not in df.columns:
            print("Error: 'value' column missing in DataFrame")
            return pd.DataFrame()

        # ✅ Remove group notifications and media messages
        temp = df[(df['user'] != 'group_notification') & (df['message'] != '<Media omitted>\n')]

        words = []
        for message in temp[temp['value'] == k]['message']:
            for word in message.lower().split():
                if word not in stop_words:
                    words.append(word)

        # ✅ Creating DataFrame with most common 20 words
        most_common_df = pd.DataFrame(Counter(words).most_common(20), columns=['word', 'count'])

        if most_common_df.empty:
            print(f"Warning: No common words found for sentiment {k}")
            return pd.DataFrame()  # Return empty DataFrame

        return most_common_df

    except Exception as e:
        print(f"Unexpected error in most_common_words(): {e}")
        return pd.DataFrame()



import emoji
import pandas as pd
from collections import Counter

def emoji_helper(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    emojis = []
    for message in df['message']:
        emojis.extend([c for c in message if c in emoji.EMOJI_DATA])  # Extract emojis

    emoji_counts = Counter(emojis).most_common()  # Get all emoji counts

    if len(emoji_counts) > 4:
        top_4 = emoji_counts[:4]  # Get top 4 emojis
        others_count = sum([count for _, count in emoji_counts[4:]])  # Sum of all other emojis

        # Create DataFrame for top 4
        emoji_df = pd.DataFrame(top_4, columns=['emoji', 'count'])

        # Add "Others" category using `pd.concat()`
        others_df = pd.DataFrame([{'emoji': 'Others', 'count': others_count}])
        emoji_df = pd.concat([emoji_df, others_df], ignore_index=True)
    else:
        emoji_df = pd.DataFrame(emoji_counts, columns=['emoji', 'count'])  # Keep all if ≤ 4

    # ✅ Fix: Ensure a DataFrame is always returned
    if emoji_df.empty:
        print("Warning: No emojis found in the dataset.")
        return pd.DataFrame(columns=['emoji', 'count'])  # Return an empty DataFrame

    return emoji_df
