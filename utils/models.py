from pydantic import BaseModel, field_validator, Field
import re

class Repo(BaseModel):
    name: str = Field(..., example="username/reponame")
    
    @field_validator('name')
    def validate_github_format(cls, v):
        v = v.strip().replace('https://github.com/', '').replace('http://github.com/', '')
        if not re.match(r'^[\w\-\.]+/[\w\-\.]+$', v):
            raise ValueError('Must be GitHub format: username/reponame')
        return v