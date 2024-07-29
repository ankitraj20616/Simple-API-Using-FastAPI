from fastapi import FastAPI, Path, Query, HTTPException
from typing import Optional
from pydantic import BaseModel, Field
from starlette import status

app = FastAPI()

class Book(BaseModel):
    id: Optional[int]
    title: str
    author: str
    description: str
    rating: float
    published_date: int

class BookRequest(BaseModel):
    id: Optional[int] = Field(description= "Id is not required while creation", default= None)
    title: str = Field(min_length= 3)
    author: str = Field(min_length= 1)
    description: str = Field(min_length= 1, max_length= 100)
    rating: float = Field(gt = 0, lt = 10)
    published_date: int = Field(gt= 1999, lt = 3000)

    model_config = {
        "json_schema_extra": {
            "example": {
                "title" : "A new Book",
                "author" : "Author of this book",
                "description": "A good explaination about the book",
                "rating": 5,
                "published_date" : 2012
            }
        }
    }


books = [Book(id= 1, title= "Title One", author= "Author One", description= "Description One", rating = 6.5, published_date = 2003),
        Book(id= 2, title= "Title Two", author= "Author Two", description= "Description Two", rating = 5, published_date = 2012),
        Book(id= 3, title= "Title Three", author= "Author Three", description= "Description Three", rating = 6, published_date = 2010),
        Book(id= 4, title= "Title Four", author= "Author Four", description= "Description Four", rating = 4, published_date= 2024),
        Book(id= 5, title= "Title Five", author= "Author Five", description= "Description Five", rating = 5, published_date= 2050)]


@app.get("/books", status_code= status.HTTP_200_OK)
async def read_all_books():
    return books

@app.get("/books/{book_id}", status_code = status.HTTP_200_OK)
async def read_by_book_id(book_id: int = Path(gt = 0)):
    books_to_return = []
    for book in books:
        if book.id == book_id:
            books_to_return.append(book)
    if len(books_to_return) == 0:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail= "Entered Id not present!")
    return books_to_return

@app.get("/books/", status_code = status.HTTP_200_OK)
async def read_by_rating(rating: float = Query(gt = 0, lt = 10)):
    books_to_return = [] 
    for book in books:
        if book.rating == rating:
            books_to_return.append(book)
    if len(books_to_return) == 0:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= "No book present of provided rating!")
    return books_to_return

def set_id_of_new_book(new_book: Book):
    if len(books) == 0:
        new_book.id = 1
    else:
        new_book.id = books[-1].id + 1
    return new_book

@app.post("/books/create_book", status_code= status.HTTP_201_CREATED)
async def create_new_book(new_book: BookRequest):
    new_book = Book(**(dict(new_book)))
    new_book = set_id_of_new_book(new_book)
    books.append(new_book)


@app.put("/books/update_book", status_code = status.HTTP_204_NO_CONTENT)
async def update_book(updated_book: BookRequest):
    flag = False
    for i in range(len(books)):
        if books[i].id == updated_book.id:
            books[i] = updated_book
            flag = True
    if flag == False:
        raise HTTPException(status_code = status.HTTP_422_UNPROCESSABLE_ENTITY, details= "Book with provided id is not present in Books list" )
    

@app.delete("/books/delete_book/", status_code = status.HTTP_200_OK)
async def delete_book(book_id: int = Query(gt = 0)):
    for i in range(len(books)):
        if books[i].id == book_id:
            books.pop(i)
            return
    raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, details= "Provided book is not present in book list")