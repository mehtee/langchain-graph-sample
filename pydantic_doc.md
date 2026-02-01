Here’s a **complete, modern (Pydantic v2+) guide** to using **Pydantic in a Pythonic, production-ready way** — from basics to advanced patterns like `RootModel`, custom validators, serialization, computed fields, and settings. All code shown assumes **Pydantic v2+** (the current major version). ([Pydantic][1])

---

## 📌 1. What Is Pydantic?

Pydantic is a **data validation and parsing** library based on Python’s type hints. It turns untrusted data (e.g., dicts from APIs) into well-typed objects, with automatic validation and conversion. It’s widely used in frameworks like FastAPI and systems that depend on schema integrity. ([Pydantic][2])

---

## 📌 2. Installing

```bash
pip install pydantic
```

Optionally for settings support:

```bash
pip install pydantic-settings
```

---

## 📌 3. BaseModel: Core Usage

Defining a model is as simple as subclassing `BaseModel` and using type annotations:

```python
from pydantic import BaseModel

class User(BaseModel):
    id: int
    name: str
    age: int = 0

u = User(id='123', name='Alice')
assert u.id == 123  # string coerced to int
```

⚠️ Pydantic guarantees the **validated output** conforms to types — not that it accepts every wrong input. ([Pydantic][1])

---

## 📌 4. Fields and Field Configuration

You can use `Field()` for additional constraints and metadata:

```python
from pydantic import Field

class Product(BaseModel):
    id: int
    price: float = Field(gt=0)  # must be > 0
```

### Field features

* Default values & factories (`default_factory`)
* Constraints like `gt`, `lt`, `min_length`, `max_length`
* Aliases for serialization
* Strict typing (`strict=True`) via `Field()` or `ConfigDict`

👉 Use `typing.Annotated` for extra validators or metadata. ([Pydantic][3])

---

## 📌 5. Model Configuration (`model_config`)

Each model can define its config via `ConfigDict`:

```python
from pydantic import BaseModel, ConfigDict

class MyModel(BaseModel):
    model_config = ConfigDict(extra='forbid')  # disallow unexpected fields
    x: int
```

Common config options:

* `extra`: `'ignore'` (default), `'allow'`, `'forbid'`
* `str_max_length`, `frozen` (immutable models)
* `from_attributes=True` (for ORM-style loading) ([Pydantic][4])

---

## 🔍 6. Validation

### Field Level

Use `@field_validator` to validate a specific field:

```python
from pydantic import field_validator

class Person(BaseModel):
    age: int

    @field_validator('age')
    def check_age(cls, v):
        if v < 0:
            raise ValueError("must be nonnegative")
        return v
```

### Model Level

Use `@model_validator` for cross-field logic:

```python
from pydantic import model_validator

class Pair(BaseModel):
    a: int
    b: int

    @model_validator(mode='after')
    def check_sum(cls, model):
        if model.a + model.b > 100:
            raise ValueError("sum too large")
        return model
```

There are also **before**, **after**, and **wrap** validator modes. ([Pydantic][5])

---

## 🧠 7. Serializing and Exporting

Pydantic supports powerful serialization:

* `.model_dump()` → dict
* `.model_dump_json()` → JSON string

```python
data = user.model_dump()
json_str = user.model_dump_json(indent=2)
```

### Custom Serialization

You can control how fields or entire models serialize:

```python
from pydantic import field_serializer, model_serializer

class Event(BaseModel):
    timestamp: datetime

    @field_serializer("timestamp")
    def serialize_ts(self, ts, _info):
        return ts.isoformat()
```

Or for whole model:

```python
    @model_serializer
    def ser(self):
        return {"user": self.name}
```

The `@field_serializer` and `@model_serializer` decorators offer deep control. ([Pydantic][6])

---

## 🧩 8. Computed Fields

Computed fields allow defining derived properties on the model:

```python
from pydantic import computed_field

class Order(BaseModel):
    price: float
    quantity: int

    @computed_field
    @property
    def total(self):
        return self.price * self.quantity
```

