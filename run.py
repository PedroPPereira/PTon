"""
no inicio fazer set FLASK_APP=flaskblog.py
inicializar set FLASK_DEBUG=1 para alterar codigo sem reinicializar web server

in cmd db use:
    in python-> from flaskblog import db
    db.create_all()
    from flaskblog import User, Post
    user_1 = User(username='Corey', email='pmpereira@gmail.com', password='pass')
    db.session.add(user_1)
    db.session.commit()

    ex. User.query.all(), User.query.first(), User.query.filter_by(username='Corey').all(),
    user=User.query.filter_by(username='Corey').first(), user.id, user = User.query.get(1)
    post_1= Post(title="blog1", content='Fistff', user_id=user.id)
    db.session.add(post_1)
    db.session.commit()
    post = Post.query.first()
    post.author -> User('Corey', 'pmpereira@gmail.com', 'default.jpg')
    db.drop_all()
"""
from flaskblog import app



if __name__ == '__main__':
    app.run(debug=False)
#
