## Code Highlighting

Python:

```python
def hello(name: str) -> str:
    return f"Hello, {name}!"


if __name__ == "__main__":
    print(hello("world"))
```

JavaScript:

```javascript
const greet = (name) => `Hello, ${name}!`;
console.log(greet("world"));
```

Bash:

```bash
#!/bin/bash
echo "Hello, world!"
for i in $(seq 1 3); do
    echo "Count: $i"
done
```

SQL:

```sql
SELECT id, name FROM users WHERE active = 1 ORDER BY name;
```

No language:

```
plain text block, no highlighting
```
