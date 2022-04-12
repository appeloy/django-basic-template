class PostSerializer():
    def __init__(self, object):
        self.id = object.id
        self.title = object.title
        self.content = object.content
        self.date_posted = object.date_posted
        self.author = object.author.username
        self.author_pic = object.author.profile.image.url,

    def as_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "date_posted": self.date_posted,
            "author": self.author,
            "author_pic":self.author_pic,
        }