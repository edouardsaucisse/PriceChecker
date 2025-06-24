#!/bin/sh
# This script installs the necessary dependencies for the project on a Debian-based system.
echo "This script needs to be run with root privileges, please use sudo."
if [ "$(id -u)" -ne 0 ]; then
    echo "You are not running this script as root. Please use sudo."
    exit 1
fi
echo "This script will install the necessary dependencies, configure and deploy pricechecker."
echo "This script will update the system and install mandatory packages :"
echo "* System : curl, wget, git, and build-essential."
echo "* Python : Python3, python3-dev, pip, and the required python packages."
echo "* RECOMMENDED : gunicorn (production grade webserver, replacing flask embedded WSGI server)."
echo "* Optional : Python3-dev, ."
echo "This script will install optional packages :"
echo "* Optional : html5lib (enhanced HTML parsing)"
echo "* Optional : chromium-browser and chromium-chromedriver (for web scraping with Selenium)"
echo "* Optional : firefox and geckodriver (for web scraping with Selenium)"
echo 'This script will pull the last version of the project from GitHub.'
echo "This script will also set up a systemd service for pricechecker."
echo "Press any key to continue or Ctrl+C to cancel."
read -n 1 -s -r
read -p "Do you want to check github to get the latest version (y to agree, any key to skip): " GITHUB
read -p "Do you want to install gunicorn? (y to agree, any key to skip): " GUNICORN
read -p "Do you want to install Python3-dev? (y to agree, any key to skip): " P3DEV
read -p "Do you want to install html5lib? (y to agree, any key to skip): " HTML5LIB
echo "You have to choose between chromium and firefox for web scraping. YOU CAN CHOOSE ONE BUT NOT BOTH."
read -p "Do you want to install Chromium and chromedriver? (y to agree, any key to skip): " BROWSER
echo "It is recommended to customize the configuration file located at ./config.py if the application is exposed on the internet."
read -p "Do you want to customize the configuration file now? You can do it later if you want (y to agree, any key to skip): " CUSTOMIZECONFIG
read -p "Do you want to start PriceChecker after the installation? (y to agree, any key to skip): " STARTNOW

if [ "BROWSER" = "y" ]; then
    BROWSER="chromium"
else
    read -p "Do you want to install firefox and geckodriver? (y to agree, any key to skip): " BROWSER
    if [ "$BROWSER" = "y" ]; then
        BROWSER="firefox"
    else
        BROWSER="none"
    fi
fi

read -p "Do you want to remove the test database? (y to agree, any key to skip): " REMOVEDB
read -p "Do you want to setup PriceChecker as a service? (y to agree, any key to skip): " SYSSERVICE

echo "#######"
echo "Updating the system..."
echo "#######"
apt update && apt upgrade -y

if $?; then
    echo "#######"
    echo "System updated successfully."
else
    echo "Failed to update the system. Please check your internet connection or package sources."
fi

echo "#######"
echo "Installing mandatory packages..."
echo "#######"
apt install -y curl wget git build-essential python3 python3-pip nano openssl

if $?; then
    echo "#######"
    echo "Mandatory packages installed successfully."
else
    echo "Failed to install mandatory packages. Please check your internet connection or package sources."
    echo "Aborting the installation."
    exit 1
fi

echo "#######"
echo "Installing pip packages..."
echo "#######"
pip3 install --upgrade pip

if $?; then
    echo "#######"
    echo "Python packages installed successfully."
else
    echo "Failed to upgrade pip. Please check your internet connection or package sources."
    echo "Aborting the installation."
    exit 1
fi

echo "#######"
echo "Installing Python packages..."
echo "#######"
pip3 install -r requirements.txt

if $?; then
    echo "#######"
    echo "Python packages installed successfully."
else
    echo "Failed to install Python packages. Please check your internet connection or package sources."
    echo "Aborting the installation."
    exit 1
fi

if [ "$GUNICORN" = "y" ]; then
    echo "#######"
    echo "Installing gunicorn..."
    echo "#######"
    pip3 install gunicorn
    if $?; then
        echo "#######"
        echo "Gunicorn installed successfully."
    else
        echo "Failed to install gunicorn. Please check your internet connection or package sources."
        GUNICORN = "failed"
    fi
fi

if [ "$P3DEV" = "y" ]; then
    echo "#######"
    echo "Installing Python3-dev..."
    echo "#######"
    apt install -y python3-dev
    if $?; then
        echo "#######"
        echo "Python3-dev installed successfully."
    else
        echo "Failed to install Python3-dev. Please check your internet connection or package sources."
        exit 1
    fi
fi

if [ "$HTML5LIB" = "y" ]; then
    echo "#######"
    echo "Installing html5lib..."
    echo "#######"
    pip3 install html5lib
    if $?; then
        echo "#######"
        echo "html5lib installed successfully."
    else
        echo "Failed to install html5lib. Please check your internet connection or package sources."
        HTML5LIB = "failed"
    fi
