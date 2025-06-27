#!/bin/bash
# This script installs the necessary dependencies for the project on a Debian-based system.

if [ "$(id -u)" -ne 0 ]; then
    echo "This script needs to be run with root privileges, please use sudo."
    echo "You are not running this script as root. Please use sudo."
    exit 1
fi

echo "This script will install the necessary dependencies, configure and deploy pricechecker."
echo ""
echo "This script will update the system and install mandatory packages :"
echo "* System : curl, wget, git, and build-essential."
echo "* Python : Python3, python3-dev, python3-venv, and the required python packages."
echo ""
echo "* RECOMMENDED : gunicorn (production grade webserver, replacing flask embedded WSGI server)."
echo ""
echo "* Optional : Python3-dev (for building some Python packages that require compilation)."
echo ""
echo "This script will ask to install optional packages :"
echo "* Optional : html5lib (enhanced HTML parsing)"
echo "* Optional : chromium-browser and chromium-chromedriver (for web scraping with Selenium)"
echo "* Optional : firefox and geckodriver (for web scraping with Selenium)"
echo ""
echo 'This script will pull the last version of the project from GitHub.'
echo ""
echo "This script will also set up a systemd service for pricechecker."
echo ""
echo "Press any key to continue or Ctrl+C to cancel."
echo ""
read -n 1 -s -r

read -p "Do you want to check github to get the latest version (y to agree, any key to skip): " GITHUB
read -p "Do you want to install gunicorn? (y to agree, any key to skip): " GUNICORN
read -p "Do you want to install Python3-dev? (y to agree, any key to skip): " P3DEV
read -p "Do you want to install html5lib? (y to agree, any key to skip): " HTML5LIB
echo ""
echo "You have to choose between chromium and firefox for web scraping. YOU CAN CHOOSE ONE BUT NOT BOTH."
read -p "Do you want to install Chromium and chromedriver? (y to agree, any key to skip): " BROWSER
if [ "$BROWSER" = "y" ]; then
    BROWSER="chromium"
else
    read -p "Do you want to install Firefox and geckodriver? (y to agree, any key to skip): " BROWSER
    if [ "$BROWSER" = "y" ]; then
        BROWSER="firefox"
    else
        BROWSER="none"
    fi
fi
echo ""
echo "It is recommended to customize the configuration file located at ./config.py if the application is exposed on the internet."
read -p "Do you want to customize the configuration file during installation? You can do it later if you want (y to agree, any key to skip): " CUSTOMIZECONFIG
echo ""
read -p "Do you want to start PriceChecker after the installation? (y to agree, any key to skip): " STARTNOW
echo ""
read -p "Do you want to remove the test database? (y to agree, any key to skip): " REMOVEDB
echo ""
read -p "Do you want to setup PriceChecker as a service? (y to agree, any key to skip): " SYSSERVICE
echo ""

echo "#######"
echo "Updating the system..."
echo "#######"
apt update && apt upgrade -y

if [ $? -eq 0 ]; then
    echo "#######"
    echo "System updated successfully."
else
    echo "Failed to update the system. Please check your internet connection or package sources."
fi

echo "#######"
echo "Installing mandatory packages..."
echo "#######"
apt install -y curl wget git build-essential python3 python3-pip python3-venv python3-full nano openssl

if [ $? -eq 0 ]; then
    echo "#######"
    echo "Mandatory packages installed successfully."
else
    echo "Failed to install mandatory packages. Please check your internet connection or package sources."
    echo "Aborting the installation."
    exit 1
fi

if [ "$GITHUB" = "y" ]; then
    if [ -d ./pricechecker ]; then
        echo "#######"
        echo "Checking for the latest version of PriceChecker..."
        echo "#######"
        cd pricechecker || exit
        git pull origin main
        if [ $? -eq 0 ]; then
            echo "PriceChecker updated successfully."
        else
            echo "Failed to update PriceChecker. Please check your internet connection or package sources."
        fi
        cd .. || exit
    else
        echo "#######"
        echo "Cloning PriceChecker from GitHub..."
        echo "#######"
        git clone https://github.com/edouardsaucisse/pricechecker
        if [ $? -eq 0 ]; then
            echo "PriceChecker cloned successfully."
            cd pricechecker || exit
        else
            echo "Failed to clone PriceChecker. Please check your internet connection or package sources."
            echo "Aborting the installation."
            exit 1
        fi
    fi
fi

echo "#######"
echo "Creating Python virtual environment..."
echo "#######"
python3 -m venv .venv

