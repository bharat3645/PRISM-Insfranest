"""
Go Fiber Code Generator for InfraNest
Generates Go Fiber code from DSL
"""

from typing import Dict, Any, Optional
import os
import shutil
import tempfile
import zipfile
import logging
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

logger = logging.getLogger(__name__)

class GoGenerator:
    """Go Fiber code generator"""
    
    def __init__(self):
        self.template_dir = Path(__file__).parent.parent.parent / "templates" / "go"
        # Create template directory if it doesn't exist
        os.makedirs(self.template_dir, exist_ok=True)
        
        # Initialize Jinja2 environment
        self.env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            trim_blocks=True,
            lstrip_blocks=True
        )
    
    def generate(self, dsl_spec: Dict[str, Any]) -> Dict[str, str]:
        """Generate Go code from DSL specification"""
        files = {}
        project_name = dsl_spec.get('meta', {}).get('name', 'go_app')
        models = dsl_spec.get('models', {})
        
        # go.mod
        files['go.mod'] = f'''module {project_name}

go 1.21

require (
\tgithub.com/gofiber/fiber/v2 v2.51.0
\tgorm.io/gorm v1.25.5
\tgorm.io/driver/postgres v1.5.4
\tgithub.com/golang-jwt/jwt/v4 v4.5.0
)
'''
        
        # main.go
        files['main.go'] = f'''package main

import (
\t"log"
\t"os"
\t
\t"github.com/gofiber/fiber/v2"
\t"github.com/gofiber/fiber/v2/middleware/cors"
\t"github.com/gofiber/fiber/v2/middleware/logger"
\t"{project_name}/database"
\t"{project_name}/routes"
)

func main() {{
\tapp := fiber.New()

\t// Middleware
\tapp.Use(logger.New())
\tapp.Use(cors.New())

\t// Connect to database
\tdatabase.Connect()

\t// Setup routes
\troutes.Setup(app)

\t// Start server
\tport := os.Getenv("PORT")
\tif port == "" {{
\t\tport = "8080"
\t}}
\tlog.Fatal(app.Listen(":" + port))
}}
'''
        
        # database/database.go
        db_code = '''package database

import (
\t"fmt"
\t"log"
\t"os"
\t
\t"gorm.io/driver/postgres"
\t"gorm.io/gorm"
)

var DB *gorm.DB

func Connect() {
\tdsn := fmt.Sprintf(
\t\t"host=%s user=%s password=%s dbname=%s port=%s sslmode=disable",
\t\tos.Getenv("DB_HOST"),
\t\tos.Getenv("DB_USER"),
\t\tos.Getenv("DB_PASSWORD"),
\t\tos.Getenv("DB_NAME"),
\t\tos.Getenv("DB_PORT"),
\t)

\tdb, err := gorm.Open(postgres.Open(dsn), &gorm.Config{})
\tif err != nil {
\t\tlog.Fatal("Failed to connect to database:", err)
\t}

\tDB = db
\t
\t// Auto migrate models
'''
        for model_name in models.keys():
            db_code += f'\tDB.AutoMigrate(&{model_name}{{}})\n'
        db_code += '}\n'
        files['database/database.go'] = db_code
        
        # models/models.go
        models_code = '''package models

import (
\t"time"
\t"gorm.io/gorm"
)

'''
        for model_name, model_spec in models.items():
            models_code += f'type {model_name} struct {{\n'
            models_code += '\tgorm.Model\n'
            fields = model_spec.get('fields', {})
            for field_name, field_spec in fields.items():
                field_type = field_spec.get('type', 'string')
                go_type = 'string'
                if field_type in ['integer', 'number']:
                    go_type = 'int'
                elif field_type == 'boolean':
                    go_type = 'bool'
                elif field_type in ['date', 'datetime']:
                    go_type = 'time.Time'
                
                models_code += f'\t{field_name.title()} {go_type} `json:"{field_name}"`\n'
            models_code += '}\n\n'
        files['models/models.go'] = models_code
        
        # handlers/handlers.go
        handlers_code = f'''package handlers

import (
\t"github.com/gofiber/fiber/v2"
\t"{project_name}/database"
\t"{project_name}/models"
)

'''
        for model_name in models.keys():
            handlers_code += f'''// Get all {model_name}s
func Get{model_name}s(c *fiber.Ctx) error {{
\tvar items []models.{model_name}
\tdatabase.DB.Find(&items)
\treturn c.JSON(items)
}}

// Get one {model_name}
func Get{model_name}(c *fiber.Ctx) error {{
\tid := c.Params("id")
\tvar item models.{model_name}
\tif err := database.DB.First(&item, id).Error; err != nil {{
\t\treturn c.Status(404).JSON(fiber.Map{{"error": "Not found"}})
\t}}
\treturn c.JSON(item)
}}

// Create {model_name}
func Create{model_name}(c *fiber.Ctx) error {{
\tvar item models.{model_name}
\tif err := c.BodyParser(&item); err != nil {{
\t\treturn c.Status(400).JSON(fiber.Map{{"error": err.Error()}})
\t}}
\tdatabase.DB.Create(&item)
\treturn c.Status(201).JSON(item)
}}

// Update {model_name}
func Update{model_name}(c *fiber.Ctx) error {{
\tid := c.Params("id")
\tvar item models.{model_name}
\tif err := database.DB.First(&item, id).Error; err != nil {{
\t\treturn c.Status(404).JSON(fiber.Map{{"error": "Not found"}})
\t}}
\tif err := c.BodyParser(&item); err != nil {{
\t\treturn c.Status(400).JSON(fiber.Map{{"error": err.Error()}})
\t}}
\tdatabase.DB.Save(&item)
\treturn c.JSON(item)
}}

// Delete {model_name}
func Delete{model_name}(c *fiber.Ctx) error {{
\tid := c.Params("id")
\tvar item models.{model_name}
\tif err := database.DB.First(&item, id).Error; err != nil {{
\t\treturn c.Status(404).JSON(fiber.Map{{"error": "Not found"}})
\t}}
\tdatabase.DB.Delete(&item)
\treturn c.SendStatus(204)
}}

'''
        files['handlers/handlers.go'] = handlers_code
        
        # routes/routes.go
        routes_code = f'''package routes

import (
\t"github.com/gofiber/fiber/v2"
\t"{project_name}/handlers"
)

func Setup(app *fiber.App) {{
\tapi := app.Group("/api/v1")
\t
'''
        for model_name in models.keys():
            plural = model_name.lower() + 's'
            routes_code += f'''\t// {model_name} routes
\t{plural} := api.Group("/{plural}")
\t{plural}.Get("/", handlers.Get{model_name}s)
\t{plural}.Get("/:id", handlers.Get{model_name})
\t{plural}.Post("/", handlers.Create{model_name})
\t{plural}.Put("/:id", handlers.Update{model_name})
\t{plural}.Delete("/:id", handlers.Delete{model_name})
\t
'''
        routes_code += '}\n'
        files['routes/routes.go'] = routes_code
        
        # Dockerfile
        files['Dockerfile'] = '''FROM golang:1.21-alpine AS builder

WORKDIR /app

COPY go.mod go.sum ./
RUN go mod download

COPY . .
RUN go build -o main .

FROM alpine:latest
WORKDIR /root/
COPY --from=builder /app/main .
EXPOSE 8080
CMD ["./main"]
'''
        
        # docker-compose.yml
        files['docker-compose.yml'] = f'''version: '3.8'
services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: {project_name}
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  web:
    build: .
    ports:
      - "8080:8080"
    depends_on:
      - db
    environment:
      DB_HOST: db
      DB_USER: postgres
      DB_PASSWORD: postgres
      DB_NAME: {project_name}
      DB_PORT: 5432
      PORT: 8080

volumes:
  postgres_data:
'''
        
        # README.md
        files['README.md'] = f'''# {project_name}

A Go Fiber API application generated by InfraNest.

## Setup

```bash
go mod download
go run main.go
```

## Docker

```bash
docker-compose up --build
```

## API Endpoints

'''
        for model_name in models.keys():
            plural = model_name.lower() + 's'
            files['README.md'] += f'''
### {model_name}
- GET /api/v1/{plural} - List all
- POST /api/v1/{plural} - Create new
- GET /api/v1/{plural}/:id - Get one
- PUT /api/v1/{plural}/:id - Update
- DELETE /api/v1/{plural}/:id - Delete
'''
        
        # .gitignore
        files['.gitignore'] = '''*.exe
*.exe~
*.dll
*.so
*.dylib
*.test
*.out
vendor/
'''
        
        return files
    
    def generate_zip(self, dsl_spec: Dict[str, Any]) -> Optional[str]:
        """Generate Go Fiber project and return path to zip file"""
        try:
            # Create a temporary directory
            temp_dir = tempfile.mkdtemp()
            project_dir = os.path.join(temp_dir, dsl_spec['meta']['name'])
            os.makedirs(project_dir, exist_ok=True)
            
            # Generate files
            files = self.generate(dsl_spec)
            
            # Write files to the temporary directory
            for filename, content in files.items():
                file_path = os.path.join(project_dir, filename)
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                with open(file_path, 'w') as f:
                    f.write(content)
            
            # Create zip file
            zip_path = os.path.join(temp_dir, f"{dsl_spec['meta']['name']}.zip")
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, _, files in os.walk(project_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, temp_dir)
                        zipf.write(file_path, arcname)
            
            return zip_path
        
        except Exception as e:
            logger.error(f"Error generating Go Fiber project: {str(e)}")
            return None
        finally:
            # Clean up temporary directory
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def preview(self, dsl_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Generate preview of code structure"""
        return {
            'files': [
                {'path': 'main.go', 'type': 'main', 'description': 'Main application file'},
                {'path': 'go.mod', 'type': 'config', 'description': 'Go module file'},
                {'path': 'go.sum', 'type': 'config', 'description': 'Go dependencies'},
                {'path': 'models/models.go', 'type': 'model', 'description': 'Data models'},
                {'path': 'handlers/handlers.go', 'type': 'handler', 'description': 'API handlers'},
                {'path': 'routes/routes.go', 'type': 'config', 'description': 'API routes'},
                {'path': 'middleware/auth.go', 'type': 'middleware', 'description': 'Authentication middleware'},
                {'path': 'database/database.go', 'type': 'config', 'description': 'Database configuration'},
                {'path': 'Dockerfile', 'type': 'config', 'description': 'Docker configuration'},
                {'path': 'docker-compose.yml', 'type': 'config', 'description': 'Docker Compose configuration'},
                {'path': 'README.md', 'type': 'doc', 'description': 'Project documentation'},
                {'path': '.gitignore', 'type': 'config', 'description': 'Git ignore file'},
            ]
        }
    
    def _create_context(self, dsl_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Create context for templates"""
        return {
            'project_name': dsl_spec['meta']['name'],
            'description': dsl_spec.get('meta', {}).get('description', ''),
            'version': dsl_spec.get('meta', {}).get('version', '0.1.0'),
            'database': dsl_spec.get('meta', {}).get('database', 'postgres'),
            'models': dsl_spec.get('models', {}),
            'auth': dsl_spec.get('auth', {}),
            'apis': dsl_spec.get('apis', {})
        }
    
    def _render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """Render a template with the given context"""
        try:
            template = self.env.get_template(template_name)
            return template.render(**context)
        except Exception as e:
            logger.error(f"Error rendering template {template_name}: {str(e)}")
            # Return a placeholder if template doesn't exist
            if template_name == 'main.go.j2':
                return self._generate_main_fallback(context)
            elif template_name == 'go.mod.j2':
                return self._generate_go_mod_fallback(context)
            else:
                return f"// TODO: Implement {template_name.replace('.j2', '')}"
    
    def _generate_main_fallback(self, context: Dict[str, Any]) -> str:
        """Generate main.go as fallback"""
        project_name = context.get('project_name', 'goapp')
        return f'''package main

import (
    "log"
    "github.com/gofiber/fiber/v2"
    "github.com/gofiber/fiber/v2/middleware/logger"
    "github.com/gofiber/fiber/v2/middleware/cors"
    "{project_name}/routes"
    "{project_name}/database"
)

func main() {{
    // Initialize Fiber app
    app := fiber.New(fiber.Config{{
        AppName: "{project_name}",
    }})
    
    // Middleware
    app.Use(logger.New())
    app.Use(cors.New())
    
    // Connect to database
    database.Connect()
    
    // Setup routes
    routes.SetupRoutes(app)
    
    // Start server
    log.Fatal(app.Listen(":8000"))
}}
'''
    
    def _generate_go_mod_fallback(self, context: Dict[str, Any]) -> str:
        """Generate go.mod as fallback"""
        project_name = context.get('project_name', 'goapp')
        return f'''module {project_name}

go 1.19

require (
    github.com/gofiber/fiber/v2 v2.46.0
    github.com/golang-jwt/jwt/v5 v5.0.0
    github.com/joho/godotenv v1.5.1
    gorm.io/driver/postgres v1.5.2
    gorm.io/gorm v1.25.1
)
'''
    
    def _generate_go_mod(self) -> str:
        """Generate go.mod"""
        return '''module infranest-app

go 1.21

require github.com/gofiber/fiber/v2 v2.52.0
'''
    
    def _generate_dockerfile(self) -> str:
        """Generate Dockerfile"""
        return '''FROM golang:1.21-alpine AS builder

WORKDIR /app
COPY . .
RUN go mod download
RUN go build -o main .

FROM alpine:latest
RUN apk --no-cache add ca-certificates
WORKDIR /root/
COPY --from=builder /app/main .
EXPOSE 8000
CMD ["./main"]
'''
