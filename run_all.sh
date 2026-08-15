
set -e

# Change directory to project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# Color Codes for Output
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${CYAN}====================================================${NC}"
echo -e "${GREEN}       Starting Plantica Core Backend Engine       ${NC}"
echo -e "${CYAN}====================================================${NC}"

# 1. Check Python Virtual Environment
VENV_PATH="$SCRIPT_DIR/env"
if [ -d "$VENV_PATH" ]; then
    echo -e "${GREEN}[1/4] Activating Virtual Environment (env)...${NC}"
    source "$VENV_PATH/bin/activate"
else
    echo -e "${YELLOW}[1/4] Virtual environment 'env' not found. Using system python...${NC}"
fi

# 2. Check & Change to Django Root
DJANGO_DIR="$SCRIPT_DIR/plantica_core"
if [ -d "$DJANGO_DIR" ]; then
    cd "$DJANGO_DIR"
else
    echo -e "${RED}Error: Django root directory 'plantica_core' not found!${NC}"
    exit 1
fi

# 3. Run Database Migrations
echo -e "${GREEN}[2/4] Applying Database Migrations...${NC}"
python3 manage.py migrate

# 4. Seed District Plant Data if needed
echo -e "${GREEN}[3/4] Ensuring District Plant Recommendations are Seeded...${NC}"
python3 manage.py seed_plants || true

# 5. Launch Django Development Server
echo -e "${CYAN}====================================================${NC}"
echo -e "${GREEN}🚀 Launching Django Server on http://0.0.0.0:8000 ${NC}"
echo -e "${YELLOW}   API Base URL: http://127.0.0.1:8000/api/v1/      ${NC}"
echo -e "${CYAN}====================================================${NC}"

python3 manage.py runserver 0.0.0.0:8000
