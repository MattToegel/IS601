# Exercise 6

Since we have been discussing debugging, today we're going to analyze some code and see if we can figure out what's going wrong.

Here's our case study:

Alice is designing a prefix notation adding machine.

This machine uses parentheses and the plus sign to designate two arguments to add together.

Arguments must either be integers or another addition operation.

For example:

```lisp
(+ 1 1)          ; <1>
(+ 1 2)          ; <2>
(+ 2 (+ 3 3))    ; <3>
```

1. `<1>` this would yield `2`
2. `<2>` this would yield `3`
3. `<3>` this would yield `8`

You can find Alice's code in the class git repo `exercise_6` directory.

You'll also find it here for reference:

[parser.py](https://raw.githubusercontent.com/MattToegel/IS601/refs/heads/main/exercise_6/parser.py)

Run Alice's program and answer the following questions:

1. **In what function are you getting an error?**

   *Your Answer:*

2. **What function called the function that's giving you an error?**

   *Your Answer:*

3. **How many function calls in total were there before the error occurred?**

   *Your Answer:*

4. **What is the type of error you're getting?**

   *Your Answer:*

5. **Is the error a problem with the parser or its input?**

   *Your Answer:*

6. **If it's an input problem, how would you fix the input?**

   *Your Answer:*

7. **If it's a parser problem, how would you fix the parser?**

   *Your Answer:*

8. **How could you make the parser raise a `ParserError` if this happens again in the future?**

   *Your Answer:*

9. **How many arguments does the addition operation in Alice's machine take?**

   *Your Answer:*
