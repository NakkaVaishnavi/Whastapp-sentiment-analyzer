import re
import pandas as pd

def preprocess(data):
    # ✅ Try matching both 12-hour and 24-hour formats
    pattern = r'\d{1,2}/\d{1,2}/\d{2}, \d{1,2}:\d{2}(?:\s?[APMapm]{2})?'

    # ✅ Extract messages and dates
    messages = re.split(pattern, data)[1:]
    dates = re.findall(pattern, data)

    if not messages or not dates or len(messages) != len(dates):
        print("🔴 Debugging: Data Format Mismatch")
        print("First few lines of input:\n", data[:500])  # Print first 500 characters of the file
        raise ValueError("Error in splitting messages and dates. Check input format.")

    # ✅ Create DataFrame
    df = pd.DataFrame({'user_message': messages, 'message_date': dates})

    # ✅ Correct Date Parsing
    df['message_date'] = pd.to_datetime(df['message_date'], format='%d/%m/%y, %H:%M', errors='coerce')

    # ✅ Rename column
    df.rename(columns={'message_date': 'date'}, inplace=True)

    # ✅ Extract user and message
    users, messages = [], []
    for message in df['user_message']:
        entry = re.split('([\w\W]+?):\s', message)
        if entry[1:]:
            users.append(entry[1])
            messages.append(" ".join(entry[2:]))
        else:
            users.append('group_notification')
            messages.append(entry[0])

    df['user'] = users
    df['message'] = messages

    # ✅ Drop original column
    df.drop(columns=['user_message'], inplace=True)

    # ✅ Extract time-based features
    df['only_date'] = df['date'].dt.date
    df['year'] = df['date'].dt.year
    df['month_num'] = df['date'].dt.month
    df['month'] = df['date'].dt.month_name()
    df['day'] = df['date'].dt.day
    df['day_name'] = df['date'].dt.day_name()
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute

    # ✅ Fix Period Calculation
    df['period'] = df['hour'].astype(str) + "-" + (df['hour'] + 1).astype(str)

    # ✅ Remove group notifications
    df = df[df['user'] != 'group_notification']

    return df
