from flask import Flask, render_template, redirect, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.sql import func

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///books_authors.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db=SQLAlchemy(app)
migrate=Migrate(app, db)

books_authors_table=db.Table('books_authors',
                db.Column('authors_id', db.Integer, db.ForeignKey('authors.id'), primary_key=True),
                db.Column('books_id', db.Integer, db.ForeignKey('books.id'), primary_key=True))

class Book(db.Model):
    __tablename__="books"
    id=db.Column(db.Integer, primary_key=True)
    title=db.Column(db.String(100))
    description=db.Column(db.String(140))
    books_authors=db.relationship("Author", secondary=books_authors_table)
    created_at=db.Column(db.DateTime, server_default=func.now())
    updated_at=db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())

class Author(db.Model):
    __tablename__ = "authors"
    id=db.Column(db.Integer, primary_key=True)
    first_name=db.Column(db.String(100))
    last_name=db.Column(db.String(100))
    notes=db.Column(db.Text)
    authors_books=db.relationship("Book", secondary=books_authors_table)
    created_at=db.Column(db.DateTime, server_default=func.now())
    updated_at=db.Column(db.DateTime, server_default=func.now(),onupdate=func.now())

@app.route("/")
def main():
    book_list=Book.query.all()
    return render_template("main.html", books=book_list)

@app.route("/authors")
def authors():
    author_list=Author.query.all()
    return render_template("authors.html", authors=author_list)

@app.route("/books/<id>")
def book(id):
    print('got here')
    book=Book.query.get(id)
    potential_authors = Author.query.all()
    return render_template("book.html", book=book, authors=potential_authors)

@app.route("/authors/<id>")
def author(id):
    author = Author.query.get(id)
    potential_books = Book.query.all()
    return render_template("author.html", author=author, books=potential_books)

@app.route("/author", methods=["POST"])
def add_author():
    new_author = Author(
        first_name=request.form['first_name'],
        last_name=request.form['last_name'],
        notes=request.form['notes']
    )
    db.session.add(new_author)
    db.session.commit()
    return redirect("/authors")

@app.route("/book", methods=["POST"])
def add_book():
    new_book=Book(
        title=request.form['title'],
        description=request.form["description"]
    )
    db.session.add(new_book)
    db.session.commit()
    return redirect("/")

@app.route("/authors_books", methods=["POST"])
def add_author_book():
    author=Author.query.get(request.form['author_id'])
    book=Book.query.get(request.form['book_id'])
    print(author, book)
    author.authors_books.append(book)
    db.session.commit()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)