fi

if [ "$BROWSER" = "chromium" ]; then
    echo "#######"
    echo "Installing Chromium and chromedriver..."
    echo "#######"
    apt install -y chromium-browser chromium-chromedriver
    if $?; then
        echo "#######"
        echo "Chromium and chromedriver installed successfully."
    else
        echo "Failed to install Chromium and chromedriver. Please check your internet connection or package sources."
        BROWSER = "failed"
    fi
elif [ "$BROWSER" = "firefox" ]; then
    echo "#######"
    echo "Installing Firefox and geckodriver..."
    echo "#######"
    apt install -y firefox-esr geckodriver
    if $?; then
        echo "#######"
        echo "Firefox and geckodriver installed successfully."
    else
        echo "Failed to install Firefox and geckodriver. Please check your internet connection or package sources."
        BROWSER = "failed"
    fi
elif [ "$BROWSER" = "none" ]; then
    echo "No browser selected for web scraping."
else
    echo "Invalid option for browser selection."
    echo "Falling back to no browser mode."
fi

if [ "$GITHUB" = "y" ]; then
    if [ -d ./pricechecker ]; then
        echo "#######"
        echo "Checking for the latest version of PriceChecker..."
        echo "#######"
        cd pricechecker || exit
        git pull origin main
        if $?; then
            echo "PriceChecker updated successfully."
        else
            echo "Failed to update PriceChecker. Please check your internet connection or package sources."
        fi
    else
        echo "#######"
        echo "Cloning PriceChecker from GitHub..."
        echo "#######"
        git clone https://github.com/edouardsaucisse/pricechecker
        if $?; then
            echo "PriceChecker cloned successfully."
        else
            echo "Failed to clone PriceChecker. Please check your internet connection or package sources."
            echo "Aborting the installation."
            exit 1
        fi
    fi
fi

if [ "$REMOVEDB" = "y" ]; then
    echo "#######"
    echo "Removing the test database..."
    echo "#######"
    if [ -f ./pricechecker.db ]; then
      rm -rf ./pricechecker.db
      if $?; then
          echo "Test database removed successfully."
      else
          echo "Failed to remove the test database. Please check your permissions."
      fi
    fi
    echo "No test database found, skipping removal."
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
    if $?; then
        echo "Pricechecker service set up successfully."
    else
        echo "Failed to set up the pricechecker service."
    fi
fi

if [ "$CUSTOMIZECONFIG" = "y" ]; then
    echo "#######"
    echo "You are about to configure pricechecker by editing config.py. Do it at your own risk."
    echo "#######"
    nano ./config.py
else
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
        if $?; then
            echo "html5lib configured successfully."
        else
            echo "Failed to configure html5lib in ./scraping/price_scraper.py."
        fi
    fi

    if [ "$BROWSER" != "none" ]; then
        if [ "$BROWSER" != "chromium" ]; then
            sed "s/USER_AGENT=PriceChecker\/2\.4\.2/USER_AGENT=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36
/g" ./.env
            if [ $? -eq 0 ]; then
                echo "Chromium user agent configured."
            else
                echo "Failed to configure Chromium user agent."
            fi
        elif [ "$BROWSER" = "firefox" ]; then
            sed "s/USER_AGENT=PriceChecker\/2\.4\.2/USER_AGENT=Mozilla/5.0 (X11; Linux x86_64; rv:122.0) Gecko/20100101 Firefox/122.0
/g" ./.env
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
        if $?; then
            echo "Gunicorn.conf configuration file created successfully."
            if [ -f /etc/systemd/system/pricechecker.service ]; then
                sed -i "s|ExecStart=$(pwd)/.venv/bin/python run.py|ExecStart=$(pwd)/.venv/bin/gunicorn -c $(pwd)/gunicorn.conf. run:app|" /etc/systemd/system/pricechecker.service
                if $?; then
                    echo "Gunicorn configuration file created successfully."
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
fi

echo "#######"
echo "Creating log directory..."
echo "#######"
mkdir -p logs
if $?; then
    echo "Log directory created successfully."
else
    echo "Failed to create log directory. Please check your permissions."
fi

if [ "$STARTNOW" = "y" ]; then
    if [ "$SYSSERVICE" = "y" ]; then
        echo "#######"
        echo "Starting the pricechecker service..."
        echo "#######"
        systemctl start pricechecker.service
        if $?; then
            echo "#######"
            echo "Pricechecker service started successfully."
        else
            echo "Failed to start the pricechecker service. Please check your internet connection or package sources."
        fi
    fi

else
    python3 ./run.py &
fi

echo "#######"
echo "PriceChecker installation completed successfully."
echo "You can now access PriceChecker at http://localhost:5000."
echo "If you have set up a domain, you can access it at http://yourdomain.com:5000."
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
sudo "journalctl -u pricechecker -f"
echo "#######"
echo "Exiting the installation script."
exit 0