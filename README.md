# django-weapp

基于`Django3`和`Django-Rest-Framework`的社交系统

响应分类

1. 信息响应(100–199)
2. 成功响应(200–299)
3. 重定向(300–399)
4. 客户端错误(400–499)
5. 服务器错误 (500–599)

我关注的人

```sql
SELECT * FROM oauth_user WHERE id in (SELECT object_id FROM follows_follow WHERE content_type_id = 6 AND sender_id = 2)
```

```python
instance = User(pk=2)
model = User
through = Follow
target = User
User.objects.filter(
    pk__in=Follow.objects.filter(
        content_type=ContentType.objects.get_for_model(target),
        sender=instance
    ).values('object_id)
)
```

关注我的人

```sql
SELECT * FROM oauth_user WHERE id in (SELECT sender_id FROM follows_follow WHERE content_type_id = 6 AND object_id = 2)
```

```python
instance = User(pk=2)
model = User
through = Follow
target = User
User.objects.filter(
    pk__in=Follow.objects.filter(
        content_type=ContentType.objects.get_for_model(model),
        object_id=instance.pk
    ).values('sender_id')
)
```

收藏夹下收藏的文章

```sql
SELECT * FROM weblog_article WHERE id in (SELECT object_id FROM collects_collect WHERE content_type_id = 6 AND sender_id = 2)
```

```python
instance = Collection(pk=2)
model = Collection
through = Collect
target = Article
Article.objects.filter(
    pk__in=Collect.objects.filter(
        content_type=ContentType.objects.get_for_model(target),
        sender=instance
    ).values('object_id')
)
```

文章被哪些收藏夹收藏

```sql
SELECT * FROM collection WHERE id in (SELECT sender_id FROM collects_collect WHERE content_type_id = 6 AND object_id = 2)
```

```python
instance = Article(pk=2)
model = Article
through = Collect
target = Collection
Collection.objects.filter(
    pk__in=Collect.objects.filter(
        content_type=ContentType.objects.get_for_model(model),
        object_id=instance.pk
    ).values('sender_id')
)
```

收藏夹被哪些人喜欢

```sql
SELECT * FROM oauth_user WHERE id in (SELECT sender_id FROM likes_like WHERE content_type_id = 6 AND object_id = 2)
```

```python
instance = Collection(pk=2)
model = Collection
through = Like
target = User
User.objects.filter(
    pk__in=Like.objects.filter(
        content_type=ContentType.objects.get_for_model(model),
        object_id=instance.pk
    ).values('sender_id')
)
```

我喜欢的收藏夹
```sql
select * from collection where id in (select object_id from likes_like where content_type_id = 6 and sender_id = 2)
```

```python
instance = User(pk=2)
model = User
through = Like
target = Collection
Collection.objects.filter(
    pk__in=Like.objects.filter(
        content_type=ContentType.objects.get_for_model(target),
        sender=instance
    ).values('object_id')
)
```

收藏夹被哪些人关注
```sql
select * from oauth_user where id in (select sender_id from follows_follow where content_type_id = 6 and object_id = 2)
```

```python
instance = Collection(pk=2)
model = Collection
through = Follow
target = User
User.objects.filter(
    pk__in=Like.objects.filter(
        content_type=ContentType.objects.get_for_model(model),
        object_id=instance.pk
    ).values('sender_id')
)
```

我关注的收藏夹
```sql
select * from collection where id in (select object_id from follows_follow where content_type_id =6 and sender_id = 2)
```

```python
instance = User(pk=2)
model = User
through = Follow
target = Collection
Collection.objects.filter(
    pk__in=Follow.objects.filter(
        content_type=ContentType.objects.get_for_model(target),
        sender=instance
    ).values('object_id')
)
```

评论被哪些人喜欢

```sql
select * from oauth_user where id in (select sender_id from likes_like where content_type_id = 6  and object_id = 2)
```

```python
instance = Comment(pk=2)
model = Comment
through = Like
target = User
User.objects.filter(
    pk__in=Like.objects.filter(
        content_type=ContentType.objects.get_for_model(model),
        object_id=instance.pk
    ).values('sender_id')
)

```

我喜欢的评论
```sql
select * from comments_comment where id in (select object_id from likes_like where content_type_id = 6 and sender_id = 2)
```

