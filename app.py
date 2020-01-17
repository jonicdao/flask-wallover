from flask import Flask, render_template, redirect, request		# same as before
from flask_sqlalchemy import SQLAlchemy			# instead of mysqlconnection
from sqlalchemy.sql import func                 # ADDED THIS LINE FOR DEFAULT TIMESTAMP
from flask_migrate import Migrate			# this is new

app = Flask(__name__)

# configurations to tell our app about the database we'll be connecting to
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///books_and_authors.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# an instance of the ORM
db = SQLAlchemy(app)

# a tool for allowing migrations/creation of tables
migrate = Migrate(app, db)

books_authors_table = db.Table('books_and_authors', db.Column('authors.id', db.Integer, db.ForeignKey('authors.id'), primary_key=True), db.Column('books.id', db.Integer, db.ForeignKey('books.id'), primary_key=True))


#### ADDING THIS CLASS ####
# the db.Model in parentheses tells SQLAlchemy that this class represents a table in our database

class Book(db.Model):
    __tablename__ = "books"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())
    authors_by_books = db.relationship('Author', secondary=books_authors_table)

class Author(db.Model):
    __tablename__ = "authors"
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    notes = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())
    books_by_author = db.relationship('Book', secondary=books_authors_table)
    
    def full_name(self):
        return self.first_name + " " + self.last_name

# routes go here...

@app.route("/")
def main():
    results = Book.query.all()
    return render_template("main.html", books = results)

@app.route("/authors")
def authors():
    results = Author.query.all()
    return render_template("authors.html", authors = results)

@app.route("/book", methods=['POST'])
def add_book():
    new_book = Book(
        title = request.form['title'],
        description = request.form['description'],
    )
    print("Adding a new book:")
    print(new_book)
    db.session.add(new_book)
    db.session.commit()
    return redirect("/")

@app.route("/books/<id>")
def view_books(id):
    book = Book.query.get(id)
    potential_authors = Author.query.all()
    print(potential_authors, book)
    return render_template("book.html", book=book, authors=potential_authors)

@app.route("/authors/<id>")
def view_authors(id):
    author = Author.query.get(id)
    potential_books = Book.query.all()
    print(potential_books)
    return render_template("author.html", author=author, books=potential_books)

@app.route("/author", methods=["POST"])
def add_author():
    new_author = Author(
        first_name = request.form['first_name'],
        last_name = request.form['last_name'],
        notes = request.form['notes']
    )
    print("adding new author to db:")
    print(new_author)
    db.session.add(new_author)
    db.session.commit()
    return redirect("/authors")

@app.route("/authors_books", methods=["POST"])
def authors_books():
    book = Book.query.get(request.form['book_id'])
    author = Author.query.get(request.form['author_id'])
    print(author, book)
    author.books_by_author.append(book)
    db.session.commit()
    return redirect("/")



if __name__ == "__main__":
    app.run(debug=True)