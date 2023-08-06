# Lord of the Rings (LOTR) SDK

Interact with the [LOTR API](https://the-one-api.dev) in a seamless way.

## First step 

Visit [API Website](https://the-one-api.dev/sign-up) to obtain token necessary for authorization 

## Virtual environment
``` 
mkdir new_project 
cd new_project 
python3 -m venv myvenv 
source myvenv/bin/activate
```

##
.env 
```
API_TOKEN=<your-api-token> 
BASE_URL=https://the-one-api.dev/v2/
```

## Install 
```sh
pip install 
```

### Fetch all books
```sh 
BooksAPI().get_books() 
``` 

### Fetch one book by book ID 
```sh
BooksAPI().get_book(book_id)
```

### Fetch book chapters by book ID
```sh 
BooksAPI().get_book_chapters(book_id)
```

### Fetch book chapters by book ID
```sh 
BooksAPI().get_book_chapters(book_id)
```

### Fetch chapter by chapter ID 
```sh
BooksAPI().get_chapter(chapter_id)
```
___ 

### Adding different params 
```sh 
BooksAPI().get_books(limit=1, page=2, offset=1) 
``` 

___

### Fetch characters 
```sh 
CharactersAPI().get_characters() 
```

### Fetch character 
```sh 
CharactersAPI().get_character(character_id) 
```

### Fetch character quote
```sh 
CharactersAPI().get_characters_quote(character_id) 
```

--- 
Extra params 

### Fetch characters with filters
```sh 
CharactersAPI().get_characters(race="Human", gender="Female", name="Adanel") 
```

___ 
### Fetch movies 

```sh
MoviesAPI().get_movies() 
```

### Fetch movie
```sh
MoviesAPI().get_movie(movie_id) 
```

### Fetch movie quotes
```sh
MoviesAPI().get_movie_quotes(movie_id) 
```

___ 
### Fetch quotes 
```sh 
QuotesAPI().get_quotes() 
``` 

### Fetch quote 
```sh
QuotesAPI().get_quote(quote_id)
```

---

## Running tests 
```sh
python -m pytest -s 
```

