# Taller

## Pasos para ejecutarlo
```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Pasos 2 y 3: pruebas y cobertura
pytest -v
pytest --cov=etl --cov-branch --cov-report=term-missing --cov-report=xml

# Paso 4: SonarQube (http://localhost:9000, admin/admin; crea el token en My Account > Security)
docker run -d --name sonarqube -p 9000:9000 sonarqube:community
export SONAR_TOKEN="tu_token"
docker run --rm --network host -e SONAR_HOST_URL="http://localhost:9000" \
  -e SONAR_TOKEN="$SONAR_TOKEN" -v "$(pwd):/usr/src" sonarsource/sonar-scanner-cli
```

## Paso 5: ANTES y DESPUÉS
se encuentra un documento pdf que explica todo lo que paso con las pruebas 
