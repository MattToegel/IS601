import json
books = []
book_id = 0
book ={
    "id": 0,
    "author": "",
    "genre": "",
    "title": "",
    "quantity": 1
}
f = open("myLibrary.json", "r")
data = f.read()
f.close()

books = json.loads(data)
print("Loaded books")
print(books)

while True:
    command = input("What do you want to do?")
    if command == "add":
        title = input("What's the title?").strip()
        author = input("Who wrote it?")
        genre = input("What genere is it?")
        n_book = book.copy()
        n_book["title"] = title
        n_book["author"] = author
        n_book["genre"] = genre
        
        does_exist = False
        for b in books:
            if b["title"].lower() == title.lower():
                b["quantity"] += 1
                does_exist = True
        
        if not does_exist:
            book_id += 1
            n_book["id"] = book_id
            books.append(n_book)
        

        print(n_book)
    elif command == "remove":
        bid = input("What book id do you want to delete?").strip()
        try:
            bid = int(bid)
        except:
            print("Not a number...")
            bid = -1
        for b in books:
            if b["id"] == bid:
                b["quantity"] -= 1
                if b["quantity"] <= 0:
                    books.remove(b)
                    print("removed book")
                else:
                    print("Reduced quantity")

    print(books)
    print(f"There are {len(books)} books")
    f = open("myLibrary.json", "w")
    f.write(json.dumps(books))
    f.close()