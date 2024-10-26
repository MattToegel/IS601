---

# Exercise 6

Since we have been discussing debugging, today we're going to analyze some code and see if we can figure out what's going wrong.

Here's our case study:

Alice is designing a prefix notation adding machine.

This machine uses parentheses and the plus sign to designate two arguments to add together.

Arguments must either be integers or another addition operation.

For example:

```lisp
(+ 1 1)          ; (1)
(+ 1 2)          ; (2)
(+ 2 (+ 3 3))    ; (3)
```

1. `<1>` this would yield `2`
2. `<2>` this would yield `3`
3. `<3>` this would yield `8`

You can find Alice's code in the class git repo `exercise_6` directory.

You'll also find it here for reference:

[parser.py](https://raw.githubusercontent.com/MattToegel/IS601/refs/heads/main/exercise_6/parser.py)

Run Alice's program and answer the following questions:

1. **In what function are you getting an error?**

   *Answer:* The error occurs in the `get_argument` function. This function tries to parse each argument, which can be either an integer or a nested operation, but it fails when it encounters an invalid character (`F`) that cannot be converted to an integer. Here’s the function:

   ```python
   def get_argument(text):
       start_index = None
       for index, character in enumerate(text):
           if character == '(':
               # Recursively call perform_operation for nested operations
               arg, remaining_text = perform_operation(text[index + 1:])
               return arg, remaining_text
           elif character != ' ' and start_index == None:
               start_index = index
           elif (character == ' ' or character == ')') and start_index != None:
               # Attempt to convert the identified substring to an integer
               arg = int(text[start_index:index])
               remaining_text = text[index + 1:]
               return arg, remaining_text
       raise ParserException("Unable to get argument")
   ```

2. **What function called the function that's giving you an error?**

   *Answer:* The function `perform_operation` called `get_argument`. `perform_operation` retrieves two arguments by calling `get_argument` twice. In this case, `get_argument` encounters `F` and tries to convert it to an integer, leading to a `ValueError`.

   Here’s the code for `perform_operation`:

   ```python
   def perform_operation(text):
       if text[0] == '+':
           # Attempt to get the first argument
           arg1, remaining_text = get_argument(text[1:])
           # Attempt to get the second argument
           arg2, remaining_text = get_argument(remaining_text)
           # Return the sum of the two arguments
           return arg1 + arg2, remaining_text
       else:
           raise ParserException("Invalid operation")
   ```

3. **How many function calls in total were there before the error occurred?**

   *Answer:* There were four function calls in total before the error occurred:
   - `find_open_parenthesis` – finds the starting point for parsing.
   - `perform_operation` (top-level) – initiates the addition operation.
   - `get_argument` (within `perform_operation`) – retrieves the first argument.
   - `perform_operation` (nested) – handles the nested operation, which leads to another call to `get_argument`, where the error occurs.

4. **What is the type of error you're getting?**

   *Answer:* The type of error is a `ValueError`. This happens when `get_argument` encounters `F` and attempts to convert it to an integer. Since `F` is not a valid integer, the `int()` function raises a `ValueError`.

5. **Is the error a problem with the parser or its input?**

   *Answer:* The error is an input problem. The parser expects valid integers for each argument, but the input contains `F`, which cannot be interpreted as an integer. Thus, the input does not meet the parser's requirements for valid arguments.

6. **If it's an input problem, how would you fix the input?**

   *Answer:* To fix the input, replace `F` with a valid integer so the parser can process the expression. For example:

   ```python
   text = "(+ (+ 1 2) (+ (+ 3 4) 5))"
   ```

   This modified input has `4` instead of `F`, allowing the parser to successfully process the addition.

7. **If it's a parser problem, how would you fix the parser?**

   *Answer:* If we want to make the parser more robust, we can add a check in `get_argument` to ensure it only attempts to convert arguments that are valid integers. We could modify `get_argument` to raise a `ParserException` if it encounters a non-integer character that cannot be parsed. Here’s an improved version of `get_argument`:

   ```python
   def get_argument(text):
       start_index = None
       for index, character in enumerate(text):
           if character == '(':
               # Handle nested operations
               arg, remaining_text = perform_operation(text[index + 1:])
               return arg, remaining_text
           elif character != ' ' and start_index is None:
               start_index = index
           elif (character == ' ' or character == ')') and start_index is not None:
               try:
                   # Convert substring to integer and catch any conversion errors
                   arg = int(text[start_index:index])
               except ValueError:
                   raise ParserException(f"Invalid argument: '{text[start_index:index]}' is not an integer.")
               remaining_text = text[index + 1:]
               return arg, remaining_text
       raise ParserException("Unable to get argument")
   ```

8. **How could you make the parser raise a `ParserError` if this happens again in the future?**

   *Answer:* Modify `get_argument` to catch any `ValueError` when attempting to convert to an integer and raise a `ParserException` instead. This would prevent a crash and make it clear to the user that the input contains an invalid argument. This improvement was implemented in the previous question’s solution. If `get_argument` encounters a non-integer, it raises a `ParserException` with a message indicating the issue.

9. **How many arguments does the addition operation in Alice's machine take?**

   *Answer:* The addition operation in Alice's machine takes exactly two arguments. Each `+` operation expects two numbers or nested operations as arguments.

---
