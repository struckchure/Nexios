#type:ignore
from nexios import get_application
from nexios.validator import Schema, fields, validate
from nexios.utils.validator import validate_request,ValidationError
app = get_application()



async def handle_validation(req,res,exc :ValidationError):
    return res.json(exc.messages,status_code = 422)

app.add_exception_handler(ValidationError,handle_validation)
    
class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    email = fields.Email(required=True)

@app.post("/users")
@validate_request(UserSchema())
async def create_user(request, response) -> None:
    return response.json({"text":"hello world"})