```python
instance = User(pk=2)
model = User
through = Like
target = Comment
Comment.objects.filter(
    pk__in=Like.objects.filter(
        content_type=ContentType.objects.get_for_model(target),
        sender=instance
    ).values('object_id')
)
```

文章被哪些人喜欢
```sql
select * from oauth_user where id in (select sender_id from likes_like where content_type_id = 6 and object_id = 2)
```

```python
instance = Article(pk=2)
model = Article
through = Like
target = User
User.objects.filter(
    pk__in=Like.objects.filter(
        content_type=ContentType.objects.get_for_model(model),
        object_id=instance.pk
    ).values('sender_id')
)

```

我喜欢的文章
```sql
select * from article where id in (select object_id from likes_like where content_type_id = 6 and sender_id = 2)
```

```python
instance = User(pk=2)
model = User
through = Like
target = Article
Article.objects.filter(
    pk__in=Like.objects.filter(
        content_type=ContentType.objects.get_for_model(target),
        sender=instance
    ).values('object_id')
)
```

想法被哪些人喜欢
```sql
select * from oauth_user where id in (select sender_id from likes_like where content_type_id = 6 and object_id = 2)
```

```python
instance = Pin(pk=2)
model = Pin
through = Like
target = User
User.objects.filter(
    pk__in=Like.objects.filter(
        content_type=ContentType.objects.get_for_model(model),
        object_id=instance.pk
    ).values('sender_id')
)

```

我喜欢的想法
```sql
select * from pin where id in (seletc object_id from likes_like where content_type_id = 6 and sender_id = 2)
```

```python
instance = User(pk=2)
model = User
through = Like
target = Pin
Pin.objects.filter(
    pk__in=Like.objects.filter(
        content_type=ContentType.objects.get_for_model(target),
        sender=instance
    ).values('object_id')
)
```

想法被哪些收藏夹收藏
```sql
select * from collection where id in (select sender_id from collects_collect where content_type_id = 6 and object_id = 2)
```

```python
instance = Pin(pk=2)
model = Pin
through = Collect
target = Collection
Collection.objects.filter(
    pk__in=Collect.objects.filter(
        content_type=ContentType.objects.get_for_model(model),
        object_id=instance.pk
    ).values('sender_id')
)

```

收藏夹下收藏的想法
```sql
select * from pin where id in (select object_id from collects_collect where content_type_id = 6 and sender_id = 2)
```

```python
instance = Collection(pk=2)
model = Collection
through = Collect
target = Pin
Pin.objects.filter(
    pk__in=Collect.objects.filter(
        content_type=ContentType.objects.get_for_model(target),
        sender=instance
    ).values('object_id')
)
```

分类被哪些人关注
```sql
select * from oauth_user where id in (select sender_id from follows_follow where content_type_id = 6 and object_id = 2)
```

```python
instance = Category(pk=2)
model = Category
through = Follow
target = User
User.objects.filter(
    pk__in=Follow.objects.filter(
        content_type=ContentType.objects.get_for_model(model),
        object_id=instance.pk
    ).values('sender_id')
)

```

我关注的分类
```sql
select * from category where id in (select object_id from follows_follow where content_type_id = 6 and sender_id = 2)
```

```python
instance = User(pk=2)
model = user
through = Follow
target = Category
Category.objects.filter(
    pk__in=Follow.objects.filter(
        content_type=ContentType.objects.get_for_model(target),
        sender=instance
    ).values('object_id')
)
```

话题被哪些人关注
```sql
select * from oauth_user where id in (select sender_id from follows_follow where content_type_id = 6 and object_id 2)
```

```python
instance = Topic(pk=2)
model = Topic
through = Follow
target = User
User.objects.filter(
    pk__in=Follow.objects.filter(
        content_type=ContentType.objects.get_for_model(model),
        object_id=instance.pk
    ).values('sender_id')
)

```

我关注的话题
```sql
select * from topic where id in (select object_id from follows_follow where content_type_id = 6 and sender_id = 2)
```

```python
instance = User(pk=2)
model = user
through = Follow
target = Topic
Topic.objects.filter(
    pk__in=Follow.objects.filter(
        content_type=ContentType.objects.get_for_model(target),
        sender=instance
    ).values('object_id')
)
```
