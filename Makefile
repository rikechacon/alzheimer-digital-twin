.PHONY: setup dev test simulate optimize validate docs deploy clean lint format

# Variables
PYTHON := python3
VENV := venv
PIP := $(VENV)/bin/pip
PYTHON := $(VENV)/bin/python

# Configuración
.DEFAULT_GOAL := help

##@ Setup y Configuración

setup: ## Configurar entorno virtual e instalar dependencias
	@echo "📦 Configurando entorno virtual..."
	$(PYTHON) -m venv $(VENV)
	@echo "✅ Entorno virtual creado en '$(VENV)'"
	@echo "⚠️  Ejecuta: source $(VENV)/bin/activate"
	@echo "⚠️  Luego: make install"

install: ## Instalar dependencias
	@echo "📥 Instalando dependencias..."
	$(PIP) install -r requirements.txt
	@echo "✅ Dependencias instaladas"

install-dev: ## Instalar dependencias de desarrollo
	@echo "📥 Instalando dependencias de desarrollo..."
	$(PIP) install -r requirements.txt
	$(PIP) install pytest pytest-cov black flake8 mypy
	@echo "✅ Dependencias de desarrollo instaladas"

##@ Desarrollo

dev: ## Iniciar servidor de desarrollo (FastAPI)
	@echo "🚀 Iniciando servidor de desarrollo..."
	$(PYTHON) -m uvicorn backend.api.main:app --reload --host 0.0.0.0 --port 8000

simulate: ## Ejecutar simulación de proteostasis
	@echo "🌀 Ejecutando simulación de proteostasis..."
	$(PYTHON) -c "from alzdt.simulator import ProteostasisSimulator; print('Simulador listo')"

optimize: ## Ejecutar optimización multi-objetivo
	@echo "🎯 Ejecutando optimización multi-objetivo..."
	$(PYTHON) -c "from alzdt.optimizer import MultiObjectiveOptimizer; print('Optimizador listo')"

##@ Testing

test: ## Ejecutar todas las pruebas
	@echo "🧪 Ejecutando pruebas..."
	$(PYTHON) -m pytest tests/ -v --tb=short

test-unit: ## Ejecutar pruebas unitarias
	@echo "🧪 Ejecutando pruebas unitarias..."
	$(PYTHON) -m pytest tests/unit/ -v

test-integration: ## Ejecutar pruebas de integración
	@echo "🧪 Ejecutando pruebas de integración..."
	$(PYTHON) -m pytest tests/integration/ -v

test-cov: ## Ejecutar pruebas con cobertura
	@echo "🧪 Ejecutando pruebas con cobertura..."
	$(PYTHON) -m pytest tests/ -v --cov=alzdt --cov-report=html --cov-report=term

##@ Validación

validate: ## Ejecutar validación clínica simulada
	@echo "✅ Ejecutando validación clínica simulada..."
	$(PYTHON) scripts/run_validation.py

validate-adni: ## Validar contra dataset ADNI
	@echo "✅ Validando contra dataset ADNI..."
	$(PYTHON) scripts/validate_adni.py

##@ Documentación

docs: ## Generar documentación
	@echo "📚 Generando documentación..."
	mkdocs build

docs-serve: ## Servir documentación localmente
	@echo "📚 Sirviendo documentación en http://localhost:8001..."
	mkdocs serve -a localhost:8001

##@ Linting y Formateo

lint: ## Ejecutar linter
	@echo "🔍 Ejecutando linter..."
	$(PYTHON) -m flake8 alzdt/ backend/ tests/ --max-line-length=120

format: ## Formatear código con Black
	@echo "✏️  Formateando código..."
	$(PYTHON) -m black alzdt/ backend/ tests/

type-check: ## Verificar tipos con MyPy
	@echo "🔍 Verificando tipos..."
	$(PYTHON) -m mypy alzdt/ backend/

##@ Despliegue

deploy: ## Desplegar a entorno de staging
	@echo "🚀 Desplegando a entorno de staging..."
	docker-compose -f docker-compose.yml up -d

docker-build: ## Construir imagen Docker
	@echo "🐳 Construyendo imagen Docker..."
	docker build -t alzdt-core:latest .

docker-run: ## Ejecutar contenedor Docker
	@echo "🐳 Ejecutando contenedor Docker..."
	docker run -p 8000:8000 alzdt-core:latest

##@ Mantenimiento

clean: ## Limpiar cachés y artefactos
	@echo "🧹 Limpiando cachés y artefactos..."
	find . -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache htmlcov .coverage
	rm -rf build dist *.egg-info

clean-all: clean ## Limpiar todo incluyendo entorno virtual
	@echo "🧹 Limpiando todo..."
	rm -rf $(VENV)
	rm -rf data/models/*
	rm -rf data/processed/*

##@ Ayuda

help: ## Mostrar esta ayuda
	@echo "🧠 Alzheimer Digital Twin - Makefile"
	@echo ""
	@echo "Comandos disponibles:"
	@echo ""
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "Ejemplos de uso:"
	@echo "  make setup          # Configurar entorno"
	@echo "  make dev            # Iniciar servidor de desarrollo"
	@echo "  make test           # Ejecutar pruebas"
	@echo "  make docs-serve     # Ver documentación local"
	@echo ""