Use this when you want read-only values derived from model state.

---

## 📦 9. RootModel & Custom Root Types

`RootModel` lets you define a model that **validates a root value instead of named fields**. This replaces the old `__root__` pattern from Pydantic v1. ([Pydantic][1])

### Example: List Root

```python
from pydantic import RootModel

Pets = RootModel[list[str]]

pets = Pets(["dog", "cat"])
print(pets.root)  # ['dog', 'cat']
```

You can use a `RootModel` when the entire payload is not a mapping/dict — e.g., a top-level array or primitive. ([Stack Overflow][7])

---

## 🧠 10. Generic Models

Like standard Python generics, Pydantic supports **generic models**:

```python
from typing import Generic, TypeVar
from pydantic import BaseModel

T = TypeVar('T')

class Result(BaseModel, Generic[T]):
    value: T

r = Result[int](value=42)
```

This is helpful for reusable API response wrappers and similar patterns. ([Pydantic][1])

---

## 🛠️ 11. ORM & Settings

### ORM Integration

You can validate data from ORMs by enabling `from_attributes=True` in `ConfigDict`.

```python
class User(BaseModel):
    model_config = ConfigDict(from_attributes=True)
```

### Settings via `pydantic-settings`

For environment variable loading:

```python
from pydantic_settings import BaseSettings

class AppConfig(BaseSettings):
    debug: bool = False
```

Settings models will automatically read `.env` and environment variables.

---

## 🧰 12. Useful Methods & Tools

| Method                | Purpose                             |
| --------------------- | ----------------------------------- |
| `model_validate()`    | Validate raw data into model        |
| `model_dump()`        | Get a dict representation           |
| `model_dump_json()`   | Get JSON                            |
| `model_construct()`   | Create *without* running validation |
| `model_copy()`        | Clone model                         |
| `model_json_schema()` | JSON Schema for models              |

`model_construct()` is useful if data is already validated and you want faster instantiation. ([Pydantic][1])

---

## 📌 13. Tips, Gotchas & Best Practices

🔹 **Avoid mutable defaults** — use `default_factory`. ([Pydantic][1])
🔹 **Prefer strict typing** for APIs handling user input.
🔹 **Use validators for cross-field logic** instead of post-processing.
🔹 **Leverage serialization decorators** for API responses.
🔹 Keep your models lean — use nested submodels for structure.

---

## 🧠 14. Summary

Pydantic v2 is a **powerful, type-safe, and flexible** system for structured data in Python:

* **Models & Fields** — core building blocks.
* **Validation** — automatic + custom logic.
* **Serialization** — full control over output.
* **Computed & Root Models** — advanced patterns.
* **Settings & ORM** — real-world workflows.

With these tools, you can confidently validate, transform, and serialize complex data in Python. ([Pydantic][1])

---

If you want, I can also generate ready-to-use template files (e.g., for an API project structure) or cheat-sheet code snippets you can paste directly into your editor.

[1]: https://docs.pydantic.dev/2.0/usage/models/?utm_source=chatgpt.com "Models - Pydantic"
[2]: https://docs.pydantic.dev/?utm_source=chatgpt.com "Welcome to Pydantic - Pydantic Validation"
[3]: https://docs.pydantic.dev/latest/concepts/fields/?utm_source=chatgpt.com "Fields - Pydantic Validation"
[4]: https://docs.pydantic.dev/latest/concepts/models/?utm_source=chatgpt.com "Models - Pydantic Validation"
[5]: https://docs.pydantic.dev/latest/concepts/validators/?utm_source=chatgpt.com "Validators"
[6]: https://docs.pydantic.dev/2.11/concepts/serialization/?utm_source=chatgpt.com "Serialization"
[7]: https://stackoverflow.com/questions/77902897/pydantic-rootmodel-data?utm_source=chatgpt.com "python - Pydantic RootModel data - Stack Overflow"
