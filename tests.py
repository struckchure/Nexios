from nexio.orm import models,fields

class User(models.Model):

    name = fields.CharField(max_length= 80)