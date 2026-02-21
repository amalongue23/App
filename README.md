# Sistema de Análise e Visualização de dados para uma Universidade (Backend API Flask + Frontend Vue.js)

API em Flask com arquitetura MVC, princípios SOLID, padrão Repository/Service, JWT, MySQL e documentação Swagger.

## Requisitos
- Python 3.11+
- MySQL (local)
- Node.js 20+
- Base de dados `mpuna`

## Backend
1. Criar base no MySQL:
   ```sql
   CREATE DATABASE mpuna;
   ```
2. Ativar ambiente virtual:
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```
3. Instalar dependências:
   ```bash
   pip install -r requirements.txt
   ```
4. Executar:
   ```bash
   python run.py
   ```

## Frontend (Vue.js)
1. Entrar na pasta:
   ```bash
   cd frontend
   ```
2. Instalar dependências:
   ```bash
   npm install
   ```
3. Executar:
   ```bash
   npm run dev
   ```
4. Abrir app:
   - `http://localhost:5173/login`

## Popular dados demo (unidades, cursos e perfis)
Executar:
```bash
python seed_demo_data.py
```

Credenciais demo criadas (`senha`: `123456`):
- Diretores: `dir.eng`, `dir.cie`, `dir.sau`
- Chefes: `chef.comp`, `chef.civ`, `chef.mat`, `chef.fis`, `chef.enf`, `chef.nut`

## URLs úteis
- Swagger UI: `http://localhost:5000/swagger-ui`
- OpenAPI JSON: `http://localhost:5000/openapi.json`
- Frontend login: `http://localhost:5173/login`

## Docker (backend + frontend + MySQL)
1. Subir tudo:
   ```bash
   docker compose up --build
   ```
2. Acessos:
   - Backend: `http://localhost:5000`
   - Frontend: `http://localhost:5173`
3. Base de dados:
   - MySQL: `localhost:3306`
   - user: `root`
   - password: (vazio)
   - db: `mpuna`

## Dashboard por período (ano)
- `GET /api/dashboard/filters`
  - Retorna lista de períodos (`ano_academico_id`, `ano_lectivo`).
- `GET /api/dashboard/chief?ano_academico_id=<id>&ano_lectivo=<label>`
  - Requer perfil `CHEFE`.
  - Ambos parâmetros são obrigatórios.
  - `ano_lectivo` deve corresponder ao `ano_academico_id`.
- `GET /api/dashboard/director?ano_academico_id=<id>&ano_lectivo=<label>`
  - Requer perfil `DIRETOR`.
  - Ambos parâmetros são obrigatórios.
  - `ano_lectivo` deve corresponder ao `ano_academico_id`.
- `GET /api/dashboard/reitor?ano_academico_id=<id>&ano_lectivo=<label>`
  - Requer perfil `REITOR`.
  - Ambos parâmetros são obrigatórios.
  - `ano_lectivo` deve corresponder ao `ano_academico_id`.

## Utilizador inicial (dev)
- `username`: `admin`
- `password`: `admin123`
- `role`: `REITOR`

## Autenticação
- `POST /api/auth/login` retorna token JWT.
- O frontend guarda token e dados do utilizador em `localStorage`.
- Rotas protegidas no frontend usam guard de autenticação.

## Papéis
- `REITOR`
- `DIRETOR`
- `CHEFE`

## Requisitos Funcionais implementados
- RF01: `POST/GET /api/academic-years`
- RF02: `POST /api/datasets/unify`
- RF03: `POST /api/datasets/validate`
- RF04: `POST /api/reports/generate`
- RF05: `/api/units`
- RF06: `/api/departments`, `/api/departments/by-unit/<unit_id>`
- RF07: `/api/courses`, `/api/courses/by-department/<department_id>`
- RF08: `/api/students`, `/api/students/by-department/<department_id>`, `/api/students/control-table`
- RF09: `POST/GET /api/users` + `POST /api/auth/login`
- RF10: JWT + autorização por papel em decorators
- RF11: validação por schemas Marshmallow em todos os endpoints
