from nexios.http.response import NexioResponse
from nexios.http.request import Request
from nexios.routers import Router, Routes
from nexios.decorators import AllowedMethods, validate_request
from models.tasks import TaskModel
from schemas.task_schemas import CreateTaskSchema, UpdateTaskSchema
from tortoise import Tortoise as db
from models.utils import LocalFileStorage
from nexios.utils.files import UploadedFile
from tortoise.exceptions import DoesNotExist

task_routes = Router(prefix="/api")
@AllowedMethods(["get"])
async def get_tasks(request: Request, response: NexioResponse):
    if request.url_params.get("id"):
        try:
            task = await TaskModel.get(id=request.url_params.get("id"))
            return response.json({
                "id": task.id,
                "name": task.name,
                "detail": task.detail,
                "completed": task.completed,
                "image": task.image,
                "date_dreated":task.date_created
            })
        except DoesNotExist:
            return response.json({"error": "Task not found"}, status_code=404)

    tasks = await TaskModel.all().values("id", "name", "image", "completed", "detail")
    return response.json(tasks)


# Create a New Task
@validate_request(CreateTaskSchema)
@AllowedMethods(["post"])
async def create_task(request: Request, response: NexioResponse):
    if not await request.validate_request():
        return response.json(request.validation_errors, status_code=400)
    data = request.validated_data

    file = LocalFileStorage()
    image = await file.store(data['image'])
    data['image'] = image
    await TaskModel.create(**data)

    return response.json({"success": "Task created"}, status_code=201)



@validate_request(UpdateTaskSchema)
@AllowedMethods(["put", "patch"])
async def update_task(request: Request, response: NexioResponse):
    if not await request.validate_request():
        return response.json(request.validation_errors, status_code=400)

    task_id = request.url_params.get("id")
    if not task_id:
        return response.json({"error": "Task ID is required"}, status_code=400)

    try:
        task = await TaskModel.get(id=task_id)
        data = request.validated_data

        # Handle optional image updates
        if "image" in data and isinstance(data["image"], UploadedFile):
            file = LocalFileStorage()
            data["image"] = await file.store(data["image"])

        await task.update_from_dict(data).save()
        return response.json({"success": "Task updated"}, status_code=200)

    except DoesNotExist:
        return response.json({"error": "Task not found"}, status_code=404)



@AllowedMethods(["delete"])
async def delete_task(request: Request, response: NexioResponse):
    task_id = request.url_params.get("id")
    if not task_id:
        return response.json({"error": "Task ID is required"}, status_code=400)

    try:
        task = await TaskModel.get(id=task_id)
        await task.delete()
        return response.json({"success": "Task deleted"}, status_code=200)

    except DoesNotExist:
        return response.json({"error": "Task not found"}, status_code=404)


# Add Routes
task_routes.add_route(Routes("/task/create", create_task))
task_routes.add_route(Routes("/task/all", get_tasks))
task_routes.add_route(Routes("/task/{id}", get_tasks))
task_routes.add_route(Routes("/task/{id}/update", update_task))
task_routes.add_route(Routes("/task/{id}/delete", delete_task))
