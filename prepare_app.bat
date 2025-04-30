@echo off
echo Preparing JARVIS App for build...

echo Installing Python dependencies...
pip install -r requirements.txt

echo Setting up Electron environment...
cd electron
npm install

echo Setup complete!
echo To start the application in development mode, run: npm run start-all
echo To build the application, run: npm run build
pause