<h1 align="center"> arrmovs </h1> <br>

With this package, you can convert your INT to array and on the contrary

<h2>instalation </h2> <br>

Ar first, let's install our package:

```python
pip install arrmovs
```

or you can use:

```python
pip3 install arrmovs
```

<h2>Convert INT to the array</h2> <br>

Let's convert our INT to array and print it:

```python
import arrmovs as arr

num = 12345
myArr = arr.IntToArr(num)

print(myArr)
```

After that, let's convert our INT to an array, but sort it:

```python
import arrmovs as arr

num = 12345
myArr = arr.IntToArrSorted(num)
```

<h2>Convert Array to INT</h2> <br>

If we have an array and we want to convert it to an INT, we can use the module ArrToInt:

```python
import arrmovs as arr

myArr = arr.IntToArrRandom(1, 10)
num = arr.ArrToInt(myArr)
```