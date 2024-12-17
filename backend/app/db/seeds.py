print('Please fill the seeds file')

import os
import psycopg2
from functools import wraps
from faker import Faker
from random import randint

database_url = os.environ['DATABASE_URL'].replace("postgres://", "postgresql://")

def db_connection(func):
    """Decorator for managing a database connection."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        connection = None
        cursor = None
        try:
            # Establish connection
            connection = psycopg2.connect(database_url)
            cursor = connection.cursor()
            
            # Pass connection and cursor to the wrapped function
            result = func(*args, connection=connection, cursor=cursor, **kwargs)
            
            # Commit the transaction
            connection.commit()
            
            return result
        except Exception as e:
            if connection:
                connection.rollback()  # Rollback transaction on error
            print(f"Database error: {e}")
            raise
        finally:
            # Close the cursor and connection
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    return wrapper

@db_connection
def get_users(connection=None, cursor=None):
    """Retrieve all users"""
    query = "SELECT * FROM users;"
    cursor.execute(query)
    users = cursor.fetchall()
    return users

@db_connection
def insert_item(slug, title, description, image, seller_id, connection=None, cursor=None):
    """Insert one item"""
    query = """
    INSERT INTO items (slug, title, description, image, seller_id)
    VALUES (%s, %s, %s, %s, %s)
    RETURNING id;
    """
    cursor.execute(query, (slug, title, description, image, seller_id))
    item = cursor.fetchone()
    print(f"Added item: {item}")
    return item

@db_connection
def insert_user(username, email, bio, image, salt, connection=None, cursor=None):
    """Insert one user"""
    query = """
    INSERT INTO users (username, email, bio, image, salt)
    VALUES (%s, %s, %s, %s, %s)
    RETURNING id;
    """
    cursor.execute(query, (username, email, bio, image, salt))
    user = cursor.fetchone()
    print(f"Added user: {user}")
    return user

@db_connection
def insert_users(users, connection=None, cursor=None):
    """Insert many users"""
    query = """
    INSERT INTO users (username, email, bio, image, salt)
    VALUES (%s, %s, %s, %s, %s)
    RETURNING id;
    """
    cursor.executemany(query, users)
    print(f"Inserted {cursor.rowcount} users successfully!")

@db_connection
def insert_items(items, connection=None, cursor=None):
    """Insert many items"""
    query = """
    INSERT INTO items (slug, title, description, image, seller_id)
    VALUES (%s, %s, %s, %s, %s)
    RETURNING id;
    """
    cursor.executemany(query, items)
    print(f"Inserted {cursor.rowcount} items successfully!")

@db_connection
def insert_comment(body, seller_id, item_id, connection=None, cursor=None):
    """Insert one comment"""
    query = """
    INSERT INTO comments (body, seller_id, item_id)
    VALUES (%s, %s, %s)
    RETURNING id;
    """
    cursor.execute(query, (body, seller_id, item_id))
    comment = cursor.fetchone()
    print(f"Added comment: {comment}")
    return comment

@db_connection
def insert_comments(comments, connection=None, cursor=None):
    """Insert many comments"""
    query = """
    INSERT INTO comments (body, seller_id, item_id)
    VALUES (%s, %s, %s)
    RETURNING id;
    """
    cursor.executemany(query, comments)
    print(f"Inserted {cursor.rowcount} comments successfully!")

@db_connection
def get_objects(table_name, connection=None, cursor=None):
    # Execute the SELECT query
    query = f"SELECT * FROM {table_name};"
    cursor.execute(query)

    # Fetch all rows
    objects = cursor.fetchall()

    # Print the results
    for object in objects:
        print(object)
    print(f"number of objects: {cursor.rowcount}")

@db_connection
def get_item_min_id(connection=None, cursor=None):
    # Execute the SELECT query
    query = "SELECT MIN(id) FROM items;"
    cursor.execute(query)

    min_id = cursor.fetchone()[0]
    return min_id

def generate_items(n):
    items = []
    for i in range(1, n+1):
        item = f'{Faker().word()}{i}'
        items.append((
            f'fakeitem-{item}',  # slug
            f'Fake Item {item}',  # title
            'test description',  # description
            f'https://picsum.photos/200/300', # image
            i  # seller_id 
        )) 
    return items

def generate_users(n):
    users = []
    for i in range(1, n+1):
        username = f'{Faker().user_name()}{i}'
        users.append((
            username,  # username
            f'{username}@anythink.com',  # email
            'test bio',  # bio
            f'https://placedog.net/{randint(1,500)}',  # image
            Faker().password()  # salt
        ))
    return users

def generate_comments(min_id, n):
    comments = [(
    f'this is a test comment no. {i}',  # body
    i,  # seller_id
    (min_id-1+i)  # item_id
    ) for i in range(1, n+1)]
    return comments

def main():
    # insert_item('added-item', 'added item', 'description', 'https://picsum.photos/id/3/200/300', 1)
    # insert_user('test user', 'testuser@anythink.com', 'test bio', 'https://placedog.net/109', 'salt')
    # insert_comment('test comment', 1, 2)

    users = generate_users(100)
    insert_users(users)

    items = generate_items(100)
    insert_items(items)

    min_item_id = get_item_min_id()
    comments = generate_comments(min_item_id, 100)
    insert_comments(comments)

if __name__ == "__main__":
    main()

