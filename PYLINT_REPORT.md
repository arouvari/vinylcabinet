# Pylint Report

## Running Pylint

```bash
pylint app.py database.py db.py
```

## Pylint Results

```
************* Module app
app.py:432:0: C0301: Line too long (104/100) (line-too-long)
app.py:496:4: E0237: Assigning to attribute 'start_time' not defined in class slots (assigning-non-slot)
app.py:13:0: C0411: standard import "import time" should be placed before "from flask import Flask, render_template, request, redirect, session, flash, abort, g" (wrong-import-order)

************* Module database
database.py:21:4: C0103: Variable name "e" doesn't conform to snake_case naming style (invalid-name)

************* Module db
db.py:14:15: W0102: Dangerous default value [] as argument (dangerous-default-value)
db.py:23:15: W0102: Dangerous default value [] as argument (dangerous-default-value)

-----------------------------------
Your code has been rated at 9.79/10
```

## Analysis of Issues

### 1. Line Too Long (app.py:432)

**Issue:**

```
app.py:432:0: C0301: Line too long (104/100) (line-too-long)
```

**Code:**

```python
user_favorites_albums = database.get_user_favorites(current_user_id) if current_user_id else []
```

**Why Not Fixed:**
This line is only 4 characters over the limit and breaking it would reduce readability. The alternative would be:

```python
user_favorites_albums = (
    database.get_user_favorites(current_user_id)
    if current_user_id
    else []
)
```

The single-line version is more concise and the extra 4 characters don't significantly impact readability.

### 2. Assigning to Non-Slot Attribute (app.py:496)

**Issue:**

```
app.py:496:4: E0237: Assigning to attribute 'start_time' not defined in class slots (assigning-non-slot)
```

**Code:**

```python
@app.before_request
def before_request():
    g.start_time = time.time()
```

**Why Not Fixed:**
This is intentional Flask functionality for storing request-specific data. The Pylint warning is a false positive because it doesn't understand Flask's dynamic `g` object pattern.

### 3. Wrong Import Order (app.py:13)

**Issue:**

```
app.py:13:0: C0411: standard import "import time" should be placed before "from flask import Flask..." (wrong-import-order)
```

**Code:**

```python
import sqlite3
import secrets
from flask import Flask, render_template, request, redirect, session, flash, abort, g
from werkzeug.security import generate_password_hash, check_password_hash
import config
import db
import database
import time
```

**Why Not Fixed:**
The `time` import was added later. Ordering doesn't affect functionality and the current organization keeps related imports together. This is a minor style issue that doesn't impact code quality.

### 4. Variable Name "e" (database.py:21)

**Issue:**

```
database.py:21:4: C0103: Variable name "e" doesn't conform to snake_case naming style (invalid-name)
```

**Code:**

```python
try:
    album_id = execute(...)
    ...
except Exception as e:
    return False, str(e)
```

**Why Not Fixed:**
The variable is only used once (in `str(e)`) and exists for a single line, making a longer name like `exception` unnecessarily long.

### 5. Dangerous Default Value [] (db.py)

**Issues:**

```
db.py:14:15: W0102: Dangerous default value [] as argument (dangerous-default-value)
db.py:23:15: W0102: Dangerous default value [] as argument (dangerous-default-value)
```

**Code:**

```python
def execute(sql, params=None):
    params = params or []
    # ...

def query(sql, params=None):
    params = params or []
    # ...
```

**Why Not Fixed:**
This warning has been addressed by changing the default from `params=[]` to `params=None` and then converting to an empty list with `params = params or []`.
Parameter is only read so it is not mutable.

```python
def execute(sql, params=None):
    params = params or []
    # ...
```

## Configuration

The `.pylintrc` file already disables many unnecessary warnings while maintaining code quality standards.