if [ $? -eq 0 ]; then
    echo "Virtual environment created successfully."
else
    echo "Failed to create virtual environment. Please check your Python installation."
    echo "Aborting the installation."
    exit 1
fi

echo "#######"
echo "Activating virtual environment..."
echo "#######"
source .venv/bin/activate

if [ $? -eq 0 ]; then
    echo "Virtual environment activated successfully."
else
    echo "Failed to activate virtual environment."
    echo "Aborting the installation."
    exit 1
fi

echo "#######"
echo "Upgrading pip in virtual environment..."
echo "#######"
.venv/bin/pip install --upgrade pip

if [ $? -eq 0 ]; then
    echo "#######"
    echo "Pip upgraded successfully in virtual environment."
else
    echo "Failed to upgrade pip in virtual environment."
    echo "Aborting the installation."
    exit 1
fi

echo "#######"
echo "Installing Python packages in virtual environment..."
echo "#######"
.venv/bin/pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "#######"
    echo "Python packages installed successfully in virtual environment."
else
    echo "Failed to install Python packages in virtual environment."
    echo "Aborting the installation."
    exit 1
fi

if [ "$GUNICORN" = "y" ]; then
    echo "#######"
    echo "Installing gunicorn in virtual environment..."
    echo "#######"
    .venv/bin/pip install gunicorn
    if [ $? -eq 0 ]; then
        echo "#######"
        echo "Gunicorn installed successfully in virtual environment."
    else
        echo "Failed to install gunicorn in virtual environment."
        GUNICORN="failed"
    fi
fi

if [ "$P3DEV" = "y" ]; then
    echo "#######"
    echo "Installing Python3-dev..."
    echo "#######"
    apt install -y python3-dev
    if [ $? -eq 0 ]; then
        echo "#######"
        echo "Python3-dev installed successfully."
    else
        echo "Failed to install Python3-dev. Please check your internet connection or package sources."
        exit 1
    fi
fi

if [ "$HTML5LIB" = "y" ]; then
    echo "#######"
    echo "Installing html5lib in virtual environment..."
    echo "#######"
    .venv/bin/pip install html5lib
    if [ $? -eq 0 ]; then
        echo "#######"
        echo "html5lib installed successfully in virtual environment."
    else
        echo "Failed to install html5lib in virtual environment."
        HTML5LIB="failed"
    fi
fi

if [ "$BROWSER" = "chromium" ]; then
    echo "#######"
    echo "Installing Chromium and chromedriver..."
    echo "#######"
    apt install -y chromium-browser chromium-chromedriver
    if [ $? -eq 0 ]; then
        echo "#######"
        echo "Chromium and chromedriver installed successfully."
    else
        echo "Failed to install Chromium and chromedriver. Please check your internet connection or package sources."
        BROWSER="failed"
    fi
