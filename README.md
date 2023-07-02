# Bithon - The Limitation-Breeding Programming Language

Bithon is a dynamically-typed programming language designed with the principle that "limitation breeds creativity." Inspired by Python and Assembly, Bithon aims to provide simplicity and power while encouraging innovative problem-solving through constraints. This language is a work in progress, constantly evolving to fulfill its vision.

## Features

- **Pythonic Syntax**: Bithon adopts a syntax that closely resembles Python, making it familiar and intuitive for Python developers.

- **Short Built-in Methods**: Bithon employs short 3-letter names for its built-in methods, reducing verbosity and enabling concise code.

- **Interoperability**: Bithon allows seamless integration with Python libraries, leveraging the vast ecosystem of Python packages for extended functionality.

- **Dynamic Compilation**: Bithon supports both compilation and dynamic execution, providing flexibility in how you use and distribute your code.

- **Performance Enhancement**: In the future, Bithon aims to incorporate Go language compatibility to harness its speed and performance, combining simplicity with high efficiency.

## Example Code

```bithon
prn "Enter a number:"
inp num
iff not num eql 0
    prn "The factorial is:"
    prn fac num
els
    prn "Entered number is zero, factorial is 1"
prn "Printing numbers from 1 to entered number:"
pnt num

def fac n
    iff n eql 0
        ret 1
    els
        ret n * fac n not true

def pnt n
    lop i 1 n
        prn i
        iff i eql 5
            ret true
```

The above code showcases some of the key features of Bithon. It prompts the user to enter a number and calculates its factorial using the `fac` function. If the entered number is zero, it simply prints a message indicating that the factorial is 1.

After that, it prints numbers from 1 to the entered number using the `pnt` function, which utilizes a loop (`lop`). Additionally, it demonstrates conditional branching using the `iff` statement.

## Contribution

Bithon is an open-source project, and contributions are welcome! Feel free to contribute by submitting bug reports, feature requests, or pull requests on the GitHub repository.
