# Validation in Nexios

The **Validation** module in Nexios is a powerful, extensible, and developer-friendly library built on top of **Marshmallow**. It provides a declarative way to define schemas, validate incoming data, and serialize responses. With its intuitive API and seamless integration with Nexios, it simplifies data validation and transformation in modern ASGI applications.

## Getting Started
### Basic Usage
Here’s a simple example of how to use the Nexios Validator module in a Nexios application:
```python
from nexios import get_application
from nexios.validator import Schema, fields, validate,ValidationError
app = get_application()

class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    email = fields.Email(required=True)

@app.post("/users")
async def create_user(request, response):
    data = await request.json
    schema = UserSchema()

    try:
        schema.load(data)
    except ValidationError as err:
        return reponse.json(err.messages,status_code = 422)
    return response.json(data)
```

---

## Core Concepts

### Schema Definition
Schemas are the core of the Nexios Validator module. They define the structure of your data and the rules for validation and serialization.

#### Example Schema
```python
from nexios.validator import Schema, fields

class ProductSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    price = fields.Float(required=True)
    in_stock = fields.Bool(default=True)
```

### Validation
Validation ensures that incoming data conforms to the schema. The `@validate_request` decorator from `.utils.validator` automatically validates request data and passes the validated data to your route handler.

#### Example Validation
```python
@app.post("/products")
@validate_request(schema)
async def create_product(request, response):
    data = request.validated_data
    return response.json(data)
```

### Serialization
Serialization converts complex data types (e.g., objects) into JSON-compatible formats. Use the `dump` method to serialize data.

#### Example Serialization
```python
@app.get("/products")
async def get_products(request, response):
    products = [
        {"id": 1, "name": "Laptop", "price": 999.99, "in_stock": True},
        {"id": 2, "name": "Mouse", "price": 19.99, "in_stock": False},
    ]
    schema = ProductSchema(many=True)
    return response.json(schema.dump(products))
```

### Error Handling
The nexios.validator module provides detailed error messages for invalid data. Use the `ValidationError` exception to handle errors.

#### Example Error Handling
```python
from nexios.validator import ValidationError

@app.post("/products")
@validate(schema=ProductSchema)
async def create_product(request, response, data):
    try:
        # Process validated data
        return response.json(data)
    except ValidationError as err:
        return response.json({"error": err.messages}, status=400)
```

---

## Advanced Features

### Nested Schemas
Nested schemas allow you to validate and serialize complex, hierarchical data structures.

#### Example Nested Schema
```python
class AddressSchema(Schema):
    street = fields.Str(required=True)
    city = fields.Str(required=True)
    zipcode = fields.Str(required=True)

class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    address = fields.Nested(AddressSchema)
```

### Custom Validators
Custom validators enable you to define application-specific validation logic.

#### Example Custom Validator
```python
from nexios.validator import validates, ValidationError

class UserSchema(Schema):
    name = fields.Str(required=True)

    @validates("name")
    def validate_name(self, value):
        if len(value) < 3:
            raise ValidationError("Name must be at least 3 characters long.")
```




## API Reference

### `Schema`
- **`dump(obj)`**: Serialize an object.
- **`load(data)`**: Deserialize and validate data.
- **`validate(data)`**: Validate data without deserialization.

### `fields`
- **`Str`**: String field.
- **`Int`**: Integer field.
- **`Float`**: Float field.
- **`Bool`**: Boolean field.
- **`Email`**: Email field.
- **`Nested`**: Nested schema field.

### Decorators
- **`@validate(schema)`**: Validate request data using the specified schema.

---

## Examples

### Example 1: User Registration
```python
class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True)

@app.post("/register")
@validate(schema=UserSchema)
async def register(request, response):
    # Save user to database
    data = request.validated_data
    return response.json({"message": "User registered successfully"})
```

### Example 2: Product Catalog
```python
class ProductSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    price = fields.Float(required=True)

@app.get("/products")
async def get_products(request, response):
    products = [
        {"id": 1, "name": "Laptop", "price": 999.99},
        {"id": 2, "name": "Mouse", "price": 19.99},
    ]
    schema = ProductSchema(many=True)
    return response.json(schema.dump(products))
```

---

## Best Practices
1. **Use Schemas Consistently**: Define schemas for all data models.
2. **Leverage Custom Validators**: Add application-specific validation logic.
3. **Handle Errors Gracefully**: Provide meaningful error messages for invalid data.
4. **Optimize Performance**: Use async validation for I/O-bound tasks.

---

## Performance Considerations
- Use caching for frequently accessed data.
- Batch process large datasets to reduce overhead.
- Avoid unnecessary validation in high-traffic routes.

---

This documentation provides a comprehensive guide to using the **Nexios Validator** module. The `nexios.validator` module is a fork of the **Marshmallow** validator, designed to provide enhanced request validation within the **Nexios framework**. It extends **Marshmallow's** functionality to better integrate with Nexios, supporting streamlined data validation for JSON, form data, and URL-encoded requests.  

For more details, refer to the official:  
- **[Nexios documentation](https://github.com/TechWithDunamix/Nexios)**  
- **[Marshmallow documentation](https://marshmallow.readthedocs.io/)**