elif [ "$BROWSER" = "firefox" ]; then
    echo "#######"
    echo "Installing Firefox and geckodriver..."
    echo "#######"

    # Installation de Firefox
    apt install -y firefox-esr
    if [ $? -ne 0 ]; then
        echo "Failed to install Firefox. Please check your internet connection or package sources."
        BROWSER="failed"
    else
        echo "Firefox installed successfully."

        # Installation manuelle de geckodriver
        echo "Installing geckodriver manually..."

        # Détection de l'architecture
        ARCH=$(uname -m)
        if [ "$ARCH" = "x86_64" ]; then
            GECKO_ARCH="linux64"
        elif [ "$ARCH" = "aarch64" ]; then
            GECKO_ARCH="linux-aarch64"
        else
            GECKO_ARCH="linux32"
        fi

        # Téléchargement de la dernière version
        GECKO_VERSION=$(curl -s https://api.github.com/repos/mozilla/geckodriver/releases/latest | grep -Po '"tag_name": "\K.*?(?=")')
        if [ -z "$GECKO_VERSION" ]; then
            echo "Failed to get geckodriver version. Using fallback version v0.34.0"
            GECKO_VERSION="v0.34.0"
        fi

        GECKO_URL="https://github.com/mozilla/geckodriver/releases/download/${GECKO_VERSION}/geckodriver-${GECKO_VERSION}-${GECKO_ARCH}.tar.gz"

        # Téléchargement et installation
        cd /tmp
        wget -O geckodriver.tar.gz "$GECKO_URL"
        if [ $? -eq 0 ]; then
            tar -xzf geckodriver.tar.gz
            chmod +x geckodriver
            mv geckodriver /usr/local/bin/
            rm -f geckodriver.tar.gz

            # Vérification de l'installation
            if [ -f /usr/local/bin/geckodriver ]; then
                echo "Geckodriver installed successfully in /usr/local/bin/"
                /usr/local/bin/geckodriver --version
            else
                echo "Failed to install geckodriver."
                BROWSER="failed"
            fi
        else
            echo "Failed to download geckodriver from GitHub."
            echo "You can install it manually later from: https://github.com/mozilla/geckodriver/releases"
            BROWSER="failed"
        fi
        cd - > /dev/null
    fi
elif [ "$BROWSER" = "none" ]; then
    echo "No browser selected for web scraping."
else
    echo "Invalid option for browser selection."
    echo "Falling back to no browser mode."
fi

if [ "$REMOVEDB" = "y" ]; then
    echo "#######"
    echo "Removing the test database..."
    echo "#######"
    if [ -f ./pricechecker.db ]; then
        rm -rf ./pricechecker.db
        if [ $? -eq 0 ]; then
            echo "Test database removed successfully."
        else
            echo "Failed to remove the test database. Please check your permissions."
        fi
    else
        echo "No test database found, skipping removal."
    fi
fi

if [ "$SYSSERVICE" = "y" ]; then
    echo "#######"
    echo "Setting up the pricechecker service..."
    echo "#######"
    if [ -f ./resources/pricechecker.service ]; then
        cp ./resources/pricechecker.service /etc/systemd/system/
        sed -i "s/User=votre-username/User=$(whoami)/" /etc/systemd/system/pricechecker.service
        sed -i "s|WorkingDirectory=/home/votre-username/projets/PriceChecker|WorkingDirectory=$(pwd)|" /etc/systemd/system/pricechecker.service
        sed -i "s|Environment=PATH=/home/votre-username/projets/PriceChecker/.venv/bin|Environment=PATH=$(pwd)/.venv/bin|" /etc/systemd/system/pricechecker.service
        sed -i "s|ExecStart=/home/votre-username/projets/PriceChecker/.venv/bin/python run.py|ExecStart=$(pwd)/.venv/bin/python run.py|" /etc/systemd/system/pricechecker.service
    else
        echo "pricechecker.service file not found in resources directory."
        echo "Skipping service setup."
    fi
    systemctl enable pricechecker.service
    if [ $? -eq 0 ]; then
        echo "Pricechecker service set up successfully."
    else
        echo "Failed to set up the pricechecker service."
    fi
fi

echo "#######"
echo "Configuring pricechecker..."
echo "#######"
echo "Generating a random secret key for the configuration file..."
SECRET_KEY=$(openssl rand -base64 32)
if [ $? -eq 0 ]; then
    sed -i "s|^SECRET_KEY=.*|SECRET_KEY=$SECRET_KEY|" ./.env
    if [ $? -eq 0 ]; then
        echo "Configuration file updated with a random secret key."
    else
        echo "Failed to update the configuration file. Please check your permissions."
    fi
else
    echo "Failed to generate a random secret key. Please check your OpenSSL installation."
fi

if [ "$HTML5LIB" = "y" ]; then
    echo "Configuring html5lib"
    sed -i "s/soup = BeautifulSoup(response\.content, 'html\.parser')/soup = BeautifulSoup(response.content, 'html5lib')/g" ./scraping/price_scraper.py
    if [ $? -eq 0 ]; then
        echo "html5lib configured successfully."
    else
        echo "Failed to configure html5lib in ./scraping/price_scraper.py."
    fi
fi

if [ "$BROWSER" != "none" ]; then
    if [ "$BROWSER" = "chromium" ]; then
        sed -i "s/USER_AGENT=PriceChecker\/2\.4\.2/USER_AGENT=Mozilla\/5.0 (X11; Linux x86_64) AppleWebKit\/537.36 (KHTML, like Gecko) Chrome\/121.0.0.0 Safari\/537.36/g" ./.env
        if [ $? -eq 0 ]; then
            echo "Chromium user agent configured."
        else
            echo "Failed to configure Chromium user agent."
        fi
    elif [ "$BROWSER" = "firefox" ]; then
        sed -i "s/USER_AGENT=PriceChecker\/2\.4\.2/USER_AGENT=Mozilla\/5.0 (X11; Linux x86_64; rv:122.0) Gecko\/20100101 Firefox\/122.0/g" ./.env
        if [ $? -eq 0 ]; then
            echo "Firefox user agent configured."
        else
            echo "Failed to configure Firefox user agent."
        fi
    else
        echo "No browser selected for web scraping, skipping user agent configuration."
    fi
fi
echo "You can customize the configuration file later at ./config.py and/or .env."

if [ "$GUNICORN" = "y" ]; then
    echo "#######"
    echo "Configuring Gunicorn as a production-class WSGI server..."
    echo "#######"
    cat > gunicorn.conf << EOF
# Gunicorn configuration for PriceChecker
bind = "0.0.0.0:5000"
workers = 4
worker_class = "sync"
timeout = 30
keepalive = 2
max_requests = 1000
max_requests_jitter = 100
preload_app = True
accesslog = "./logs/access.log"
errorlog = "./logs/error.log"
loglevel = "info"
EOF
    if [ $? -eq 0 ]; then
        echo "Gunicorn.conf configuration file created successfully."
        if [ -f /etc/systemd/system/pricechecker.service ]; then
            systemctl stop pricechecker.service
            sed -i "s|ExecStart=$(pwd)/.venv/bin/python run.py|ExecStart=$(pwd)/.venv/bin/gunicorn -c $(pwd)/gunicorn.conf run:app|" /etc/systemd/system/pricechecker.service
            if [ $? -eq 0 ]; then
                echo "Gunicorn configuration deployed in /etc/systemd/system/pricechecker.service."
            else
                echo "Failed to configure Gunicorn service in /etc/systemd/system/pricechecker.service."
                echo "Skipping Gunicorn configuration."
            fi
        fi
    else
        echo "Failed to create Gunicorn configuration file."
        echo "Skipping Gunicorn configuration."
    fi
fi

if [ "$CUSTOMIZECONFIG" = "y" ]; then
    echo "#######"
    echo "You are about to configure pricechecker by editing config.py. Do it at your own risk."
    echo "#######"
    nano ./config.py
fi

echo "#######"
echo "Creating log directory..."
echo "#######"
mkdir -p logs
if [ $? -eq 0 ]; then
    echo "Log directory created successfully."
else
    echo "Failed to create log directory. Please check your permissions."
fi

if [ "$STARTNOW" = "y" ]; then
    if [ "$SYSSERVICE" = "y" ]; then
        echo "#######"
        echo "Starting the pricechecker service..."
        echo "#######"
        systemctl stop pricechecker.service
        systemctl daemon-reload
        systemctl start pricechecker.service
        if [ $? -eq 0 ]; then
            echo "#######"
            echo "Pricechecker service started successfully."
        else
            echo "Failed to start the pricechecker service."
        fi
    else
        echo "#######"
        echo "Starting PriceChecker manually..."
        echo "#######"
        .venv/bin/python ./run.py &
        if [ $? -eq 0 ]; then
            echo "PriceChecker started successfully."
        else
            echo "Failed to start PriceChecker manually."
        fi
    fi
fi

echo "#######"
echo "PriceChecker installation completed successfully."
echo "You can now access PriceChecker at http://localhost:5000."
echo "If you have set up a domain, you can access it at http://yourdomain.com:5000."
echo ""
echo "To start PriceChecker manually in the future, use:"
echo "source .venv/bin/activate && python run.py"
echo ""
echo "If you want to change this, consider changing the application's configuration files (config.py, .env)"
echo "and the service file (/etc/systemd/system/pricechecker.service)."
echo "DO IT AT YOUR OWN RISK."
echo "#######"
echo "Thank you for using PriceChecker!"
echo "#######"
echo "If you encounter any issues, please refer to the documentation or open an issue on GitHub."
echo "Github repository: https://github.com/edouardsaucisse/pricechecker"
echo "#######"
echo "Local troubleshooting :"
echo "## 1. Check python3 environment:"
echo "source .venv/bin/activate"
echo "which python"
echo "python --version"
echo "pip list"
echo "## 2. Check if the port 5000 is in use:"
echo "sudo netstat -tulpn | grep 5000"
echo "or"
echo "sudo lsof -i :5000"
echo "or"
echo "sudo ss -tulpn | grep 5000"
echo "## 3. check disk space:"
echo "df -h"
echo "## 4. Check if the pricechecker service is running:"
echo "sudo systemctl status pricechecker.service"
echo "## 5. Check if the pricechecker service is enabled to start on boot:"
echo "sudo systemctl is-enabled pricechecker.service"
echo "check system logs:"
echo "sudo journalctl -u pricechecker -f"
echo "#######"
echo "Exiting the installation script."
exit 0